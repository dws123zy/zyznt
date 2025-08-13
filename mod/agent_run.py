# _*_coding:utf-8 _*_
import json
import traceback
import logging
from concurrent.futures import ThreadPoolExecutor  # 线程池
from fastapi import Request
import asyncio
import importlib
import time
import copy
from threading import Timer
import base64
from datetime import datetime

from requests import session

# 本地模块
from db import mv, my, zyredis, sa
from data.data import get_zydict, apikeyac, get_agent, get_rag
from mod.file import zyembd
from mod.llm import openai_llm, openai_llm_stream, openai_llm_json


'''agent智能体运行模块'''


'''日志'''

logger = logging.getLogger(__name__)


'''初始化线程池'''

agent_pool = ThreadPoolExecutor(max_workers=9)


'''智能体rag知识库搜索'''


def agent_rag_search(data):
    try:
        # 获取检索条件
        # filterdata = data.get('filter', {})
        raglist = data.get('rag').split('/')
        rag_text = []
        for ragid in raglist:
            try:
                # 获取rag配置数据
                ragdata = get_rag(ragid)
                search_fun = ragdata.get('search', {}).get('search_fun', 'vector')
                # 获取embedding数据
                embdid = ragdata.get('embedding').split('/')[1] if ragdata.get('embedding') else 'bge-large-zh-v1.5'
                embddata = get_zydict('embd', embdid)
                datac = []
                logger.warning(f'获取到的数据:search_fun={search_fun}, embddata={embddata}')
                if search_fun in ['vector', 'sparse']:  # 单向量搜索
                    if search_fun in ['vector']:  # 密集向量搜索
                        logger.warning(f'向量搜索开始')
                        # 把text转为向量后传入搜索函数
                        textv = zyembd(data.get('text', ''), embddata)
                        datac = mv.vector_search(ragdata.get('ragid', ''), [textv], 'vector',
                                                 limit=data.get('limit', 10), radius=data.get('score', 0.1))
                    else:  # 稀疏向量搜索
                        logger.warning(f'稀疏向量搜索开始')
                        datac = mv.vector_search(ragdata.get('ragid', ''), [data.get('text', '')], 'sparse',
                                                 limit=data.get('limit', 10),  radius=data.get('score', 0.1))
                elif search_fun in ['vs']:  # 混合搜索
                    logger.warning(f'混合搜索开始')
                    # 把text转为向量后传入搜索函数
                    textv = zyembd(data.get('text', ''), embddata)
                    # 组合重排序
                    rerank = 'RRFRanker'
                    rrv = '60'
                    search_data = ragdata.get('search', {})
                    if 'wr' in search_data:
                        rrv = search_data.get('wr', '0.8/0.5')
                        rerank = 'WeightedRanker'
                    elif 'rr' in search_data:
                        rrv = search_data.get('rr', '60')
                        rerank = 'RRFRanker'
                    # 执行混合搜索
                    datac = mv.hybrid_search(ragdata.get('ragid', ''), [textv], [data.get('text', '')],
                                         limit=data.get('limit', 5), reranking=rerank, rrv=rrv)
                logger.warning(f'搜索结果={datac}')
                if datac:
                    rag_text.append(datac)  # 添加到列表中
            except Exception as e:
                logger.error(f" rag知识搜索错误: {e}")
                logger.error(traceback.format_exc())

        return '\n'.join('\n'.join(r) for r in rag_text)
    except Exception as e:
        logger.error(f"rag知识搜索错误: {e}")
        logger.error(traceback.format_exc())
        return ''


'''改写sql中的时间格式化示例llm用'''

sql_example1 = json.dumps(
    [{"text":"查询月度保单数据", "db_id": "db1001", "sql": "SELECT * FROM insurance WHERE time >= '2025-08-01 00:00:00' AND time < '2025-09-01 00:00:00';"}],
    ensure_ascii=False
)

sql_example2 = json.dumps(
    [{"text":"查询月度保单数据", "db_id": "db1001", "sql": "SELECT * FROM insurance WHERE time >= '2025-07-01 00:00:00' AND time < '2025-08-01 00:00:00';"},
     {"text":"查询月度保险代理人数据", "db_id": "db1001", "sql": "SELECT * FROM agent WHERE time >= '2025-07-01 00:00:00' AND time < '2025-08-01 00:00:00';"}],
    ensure_ascii=False
)

sql_example3 = json.dumps(
    [{"text":"查询代理人陈静月度的业绩和佣金", "db_id": "db1001", "sql": "SELECT agent_name AS `代理人姓名`,COUNT(DISTINCT policy_number) AS `保单数量`,SUM(total_premium) AS `总业绩`,SUM(commission_amount) AS `总佣金` FROM policy_commissions WHERE agent_name = '陈静' AND application_date BETWEEN '2025-07-01' AND '2025-07-31' GROUP BY agent_name;"}],
    ensure_ascii=False
)


