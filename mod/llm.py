# _*_coding:utf-8 _*_

from openai import OpenAI
import logging
import json
import time
import traceback
import os


'''日志'''

logger = logging.getLogger(__name__)



'''
api_key = ''
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
model = 'qwen2.5:7b'

# 通过 messages 数组实现上下文管理
messages = [
    {'role': 'system', 'content': str(dy)},
    {'role': 'system', 'content': zl2},
    {'role': 'assistant', 'content': '您好，我是平安车险续保中心的，我看咱家车险快到期了，现在有一个团购优惠活动，最低可以到4.7折，您看方便加下您的微信，给您发个报价吗？'}
]

# 模型列表
mxlist = ['qwen-plus', 'qwen2.5-7b-instruct-1m', 'qwen-turbo', 'deepseek-r1', 'deepseek-v3', 'qwen-max-2025-01-25',
          'deepseek-r1-distill-qwen-1.5b', 'qwen2.5-14b-instruct-1m', 'qwen2.5:7b', 'ernie-4.0-turbo-8k',
          'deepseek-v3-241226', 'doubao-1.5-lite-32k-250115', 'doubao-1.5-pro-32k-250115']

# base_url="https://qianfan.baidubce.com/v2",  # 百度云
# base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云
# base_url='http://localhost:11434/v1/',  # 本地
# base_url='https://api.lkeap.cloud.tencent.com/v1',  # 腾讯云
base_url='https://ark.cn-beijing.volces.com/api/v3',  # 火山

'''



'''openai-sdk-llm大模型'''

def openai_llm(msg, apikey, url, mod, tools=None, temperature=0.9):
    try:
        if not tools:
            tools = None
        # 组合客户端
        client = OpenAI(
            api_key = apikey,
            base_url=url,
        )

        completion = client.chat.completions.create(
            model=mod,
            temperature=temperature,  # 热度
            messages=msg,  # 消息列表、提示词、上下文
            tools=tools,  # 工具集
            # stream=stream  # 流式输出
        )

        return completion
    except Exception as e:
        logger.error({"openai_llm错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return ''


        # # 流式获取
        # nrlist = ''
        # lst = time.time()
        # print('开始获取流=', lst)
        # for chunk in completion:
        #     nr = json.loads(chunk.model_dump_json())
        #     wb = nr.get('choices')
        #     if wb:
        #
        #         if nr.get('choices')[0]['delta']['content']:
        #             print('时间', time.time(), '内容=', nr.get('choices')[0]['delta']['content'])
        #             nrlist = nrlist + nr.get('choices')[0]['delta']['content']
        #             if bdfh(nrlist):  # 有标点时说明是一句话了
        #                 bdwz = bdfhwz(nrlist) + 1  # 把标记也截取走，所以要+1
        #                 xtext = nrlist[:bdwz]
        #
        #                 llmlsdh[cdrid][dhid]['x'] = llmlsdh[cdrid][dhid]['x'] + xtext
        #                 print('成功加入一句话=', xtext)
        #                 # 清空nrlist已取走的内容
        #                 nrlist = nrlist.replace(xtext, '')
        #
        # lent = time.time()
        # print('获取流完成，所用时间=', lent - lst)



'''openai-sdk-llm大模型'''

def openai_llm_stream(msg, apikey, url, mod, tools=None, temperature=0.9, stream=True):
    try:
        if not tools:
            tools = None
        # 组合客户端
        client = OpenAI(
            api_key = apikey,
            base_url=url,
        )

        # 执行LLM请求
        completion = client.chat.completions.create(
            model=mod,
            temperature=temperature,  # 热度
            messages=msg,  # 消息列表、提示词、上下文
            tools=tools,  # 工具集
            stream=stream  # 流式输出
        )
        # 流式获取
        # nrlist = ''
        # lst = time.time()
        # print('开始获取流=', lst)
        if completion:
            for chunk in completion:
                nr = json.loads(chunk.model_dump_json())
                wb = nr.get('choices')
                if wb:

                    if nr.get('choices')[0]['delta']['content']:
                        print('时间', time.time(), '内容=', nr.get('choices')[0]['delta']['content'])
                        yield nr.get('choices')[0]['delta']['content']
        else:
            yield ''

        # lent = time.time()
        # print('获取流完成，所用时间=', lent - lst)

        # return completion
    except Exception as e:
        logger.error({"openai_llm stream错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        yield ''














