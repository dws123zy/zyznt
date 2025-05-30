# _*_coding:utf-8 _*_

import traceback
import logging
from concurrent.futures import ThreadPoolExecutor  # 线程池
from fastapi import Request
import asyncio
import importlib


# 本地模块
from db import mv, my
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




'''work agent工作处理函数'''

async def agent_work(q_data):
    try:
        '''使用agentid拿到智能体配置数据'''
        agent = get_agent(q_data.get('agentid', {})).get('data', {})
        if agent:
            ragtext = '空'
            q_text = q_data.get('msg', [])[-1].get('content', '')
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
            # 文件知识
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
            if agent.get('prompt'):  # 增加系统提示词到msg中
                msg.append({'role': 'system', 'content': agent.get('prompt', '')})
            if agent.get('context'):  # 增加上下文到msg中
                msg.append({'role': 'system', 'content': agent.get('context', '')})
            # 增加本次消息列表到msg中
            msg.extend(q_data.get('msg', []))
            if ragtext:  # 增加rag搜索结果到msg中
                msg.append({'role': 'system', 'content': f'根据用户问题{q_text}，查到的外部知识为：{ragtext}'})
            if ragtext:  # 增加文件内容到msg中
                msg.append({'role': 'system', 'content': f'文件内容：{filetext}'})
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
                'stream': agent.get('stream', True)
            }
            # 返回数据
            return rdata


        else:
            logger.warning(f'未找到智能体配置')
            return ''
    except Exception as e:
        logger.error(f'agent工作处理函数错误: {e}')
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
        workdata = await agent_work(data)
        if workdata:
            # 调用大模型
            llmsdk = workdata.get('sdk', '')
            if llmsdk in ['openai']:
                # 调用openai大模型
                logger.warning(f'使用openai-sdk调用大模型')
                async for chunk in openai_llm_stream(workdata.get('msg', []), workdata.get('apikey', ''), workdata.get('url', ''),
                                        workdata.get('mod', ''), workdata.get('tools', None),
                                        workdata.get('temperature', 0.9), workdata.get('stream', True)):
                    logger.warning(f'LLM流返回={chunk}')
                    yield f"{chunk}"

            elif llmsdk in  ['ollama']:
                # 调用llm大模型
                logger.warning(f'从ollama调用llm大模型')
            else:
                logger.warning(f'不支持的llm模型={llmsdk}')
                yield f"不支持的llm模型={llmsdk}"
        else:
            logger.warning(f'agent工作处理函数错误')
            yield f"agent工作处理函数错误"

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
        yield f"错误"



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