sql_json_msg=[{
        "role": "system",
        "content": """根据用户的文本内容和现在的时间，计算出用户查询需要的具体时间或时间段，然后改写为SQL查询语句中的时间，然后按原格式并返回SQL查询数据。输出为JSON格式。
        示例：
        Q：文本内容是："帮我查询上个月的保单数据"， 现在的时间是："2025-08-03 09:01:00"，原始的SQL查询数据是：'''[{"text":"查询月度保单数据", "db_id": "db1001", "sql": "SELECT * FROM insurance WHERE time >= '2025-08-01 00:00:00' AND time < '2025-09-01 00:00:00';"}]'''
        A：%s

        Q：用户的文本内容是："帮我查询这个月的代理人的业绩数据"， 现在的时间是："2025-08-23 16:01:00"，原始的SQL查询数据是：[{"text":"查询月度保单数据", "db_id": "db1001", "sql": "SELECT * FROM insurance WHERE time >= '2025-01-01 00:00:00' AND time < '2025-02-01 00:00:00';"},
     {"text":"查询月度保险代理人数据", "db_id": "db1001", "sql": "SELECT * FROM agent WHERE time >= '2025-01-01 00:00:00' AND time < '2025-02-01 00:00:00';"}]
        A：%s
        
        Q：文本内容是："查询代理人陈静上个月的业绩和佣金"， 现在的时间是："2025-08-12 09:01:00"，原始的SQL查询数据是：'''[{"text":"查询代理人陈静月度的业绩和佣金", "db_id": "db1001", "sql": "SELECT agent_name AS `代理人姓名`,COUNT(DISTINCT policy_number) AS `保单数量`,SUM(total_premium) AS `总业绩`,SUM(commission_amount) AS `总佣金` FROM policy_commissions WHERE agent_name = '张三' AND application_date BETWEEN '2025-06-01' AND '2025-06-30' GROUP BY agent_name;"}]'''
        A：%s
        """ % (sql_example1, sql_example2, sql_example3)
    }]


'''格式化数据生成md格式'''


def smart_truncate(text, max_length=110):
    """智能截断文本，尽量在空格处分词"""
    try:
        if len(text) <= max_length:
            return text

        # 尝试在标点处截断（逗号、句号等）
        truncated = text[:max_length - 3]
        for punct in ['，', '。', ',', '.', '；', ';']:
            if punct in truncated:
                last_punct = truncated.rfind(punct)
                if last_punct > max_length // 2:  # 确保不会截得太短
                    return truncated[:last_punct + 1] + "..."
        return truncated + "..."
    except Exception as e:
        logger.error(f"数据格式化错误: {e}")
        logger.error(traceback.format_exc())
        return text


def generate_markdown_table(data, alignments=None, max_col_width=100):
    """
    生成优化的Markdown表格

    参数:
    data: 数据列表
    alignments: 每列对齐方式，如['left', 'center', 'left']
    max_col_width: 最大列宽
    """
    try:
        if not data:
            return ""

        headers = list(data[0].keys())
        num_columns = len(headers)
        alignments = alignments or ['left'] * num_columns

        # 计算每列最大显示宽度（考虑中文）
        col_widths = {}
        for i, header in enumerate(headers):
            # 中文每个字符宽度为2
            max_width = len(header) * 2 if any('\u4e00' <= char <= '\u9fff' for char in header) else len(header)

            for item in data:
                value = str(item.get(header, ""))
                display_value = smart_truncate(value, max_col_width)

                # 计算显示宽度（中文算2个字符）
                display_width = sum(2 if '\u4e00' <= char <= '\u9fff' else 1 for char in display_value)

                if display_width > max_width:
                    max_width = display_width

            # 确保最小宽度为4
            col_widths[header] = max(4, max_width)

        # 生成表头
        header_cells = []
        for i, header in enumerate(headers):
            # 中文每个字符宽度为2，需要特殊处理填充
            chinese_count = sum(1 for char in header if '\u4e00' <= char <= '\u9fff')
            non_chinese_count = len(header) - chinese_count
            total_width = chinese_count * 2 + non_chinese_count

            # 计算需要填充的空格数
            padding = col_widths[header] - total_width
            if padding > 0:
                padded_header = header + ' ' * padding
            else:
                padded_header = header

            header_cells.append(padded_header)

        header_row = "| " + " | ".join(header_cells) + " |"

        # 生成分隔行
        separator_cells = []
        for i, header in enumerate(headers):
            align = alignments[i]
            width = col_widths[header]

            if align == 'left':
                separator = ":" + "-" * (width - 1)
            elif align == 'center':
                separator = ":" + "-" * (width - 2) + ":"
            elif align == 'right':
                separator = "-" * (width - 1) + ":"
            else:
                separator = "-" * width

            separator_cells.append(separator)

        separator_row = "| " + " | ".join(separator_cells) + " |"

        # 生成数据行
        data_rows = []
        for item in data:
            row_cells = []
            for i, header in enumerate(headers):
                raw_value = str(item.get(header, ""))
                display_value = smart_truncate(raw_value, max_col_width)

                # 计算显示宽度（中文算2个字符）
                chinese_count = sum(1 for char in display_value if '\u4e00' <= char <= '\u9fff')
                non_chinese_count = len(display_value) - chinese_count
                total_width = chinese_count * 2 + non_chinese_count

                # 计算需要填充的空格数
                padding = col_widths[header] - total_width
                if padding > 0:
                    padded_value = display_value + ' ' * padding
                else:
                    padded_value = display_value

                row_cells.append(padded_value)

            data_rows.append("| " + " | ".join(row_cells) + " |")

        return "\n".join([header_row, separator_row] + data_rows)
    except Exception as e:
        logger.error(f"生成Markdown表格错误: {e}")
        logger.error(traceback.format_exc())
        return str(data)




