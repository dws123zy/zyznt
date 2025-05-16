# _*_coding:utf-8 _*_

from openai import OpenAI
import logging
import json
import time
import traceback
import os

# 本地模块
from data.data import get_zydict
from mod.zymcp import mcp_client


'''LLM大模型处理模块'''


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

        # 有工具调用时循环，保证多轮工具调用
        tool_while = True  # 非工具调用时，此值改为假
        nub = 0  # 控制工具调用轮数，以免llm死循环调用
        while tool_while and nub < 10:
            nub  = nub + 1
            if not completion:
                break
            # 流式获取
            msg_type = 'text'  # 默认为text，还有个是tool工具调用
            tool_data_chunk = []
            for chunk in completion:
                chunk_dict = json.loads(chunk.model_dump_json())
                choices = chunk_dict.get('choices')
                if choices:
                    delta = choices[0]['delta']  # 流式的message是delta
                    # 判断是否为工具调用
                    if delta.get('tool_calls') and msg_type in ['text']:  # 此轮为工具调用
                        msg_type = 'tool'
                    # 按类型走对应的逻辑
                    if msg_type in ['tool']:  # 工具调用，收集数据
                        print('工具调用数据块')
                        tool_data_chunk.append(chunk_dict)
                    else:  # 正常文本回复，非工具调用，流式回复
                        if delta.get('reasoning_content'):  # 输出推理内容
                            print('时间', time.time(), '内容=', delta['reasoning_content'])
                            yield f"reasoning_content:{delta['content']}"
                        elif delta.get('content'):
                            print('正常文本回复，非推理')
                            print('时间', time.time(), '内容=', delta['content'])
                            yield delta['content']
            # 执行工具调用
            if tool_data_chunk:
                yield '调用工具中'
                # 组合获取完整工具调用数据
                tool_data = parse_tool_data(tool_data_chunk)
                if not tool_data:
                    logger.warning('调用工具失败,无工具调用数据')
                # 调用工具
                tool_result = tool_call_result(tool_data)
                # 组合到msg中返回给大模型
                delta = tool_data_chunk[0]['choices'][0]['delta']
                delta['tool_calls'] = tool_data
                msg.append(delta)  # 增加llm工具调用数据
                # 增加工具调用结果
                msg = msg+tool_result
                # 执行LLM请求
                completion = client.chat.completions.create(
                    model=mod,
                    temperature=temperature,  # 热度
                    messages=msg,  # 消息列表、提示词、上下文
                    tools=tools,  # 工具集
                    stream=stream  # 流式输出
                )
            else:
                tool_while = False

        # lent = time.time()
        # print('获取流完成，所用时间=', lent - lst)

        # return completion
    except Exception as e:
        logger.error({"openai_llm stream错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        yield ''



'''解析流式工具数据'''

def parse_tool_data(toollist):
    try:
        # 初始化累积工具调用的数组
        accumulated_tool_calls = []

        for chunk_dict in toollist:
            if chunk_dict.get("choices"):
                for choice in chunk_dict["choices"]:
                    tool_calls = choice.get("delta", {}).get("tool_calls", [])
                    for tool_call in tool_calls:
                        index = tool_call.get("index", 0)
                        # 扩展数组以容纳新索引
                        while len(accumulated_tool_calls) <= index:
                            accumulated_tool_calls.append({
                                "id": "",
                                "type": "function",
                                "index": index,
                                "function": {
                                    "name": "",
                                    "arguments": ""
                                }
                            })
                        current_tool_call = accumulated_tool_calls[index]

                        # 合并 id
                        if "id" in tool_call and tool_call["id"] and not current_tool_call["id"]:
                            current_tool_call["id"] += tool_call["id"]
                        # 合并 function name
                        if "function" in tool_call and "name" in tool_call["function"] and tool_call["function"]["name"]:
                            current_tool_call["function"]["name"] += tool_call["function"]["name"]
                        # 合并 arguments
                        if "function" in tool_call and "arguments" in tool_call["function"] and tool_call["function"]["arguments"]:
                            current_tool_call["function"]["arguments"] += tool_call["function"]["arguments"]
        return accumulated_tool_calls
    except Exception as e:
        logger.error({"解析流式工具数据错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return []



'''工具调用并返回结果'''

def tool_call_result(accumulated_tool_calls):
    try:
        tool_res_list = []
        # 流处理结束后，提取工具调用信息
        for tool_call in accumulated_tool_calls:
            if tool_call["function"]["name"]:  # 有工具名就可以调用
                try:
                    # 获取工具信息并判断工具类型
                    tool_name = tool_call["function"]["name"].split('/')
                    tool_data = get_zydict('tool', tool_name[1])
                    if tool_data.get('type') in ['mcp']:
                        logger.warning(f"工具类型为mcp，调用mcp模块")
                        mcp_data = tool_data.get('data', {})
                        tool_result = mcp_client(mcp_data, 'call_tool',tool_call)
                        tool_res_list.append(tool_result)
                    else:
                        logger.warning(f"工具类型为{tool_data.get('type')},调用普通工具模块")

                except json.JSONDecodeError:
                    print("参数解析失败:", tool_call["function"]["arguments"])


        return tool_res_list
    except Exception as e:
        logger.error({"工具调用并返回结果错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return ''










