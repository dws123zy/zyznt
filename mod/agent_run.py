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

from requests import session

# 本地模块
from db import mv, my, zyredis
from data.data import get_zydict, apikeyac, get_agent, get_rag
from mod.file import zyembd
from mod.llm import openai_llm, openai_llm_stream


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
            agent = get_agent(q_data.get('agentid', '')).get('data', {})
            if agent:
                ragtext = '空'
                q_text = q_data.get('msg', [])[-1].get('content', '')  # 拿到本次的问题
                # 处理rag知识搜索
                if agent.get('rag', ''):  # 有值说明有配置，要查rag
                    if q_data.get('msg', []):
                        if q_text in ['你好', '您好', '你叫什么名字', '你是谁', 'hi', 'hello']:
                            logger.warning(f'用户常规性问候，无需查询rag')
                            return ''
                        else:
                            ragtext = agent_rag_search({'text': q_text, 'rag': agent.get('rag', '')})
                # 网页搜索
                if agent.get('website', ''):
                    logger.warning(f'用户请求网页搜索')

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


'''动态加载文件读取模块'''

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

def agent_flow_start(data):
    try:
        alldata = {}  # 全局数据集合
        rdata = {}  # 要返回的数据
        # 获取智能体配置数据
        agent = get_agent(data.get('agentid')).get('data', {})
        # 判断第一次交互还是多轮
        if data.get('session'):
            print('多轮对话，从redis拿历史对话数据进行对话，找到执行的节点id,接着执行')
        else:
            print('第一次对话，先找开始节点，拿到配置数据')
            next = 'start_mod'  # 要执行的节点id
            agent_data = agent.get('flow_data', {})
            # 获取开始节点id
            for k in agent_data:
                if agent_data.get(k).get('module') in ['start_mod']:
                    next = k
                    break

            # 循环执行所有节点，只有当next值为空时才退出循环
            while next:
                flow_data = agent_data.get(next, {})  # 节点数据
                mod_name = flow_data.get('module')  # 节点模块名
                if  flow_data:
                    # 执行节点
                    if mod_name in ['start_mod']:  # 开始节点，走的流程不一样
                        start_data = modlist[mod_name](data, flow_data)
                        if start_data.get('code') in ['200', 200]:
                            # 初始化数据到全局数据集合alldata中
                            alldata = start_data.get('data', {})
                            next = flow_data.get('next', '')  # 获取下一个节点id
                            continue
                        else:  # 节点执行失败
                            next = ''  # 不再执行节点
                            return start_data
                    else:  # 非开始节点执行
                        # 组合本次节点的入参数据
                        indata = modlist['param_data'](alldata, flow_data)
                        # 执行节点
                        datac = modlist[mod_name](indata, flow_data)
                        if datac.get('code') in ['200', 200]:
                            print(f'节点执行成功，节点id={next},节点数据={datac}')
                            alldata[next] = datac.get('data', {})
                            next = flow_data.get('next', '')
                        else:
                            print(f'节点执行失败，节点id={next},节点数据={datac}')
                            return datac
        # 所有节点执行完毕，处理对话存储和返回结果
        pass
        # 返回结果数据
        return rdata
    except Exception as e:
        logger.error(f"智能体流运行开始错误: {e}")
        logger.error(traceback.format_exc())
        return ''



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