def data2md_table(data2):
    try:
        # # 生成表头
        # header = "| " + " | ".join(data2[0].keys()) + " |\n"
        # separator = "| " + " | ".join(["---"] * len(data2[0])) + " |\n"
        #
        # # 生成数据行 - 修复点在这里
        # rows = ""
        # for item in data2:
        #     # 确保所有值转换为字符串
        #     rows += "| " + " | ".join(str(value) for value in item.values()) + " |\n"
        #
        # markdown_table = header + separator + rows
        return generate_markdown_table(data2)
    except Exception as e:
        logger.error(f"md数据格式化表格错误: {e}")
        logger.error(traceback.format_exc())
        return str(data2)





'''智能体数据Bi处理模块'''

def agent_bi(q_data, appid):
    """智能体数据Bi处理模块"""
    try:
        msg_bi = ''  # 最终要返回的内容
        bi_sql_json = []
        bi_data = q_data.get('bi_data', {})
        if not bi_data:
            return '', ''
        # 判断是否需要llm智能改写sql中的时间
        q_text = str(q_data.get('msg', [])[-1].get('content', ''))  # 获取用户输入的文本内容
        if bi_data.get('sql_time') in ['t'] and bi_data.get('sql'):
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # 调用格式化输出大模型根据用户的文件内容分析，并改写sql中的时间
            msg_text = f"""请根据提供的文本内容和现在的时间，分析出用户查询需要的具体时间、时间段、季度、人名、地区、区域、产品名等，然后改写SQL查询语句中对应的内容，
            然后按原格式并返回改写后SQL查询数据。输出为JSON格式。如果无需修改sql内容，直接返回原数据即可。文本内容是："{q_text}"，现在时间是："{nowtime}"，原始的SQL查询数据是：{bi_data.get('sql')}"""
            msg = sql_json_msg+[{"role": "user", "content": msg_text}]
            llm_data = get_zydict('llm',f'llm_json_{appid}')
            sql_data = openai_llm_json(msg, llm_data.get('apikey', ''), llm_data.get('url', ''), llm_data.get('module', ''))
            if sql_data:
                logger.warning(f'llm智能改写sql={type(sql_data)}结果={sql_data}')
                bi_data['sql'] = sql_data
            else:
                logger.warning(f'llm智能改写sql错误')

        # 判断是否需要执行sql并把结果加入msg中
        if bi_data.get('sql_execute') in ['t'] and bi_data.get('sql'):
            msg_bi = f'根据用户的提问“{q_text}”，执行了用户配置的sql查询语句，执行后的结果如下：\n'
            # 遍历sql配置数据执行sql命令
            for s in bi_data.get('sql', []):
                # 获取db_id，然后拿到db的连接配置数据
                logger.warning(f'bi_sql={s}')
                db_data = get_zydict('db', s.get('db_id', ''))
                logger.warning(f'db_data={db_data}')
                if db_data:
                    # 执行sql查询数据
                    db_result = sa.sa_sql_query(db_data.get('db_url', ''), s.get('sql', ''), timeout=db_data.get('timeout', 120))
                    logger.warning(f'bi_sql查询结果={db_result}')
                    if db_result.get('code') in [200]:
                        msg_bi = msg_bi+f'查询主题：{s.get("text", "")}，\nsql: {s.get('sql', '')}，\n执行后的结果: {db_result.get('data', '')}\n'
                        s['data'] = db_result.get('data', '')
                    else:
                        msg_bi = msg_bi+f'查询主题：{s.get("text", "")}，\nsql: {s.get("sql", "")}，执行后的结果: {db_result.get('msg', '')}\n'
                        s['data'] = db_result.get('msg', '')
                    # 把执行后的格式化结果加到json_msg中
                    bi_sql_json += [s]


        # 判断是否需要把数据可视化图表要求加到msg中
        if bi_data.get('chart') and bi_data.get('sql'):
             pass

        # 判断是否需要表配置中的内容加到msg中
        if bi_data.get('table'):
             pass

        logger.warning(f'智能体数据Bi处理结果={msg_bi}')
        # 返回结果
        return {"role": "system", "content": msg_bi}, bi_sql_json
    except Exception as e:
        logger.error(f"智能体数据Bi处理错误: {e}")
        logger.error(traceback.format_exc())
        return '', ''



'''work agent工作数据组合函数'''

async def agent_work(q_data):
    try:
        '''判断session id是否已存在，如果有就是老对话，无就是新对话'''
        session_type = 'new'  # 默认新对话
        session_data = {}
        session_id = q_data.get('session', '')
        if session_id:
            # 先查redis中的session数据
            r_data = zyredis.rjget(['agent_record', '.' + session_id])
            if r_data:
                session_data = r_data
                session_type = 'redis'  # redis中有的数据，说明是老对话，也在redis中，近期的
            else:  # 从mysql中取值
                sqlcmd = my.sqlc3({'session': session_id}, 'agent_record', '1', '1', '')
                session_data_my = my.msqlc(sqlcmd)
                if session_data_my:
                    session_data = session_data_my[0]
                    session_data['data'] = json.load(session_data['data'])  # my数据库中的data要转为字典
                    session_type = 'old'  # redis中无，my中有，说明数据很久了


        '''当为新对话或很久的老对话时，生成智能体初始化数据'''
        if session_type in ['new' , 'old']:
            logger.warning(f'{session_type}此为新对话或mysql中的老对话，生成智能体初始化数据={session_id}')
            '''使用agentid拿到智能体配置数据'''
            agent_data = get_agent(q_data.get('agentid', {}))
            agent = agent_data.get('data', {})
            if agent:
                ragtext = ''
                q_text = str(q_data.get('msg', [])[-1].get('content', ''))  # 拿到本次的问题
                # 处理rag知识搜索
                if agent.get('rag', ''):  # 有值说明有配置，要查rag
                    if q_data.get('msg', []):
                        if q_text in ['你好', '您好', '你叫什么名字', '你是谁', 'hi', 'hello']:
                            logger.warning(f'用户常规性问候，无需查询rag')
                            # return ''
                        else:
                            ragtext = agent_rag_search({'text': q_text, 'rag': agent.get('rag', '')})
                # 网页搜索
                if agent.get('website', ''):
                    logger.warning(f'用户请求网页搜索')
                # agent中配置的文件知识
                filetext = ''
                if agent.get('file', ''):
                    logger.warning(f'用户请求文件知识')
                    for f in agent.get('file', '').split('/'):
                        try:
                            db_text = my.sqlc3({'fileid': f}, 'file', '1', '1', '')
                            if db_text and db_text[0].get('text', ''):
                                filetext += str(db_text[0].get('text', ''))
                        except Exception as e2:
                            logger.error(f"文件知识搜索错误: {e2}")
                            logger.error(traceback.format_exc())

                # bi数据处理
                bi_data, bi_sql_json = agent_bi(q_data,agent_data.get('appid', ''))

                # db_id 数据源配置数据处理，获取数据链接配置，然后连接数据源，拿到对应的数据库结构
                db_system = ''
                if q_data.get('db_id'):
                    db_data = get_zydict('db', q_data.get('db_id', ''))
                    if db_data:
                        db_schema = sa.export_db_schema(db_data.get('db_url', ''))
                        if type(db_schema) in [str]:
                            logger.warning(f'数据库结构获取失败={db_schema}')
                        else:
                            logger.warning(f'数据库结构获取成功')
                            # 从结果中获取数据库结构的ddl
                            for d in db_schema['tables']:
                                if db_schema['tables'].get(d, {}).get('ddl'):
                                    db_system = db_system+str(db_schema['tables'][d].get('ddl', ''))+'\n\n'

                # 获取大模型LLM配置数据
                llmdata = get_zydict('llm', agent.get('llm', ''))

                # 组合msg
                msg = []
                '''增加系统参数到msg中'''
                if agent.get('prompt'):  # 增加系统提示词到msg中
                    msg.append({'role': 'system', 'content': agent.get('prompt', '')})
                if agent.get('context'):  # 增加上下文到msg中
                    msg.append({'role': 'system', 'content': agent.get('context', '')})
                if filetext:  # 增加文件内容到msg中
                    msg.append({'role': 'system', 'content': f'文件内容：{filetext}'})
                if bi_data:  # 添加bi数据到msg中
                    msg.append(bi_data)
                if db_system:  # 添加数据库结构到msg中
                    msg.append({'role': 'system', 'content': f'数据库结构：{db_system}'})

                '''把初始化agent数据存到redis，便于后面对话使用'''
                r_msg = copy.deepcopy(msg)
                r_agen_data = {
                    'msg': r_msg,
                    'apikey': llmdata.get('apikey', ''),
                    'sdk': llmdata.get('sdk', 'openai'),
                    'url': llmdata.get('url', ''),
                    'mod': llmdata.get('module', ''),
                    'tools': agent.get('tools', ''),
                    'temperature': agent.get('temperature', 0.9),
                    'stream': agent.get('stream', True)
                }
                nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                # 老数据时，要拿到历史的data数据，一起存到redis中
                data_msg = []
                if session_type in ['old']:
                    data_msg = session_data.get('data', [])  # 获取历史数据
                    # 从历史数据中取出msg然后加到当前的msg中
                    for m in data_msg:
                        if m.get('msg'):
                            msg.extend(m.get('msg', []))
                # 组合要存入redis的数据
                r_session_data = {"appid": agent_data.get('appid', ''), "agentid": q_data.get('agentid', ''),
                                  "session": session_id, "name": agent.get('name', ''), "user": q_data.get('user', ''),
                                  "start_time":  nowtime, "last_time": nowtime, "tokens": 0, "type": "agent",
                                  "data": data_msg, "agent_data": r_agen_data, "fileid": q_data.get('fileid', []),
                                  "title": q_text[:60]}
                if not session_data:
                    session_data = r_session_data  # 当前对话数据为空时，直接使用新的r_session_data
                rjg = zyredis.rjset(['agent_record', '.' + session_id, r_session_data])

                '''当为新对话时，存到mysql中'''
                if session_type in ['new']:
                    my_session_data = copy.deepcopy(r_session_data)
                    del my_session_data['agent_data']  # mysql中不存agent_data
                    del my_session_data['fileid']  # mysql中不存fileid
                    my_session_data['data'] = my.list_to_safe_base64(my_session_data['data'])
                    my_session_data['title'] = my.list_to_safe_base64(my_session_data['title'])
                    logger.warning("当为新对话时，存到mysql中")
                    sqlcmd= my.sql3sz(my_session_data, 'agent_record')
                    logger.warning(f"sqlcmd={sqlcmd}")
                    mjg = my.msqlzsg(sqlcmd)

                '''组合本次请求中的file文件'''
                q_file_text = ''
                if q_data.get('fileid', []):
                    logger.warning(f'处理本次用户请求文件内容')
                    for qf in q_data.get('fileid', []):
                        try:
                            q_db_text = my.sqlc3({'fileid': qf}, 'file', '1', '1', '')
                            if q_db_text and q_db_text[0].get('text', ''):
                                f_text = f"文件名：{q_db_text[0].get('name', '')}，文件内容：{str(q_db_text[0].get('text', ''))}。  "
                                q_file_text += f_text
                        except Exception as e3:
                            logger.error(f"文件知识搜索错误: {e3}")
                            logger.error(traceback.format_exc())

                '''增加本次消息内容到msg中'''
                this_msg = []
                if q_file_text:  # 增加本次文件内容到msg中
                    f_msg = {'role': 'system', 'content': f'{q_file_text}'}
                    msg.append(f_msg)  # 添加文件内容到主msg中
                    this_msg.append(f_msg)  # 添加文件内容到本次msg中
                if agent.get('prologue') and session_type in ['new']:  # 增加开场白到msg中
                    p_msg = {'role': 'assistant', 'content': agent.get('prologue', '')}
                    msg.append(p_msg)  # 添加开场白到主msg中
                    this_msg.append(p_msg)  # 添加开场白到本次msg中
                # 增加本次bi数据处理结果到this_msg中
                if bi_data:  # 添加bi数据到this_msg中
                    this_msg.append(bi_data)

                #  增加本次问题到msg中
                q_msg = q_data.get('msg', [])[-1]
                logger.warning(f'q_msg={q_msg}')
                msg.append(q_msg)  # 增加本次问题列表到msg中
                this_msg.append(q_msg)  # 添加本次问题列表到本次msg中

                if ragtext:  # 增加本次问题rag搜索结果到msg中
                    rag_msg = {'role': 'system', 'content': f'根据用户问题{q_text}，查到的外部知识为：{ragtext}'}
                    msg.append(rag_msg)  # 添加 rag搜索结果到主msg中
                    this_msg.append(rag_msg)  # 添加 rag搜索结果到本次msg中

                '''
                # 数据组合
                msg, apikey, url, mod, tools = None, temperature = 0.9, stream = True
                '''
                rdata = {
                    'msg': msg,
                    'apikey': llmdata.get('apikey', ''),
                    'sdk': llmdata.get('sdk', 'openai'),
                    'url': llmdata.get('url', ''),
                    'mod': llmdata.get('module', ''),
                    'tools': agent.get('tools', ''),
                    'temperature': agent.get('temperature', 0.9),
                    'stream': agent.get('stream', True),
                    'this_msg': this_msg,
                    'session_data': session_data,
                    'bi_data': bi_data,
                    'bi_sql_json': bi_sql_json,
                }
                # 返回数据
                return rdata
            else:
                logger.warning(f'未找到智能体配置')
                return {}
        else:
            logger.warning(f'此为redis缓存对话，使用redis数据库中的数据={session_id}')
            # 判断agentid 与 历史中的agentid是否一致，不一致返回错误
            if session_data.get('agentid', '') != q_data.get('agentid', ''):
                logger.warning(f"agentid与历史使用不一致，请检查agentid：{session_data.get("agentid", '')} != {q_data.get("agentid", '')}")
                return {}
            '''使用agentid拿到智能体配置数据'''
            agent_data = get_agent(q_data.get('agentid', {}))
            agent = agent_data.get('data', {})
            # agent = get_agent(q_data.get('agentid', '')).get('data', {})
            if agent:
                ragtext = '空'
                q_text = q_data.get('msg', [])[-1].get('content', '')  # 拿到本次的问题
                # 处理rag知识搜索
                if agent.get('rag', ''):  # 有值说明有配置，要查rag
                    if q_data.get('msg', []):
                        if q_text in ['你好', '您好', '你叫什么名字', '你是谁', 'hi', 'hello']:
                            logger.warning(f'用户常规性问候，无需查询rag')
                            # return ''
                        else:
                            ragtext = agent_rag_search({'text': q_text, 'rag': agent.get('rag', '')})
                # 网页搜索
                if agent.get('website', ''):
                    logger.warning(f'用户请求网页搜索')

                # bi数据处理
                bi_data, bi_sql_json = agent_bi(q_data,agent_data.get('appid', ''))

                # 获取大模型LLM配置数据
                llmdata = get_zydict('llm', agent.get('llm', ''))

                # 组合msg
                msg = []
                # 老数据时，要拿到历史的data数据，一起存到redis中
                data_msg = session_data.get('data', [])  # 获取历史数据
                if data_msg:
                    # 从历史数据中取出msg然后加到当前的msg中
                    for m in data_msg:
                        if m.get('msg'):
                            msg.extend(m.get('msg', []))

                '''组合本次请求中的file文件'''
                q_file_text = ''
                if q_data.get('fileid', []):
                    logger.warning(f'处理本次用户请求文件内容')
                    filelist = session_data.get('fileid', [])  # 已处理过的fileid
                    for qf in q_data.get('fileid', []):
                        if qf not in filelist:
                            try:
                                q_db_text = my.sqlc3({'fileid': qf}, 'file', '1', '1', '')
                                if q_db_text and q_db_text[0].get('text', ''):
                                    f_text = f"文件名：{q_db_text[0].get('name', '')}，文件内容：{str(q_db_text[0].get('text', ''))}。  "
                                    q_file_text += f_text
                                    session_data['fileid'] = session_data['fileid']+[qf]  # 增加本次文件id到已处理过的fileid中
                            except Exception as e3:
                                logger.error(f"文件知识搜索错误: {e3}")
                                logger.error(traceback.format_exc())

                '''增加本次消息内容到msg中'''
                this_msg = []
                if q_file_text:  # 增加本次文件内容到msg中
                    f_msg = {'role': 'system', 'content': f'{q_file_text}'}
                    msg.append(f_msg)  # 添加文件内容到主msg中
                    this_msg.append(f_msg)  # 添加文件内容到本次msg中
                if agent.get('prologue') and session_type in ['new']:  # 增加开场白到msg中
                    p_msg = {'role': 'assistant', 'content': agent.get('prologue', '')}
                    msg.append(p_msg)  # 添加开场白到主msg中
                    this_msg.append(p_msg)  # 添加开场白到本次msg中
                # 增加bi数据到msg中
                if bi_data:
                    msg.append(bi_data)
                    this_msg.append(bi_data)

                # msg.extend(q_data.get('msg', []))  # 增加本次问题列表到msg中
                #  增加本次问题到msg中
                q_msg = q_data.get('msg', [])[-1]  # 取前端推过来的最后一条
                logger.warning(f'q_msg={q_msg}')
                msg.append(q_msg)  # 增加本次问题列表到msg中
                this_msg.append(q_msg)  # 添加本次问题列表到本次msg中

                if ragtext:  # 增加本次问题rag搜索结果到msg中
                    rag_msg = {'role': 'system', 'content': f'根据用户问题{q_text}，查到的外部知识为：{ragtext}'}
                    msg.append(rag_msg)  # 添加 rag搜索结果到主msg中
                    this_msg.append(rag_msg)  # 添加 rag搜索结果到本次msg中

                '''
                # 数据组合
                msg, apikey, url, mod, tools = None, temperature = 0.9, stream = True
                '''
                rdata = session_data.get('agent_data', {})  # 增加当前智能体的初始化数据
                rdata['this_msg'] = this_msg  # 增加本轮msg
                rdata['msg'] = rdata['msg'] + msg
                rdata['session_data'] = session_data
                rdata['bi_data'] = bi_data
                rdata['bi_sql_json'] = bi_sql_json
                # 返回数据
                return rdata
            else:
                logger.warning(f'未找到智能体配置')
                return {}
    except Exception as e:
        logger.error(f'agent_work工作处理函数错误: {e}')
        logger.error(traceback.format_exc())
        return ''



'''agent流式回复处理模块'''

async def agent_stream(request: Request, data):
    try:
        logger.warning(f'data={data}')
        # 验证请求合法性
        # appid = get_agent(data.get('agentid', {})).get('appid', '')
        # if not apikeyac(data.get('apikey', ''), appid):
        #     logger.warning(f'agent请求验证失败')
        #     yield f"agent验证失败\n\n"
        #     return
        '''调用函数处理agent配置work，返回以下参数用于调用大模型
        msg, apikey, url, mod, tools=None, temperature=0.9, stream=True  sdk
        '''
        workdata = await agent_work(data)  # agent工作数据组合
        if workdata:
            logger.warning(f'workdta={workdata}')

            # 初始化本轮对话数据
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            this_data = {'start_time': nowtime, 'end_time': '', 'msg': workdata.get('this_msg', []),
                         'custom_data': data.get('custom_data', {}), 'log': []}
            llm_msg = {'role': 'assistant', 'content': ''}

            # 判断bi_sql_json是否有数据，如果有，则先返回bi的原始数据，然后再调llm
            if workdata.get('bi_sql_json'):
                chunk0 = f'根据本次的提问，执行了已配置的sql查询语句，执行后的结果如下：<br/><br/>'
                yield chunk0
                llm_msg['content'] = llm_msg['content'] + str(f'{chunk0}')
                for j in workdata.get('bi_sql_json', []):
                    if j:  # 加粗字体 <b>知识内容：</b>
                        chunk1 = str(f"<b>查询主题：</b> {j.get("text", "")}，<br/><br/><b>sql:</b> '''{j.get("sql", "")}''' <br/><br/><b>执行后的结果:</b> <br/>")
                        yield chunk1
                        chunk2 = '\n\n'
                        yield chunk2
                        chunk3 = data2md_table(j.get('data'))
                        yield chunk3
                        chunk4 = '\n\n<br/><br/>\n\n'
                        yield chunk4
                        llm_msg['content'] = llm_msg['content'] + str(f'{chunk1}{chunk2}{chunk3}{chunk4}')
                        # bi_chunk = str(workdata.get('bi_data', {}).get('content', ''))
                        # # this_data['log'] = this_data['log'] + [bi_chunk]
                        # yield bi_chunk

            # 调用大模型
            llmsdk = workdata.get('sdk', '')
            if llmsdk in ['openai']:
                # 调用openai大模型
                logger.warning(f'使用openai-sdk调用大模型')
                async for chunk in openai_llm_stream(workdata.get('msg', []), workdata.get('apikey', ''), workdata.get('url', ''),
                                        workdata.get('mod', ''), workdata.get('tools', None),
                                        workdata.get('temperature', 0.7), workdata.get('stream', True)):
                    logger.warning(f'LLM流返回={chunk}')
                    if type(chunk) in [dict, 'dict'] and 'reasoning_content' not in chunk:  # 此为运行日志
                        this_data['log'] = this_data['log']+[chunk]
                    else:  # 此为文本消息回复
                        llm_msg['content'] = llm_msg['content'] + str(chunk)
                        yield f"{chunk}"

            elif llmsdk in  ['ollama']:
                # 调用llm大模型
                logger.warning(f'从ollama调用llm大模型')
            else:
                logger.warning(f'不支持的llm模型={llmsdk}')
                yield f"不支持的llm模型={llmsdk}"
            # 存结果
            logger.warning(f'LLM执行完成，现在把结果存到redis和mysql={llm_msg}')
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            this_data['end_time'] = end_time  # 增加结束时间
            this_data['msg'].append(llm_msg)  #  添加LLM结果到主msg中
            # 存结果到数据库中
            r_data = workdata.get('session_data', {}).get('data', [])+[this_data]
            session_id = data.get('session', 'a')
            if session_id:
                rjg = zyredis.rjset(['agent_record', f'.{session_id}.data', r_data])  # 存data到redis中
                last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                rjg = zyredis.rjset(['agent_record', f'.{session_id}.last_time', last_time])  # 更新last_time到redis中
                # 存到mysql中
                b64rdata = my.list_to_safe_base64(r_data)
                sqlcmd = my.sqlg({'data': b64rdata, 'last_time': last_time},  'agent_record', {'session': session_id})
                mjg = my.msqlzsg(sqlcmd)  # 存入mysql
        else:
            logger.warning(f'agent工作处理函数错误')
            yield f"agent工作中遇到了点麻烦，请稍后再试"

        # for i in range(10):
        #     if await request.is_disconnected():
        #         print("客户端断开连接")
        #         break
        #
        #     data = f"这是第 {i+1} 条消息"
        # yield f"data: {data}\n\n"
        #     await asyncio.sleep(1)
    except Exception as e:
        logger.error(f'agent_stream错误信息：{e}')
        logger.error(traceback.format_exc())
        yield f"智能体工作中遇到了点麻烦，请稍后再试"



'''智能体流运行'''

'''获取flow读取模块配置'''

flow_mod_data = get_zydict('flowmod', 'flowmod')


'''动态加载工作流组件模块'''

modlist = {}


for m in flow_mod_data:
    try:
        module = importlib.import_module(m.get('dir'))
        # 获取函数
        func = getattr(module, m.get('fun_name'))
        modlist[m.get('fun_name')] = func
        print('模块导入成功=', func)
    except ImportError as e:
        print(f"导入失败: {e}")

logger.warning(f'模块导入成功={modlist}')



'''flow 智能体流运行开始'''

async def agent_flow_start(data):
    alldata = {}  # 全局数据集合
    rdata = {'status': '', 'node_id': '', 'name': '', 'data': '', 'custom_data':data.get('custom_data')}  # 要返回的数据
    try:
        # 获取智能体配置数据
        agent = get_agent(data.get('agentid')).get('data', {})
        # 判断第一次交互还是多轮
        if data.get('session'):
            logger.warning('多轮对话，从redis拿历史对话数据进行对话，找到执行的节点id,接着执行')
        else:
            logger.warning('第一次对话，先找开始节点，拿到配置数据')
            next_node_id = 'start_mod'  # 要执行的节点id
            agent_data = agent.get('flow_data', {})
            # 获取开始节点id
            for k in agent_data:
                if agent_data.get(k).get('module') in ['start_mod']:
                    next_node_id = k
                    break

            # 循环执行所有节点，只有当next值为空时才退出循环
            while next_node_id:
                flow_data = agent_data.get(next_node_id, {})  # 节点数据
                mod_name = flow_data.get('module')  # 节点模块名
                if  flow_data:
                    # 执行节点
                    if mod_name in ['start_mod']:  # 开始节点，走的流程不一样
                        start_data = await modlist[mod_name](data, flow_data)
                        if start_data.get('code') in ['200', 200]:
                            # 初始化数据到全局数据集合alldata中
                            alldata = start_data.get('data', {})
                            next_node_id = flow_data.get('next', '')  # 获取下一个节点id
                            # continue
                        else:  # 节点执行失败
                            next_node_id = ''  # 不再执行节点
                            err_text = f"开始节点执行失败,{start_data.get('data')}"
                            alldata[next_node_id] = err_text
                            # 更新rdata数据并返回
                            rdata['status'] = 'error'
                            rdata['node_id'] = flow_data.get('node_id', '')
                            rdata['name'] = flow_data.get('name', '')
                            rdata['data'] = err_text
                            return rdata
                    elif mod_name in ['end_mod']:  # 结束节点，走的流程不一样
                        # 记录结束时间
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        alldata['system']['end_time'] = now
                        alldata[next_node_id] = 'end'
                        next_node_id = ''  # 不再执行节点
                    else:  # 非开始节点执行
                        # 组合本次节点的入参数据
                        indata = await modlist['param_data'](alldata, flow_data)
                        logger.warning(f'组合本次节点的入参数据indata={indata}')
                        if indata.get('code') in ['502', '501']:
                            err_text = f"数据组合param_data执行失败,{indata.get('data')}"
                            alldata['param_data'] = err_text
                            # 更新rdata数据并返回
                            rdata['status'] = 'error'
                            rdata['node_id'] = flow_data.get('node_id', '')
                            rdata['name'] = flow_data.get('name', '')
                            rdata['data'] = err_text
                            return rdata
                        # 执行节点
                        datac = await modlist[mod_name](indata, flow_data)
                        if datac.get('code') in ['200', 200]:
                            logger.warning(f'节点执行成功，节点id={next_node_id},节点执行结果={datac}')
                            alldata[next_node_id] = datac.get('data', {})
                            alldata[next_node_id]['status'] = 'success'
                            alldata[next_node_id]['node_id'] = next_node_id
                            alldata[next_node_id]['name'] = flow_data.get('name', '')
                            # 更新rdata数据并返回
                            rdata['status'] = 'success'
                            rdata['node_id'] = next_node_id
                            rdata['name'] = flow_data.get('name', '')
                            rdata['data'] = datac.get('data', {})
                            # 获取下一个节点id
                            next_node_id = flow_data.get('next', '')
                        else:
                            logger.warning(f'节点执行失败，现在终止执行，节点id={next_node_id},节点数据={datac}')
                            err_text = f"节点执行失败,{datac.get('data')}"
                            alldata[next_node_id] = {'status': 'error', 'node_id': flow_data.get('node_id', ''),
                                                     'name': flow_data.get('name', ''), 'data': err_text}
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            alldata['system']['end_time'] = now
                            # 更新rdata数据并返回
                            rdata['status'] = 'error'
                            rdata['node_id'] = flow_data.get('node_id', '')
                            rdata['name'] = flow_data.get('name', '')
                            rdata['data'] = err_text
                            return rdata
                else:
                    logger.warning(f'找不到节点id={next_node_id}')
                    err_text =f'找不到节点id={next_node_id}'
                    alldata[next_node_id] = {'status': 'error', 'node_id': flow_data.get('node_id', ''),
                                             'name': flow_data.get('name', ''), 'data': err_text}
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    alldata['system']['end_time'] = now
                    # 更新rdata数据并返回
                    rdata['status'] = 'error'
                    rdata['node_id'] = flow_data.get('node_id', '')
                    rdata['name'] = flow_data.get('name', '')
                    rdata['data'] = err_text
                    return rdata

        # 所有节点执行完毕，处理对话存储和返回结果
        agentdata = get_agent(data.get('agentid'))
        appid = agentdata.get('appid', '')
        session_id = alldata.get('system', {}).get('session', '')
        user = data.get('user', '')
        start_time = alldata.get('system', {}).get('start_time', '')
        end_time = alldata.get('system', {}).get('end_time', '')
        alldata_b64 = my.list_to_safe_base64(alldata)
        r_data = {'appid': appid, 'session': session_id, 'user': user, 'agentid': data.get('agentid', ''),
                  'type': 'flow', 'start_time': start_time, 'last_time': end_time, 'name': agentdata.get('name', ''),
                  'data': alldata_b64}
        # 存到mysql中
        sqlcmd = my.sql3sz(r_data, 'agent_record')
        logger.warning(f"智能体工作流记录入库sqlcmd={sqlcmd}")
        mjg = my.msqlzsg(sqlcmd)
        logger.warning(f"智能体工作流记录入库结果mjg={mjg}")
        # 返回结果数据
        return rdata
    except Exception as e:
        logger.error(f"智能体流运行开始错误: {e}")
        logger.error(traceback.format_exc())
        rdata['status'] = 'error'
        return rdata



'''agent对话记录定期删除'''


def agent_record_init():
    try:
        '''智能体对话记录'''

        agent_record_data = {"session": {"session": "session", "appid": "zy001", "user": "dws@zy", "agentid": "agent004",
                                    "type": "agent", "start_time": "", "end_time": "", "tokens": "", "data": []}}
        zyredis.rjset(['agent_record', '.', agent_record_data])
        logger.warning(f'初始化智能体对话记录成功')
    except  Exception as e:
        logger.error(f"初始化智能体对话记录错误: {e}")
        logger.error(traceback.format_exc())



'''定时程序'''

def reloadtime(inc):
    try:
        # 入库消息记录和套餐时长
        nowtime = time.strftime('%H:%M', time.localtime(time.time()))
        if nowtime in ['00:01']:
            agent_record_init()
            time.sleep(70)
        t = Timer(inc, reloadtime, (inc,))
        t.start()

    except Exception as e:
        logger.error("reload定时错误:")
        logger.error(e)
        logger.error(traceback.format_exc())


# 开启定时reload  初始化对话，验证码 1
# reloadtime(5)




