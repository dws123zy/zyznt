# _*_coding:utf-8 _*_

from openai import OpenAI
from openai import AsyncOpenAI
import logging
import json
import time
import traceback
import asyncio

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

        # 执行LLM请求
        completion = client.chat.completions.create(
            model=mod,
            temperature=temperature,  # 热度
            messages=msg,  # 消息列表、提示词、上下文
            tools=tools,  # 工具集
        )

        # 有工具调用时循环，保证多轮工具调用
        tool_while = True  # 非工具调用时，此值改为假
        nub = 0  # 控制工具调用轮数，以免llm死循环调用
        while tool_while and nub < 10:
            nub  = nub + 1
            if not completion:
                return 'llm调用失败'
            # 流式获取
            msg_type = 'text'  # 默认为text，还有个是tool工具调用
            tool_data_chunk = []
            # 解析llm返回的结果
            chunk_dict = json.loads(completion.model_dump_json())
            choices = chunk_dict.get('choices')
            if choices:
                delta = choices[0]['message']  # 流式的message是delta
                # 判断是否为工具调用
                if delta.get('tool_calls') and msg_type in ['text']:  # 此轮为工具调用
                    msg_type = 'tool'
                # 按类型走对应的逻辑
                if msg_type in ['tool']:  # 工具调用，收集数据
                    logger.warning('工具调用数据块')
                    tool_data_chunk= delta.get('tool_calls')
                else:  # 正常文本回复，非工具调用，流式回复
                    if delta.get('reasoning_content'):  # 输出推理内容+正常文本
                        logger.warning(f'时间{time.time()}，推理内容={delta['reasoning_content']}')
                        return f"reasoning_content:{delta['reasoning_content']}  content:{delta['content']}"
                    elif delta.get('content'):
                        # print('正常文本回复，非推理')
                        logger.warning(f'时间{time.time()}, 输出内容={delta['content']}')
                        return f"content:{delta['content']}"
            # 执行工具调用
            if tool_data_chunk:
                # 组合获取完整工具调用数据
                tool_data =tool_data_chunk
                logger.warning(f'要调用的工具数据={tool_data}')
                if not tool_data:
                    logger.warning('调用工具失败,无工具调用数据')
                    return '调用工具失败'
                # 调用工具
                # 同步函数中调用异步函数
                tool_result =  asyncio.run(tool_call_result(tool_data))
                # 组合到msg中返回给大模型
                delta = tool_data_chunk[0]['choices'][0]['message']
                delta['tool_calls'] = tool_data
                msg.append(delta)  # 增加llm工具调用数据
                # 增加工具调用结果
                if tool_result:
                    msg = msg+tool_result
                else:
                    return '调用工具失败'
                # 执行LLM请求
                completion = client.chat.completions.create(
                    model=mod,
                    temperature=temperature,  # 热度
                    messages=msg,  # 消息列表、提示词、上下文
                    tools=tools,  # 工具集
                )
            else:
                tool_while = False
                return 'llm调用失败'

        # lent = time.time()
        # print('获取流完成，所用时间=', lent - lst)

        return completion
    except Exception as e:
        logger.error({"openai_llm stream错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return ''




'''openai-sdk-llm大模型 流式'''

async def openai_llm_stream(msg, apikey, url, mod, tools=None, temperature=0.9, stream=True):
    try:
        if not tools:
            tools = None
        # 组合客户端
        client = AsyncOpenAI(
            api_key = apikey,
            base_url=url,
        )

        # 执行LLM请求
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        yield {"time": now_time, "text": "开始调用llm"}
        logger.warning(f'开始调用llm,现在的msg={msg}')
        completion = await client.chat.completions.create(
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
            async for chunk in completion:
                chunk_dict = json.loads(chunk.model_dump_json())
                choices = chunk_dict.get('choices')
                if choices:
                    delta = choices[0]['delta']  # 流式的message是delta
                    # 判断是否为工具调用
                    if delta.get('tool_calls') and msg_type in ['text']:  # 此轮为工具调用
                        msg_type = 'tool'
                    # 按类型走对应的逻辑
                    if msg_type in ['tool']:  # 工具调用，收集数据
                        logger.warning('工具调用数据块')
                        tool_data_chunk.append(chunk_dict)
                    else:  # 正常文本回复，非工具调用，流式回复
                        if delta.get('reasoning_content'):  # 输出推理内容
                            logger.warning(f'时间{time.time()}, 推理内容={delta['reasoning_content']}')
                            yield {'reasoning_content': delta['reasoning_content']}
                        elif delta.get('content'):
                            # print('正常文本回复，非推理')
                            logger.warning(f'时间{time.time()}, 回复内容={delta['content']}')
                            yield delta['content']
            # 执行工具调用
            if tool_data_chunk:
                yield '准备调用工具...'
                # 组合获取完整工具调用数据
                tool_data = await parse_tool_data(tool_data_chunk)
                logger.warning(f'解析后的工具数据={tool_data}')
                if not tool_data:
                    logger.warning('调用工具失败,无工具调用数据')
                    yield '调用工具失败'
                    break
                # 调用工具
                tool_status = f'开始调用工具={tool_data[0].get('function', {}).get('name')}'
                logger.warning(tool_status)
                yield tool_status
                now_time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                yield {"time": now_time2, "text": tool_status}
                tool_result = await tool_call_result(tool_data)
                # 组合到msg中返回给大模型
                delta = tool_data_chunk[0]['choices'][0]['delta']
                delta['tool_calls'] = tool_data
                msg.append(delta)  # 增加llm工具调用数据
                # 增加工具调用结果
                now_time3 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                if tool_result:
                    msg = msg+tool_result
                    yield {"time": now_time3, "text": f'工具调用结果={tool_result}'}
                else:
                    yield '调用工具失败'
                    yield {"time": now_time3, "text": f'工具调用失败'}
                    break
                # 执行LLM请求
                yield {"time": now_time3, "text": '开始调用llm'}
                logger.warning(f'现在的msg数据={msg}')
                completion = await client.chat.completions.create(
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
        yield 'openai_llm stream错误，暂停执行'



'''解析流式工具数据'''

async def parse_tool_data(toollist):
    try:
        logger.warning(f"解析流式工具数据={toollist}")
        # 初始化累积工具调用的数组
        accumulated_tool_calls = []

        for chunk_dict in toollist:
            if chunk_dict.get("choices"):
                for choice in chunk_dict["choices"]:
                    tool_calls = choice.get("delta", {}).get("tool_calls", [])
                    if tool_calls:
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

async def tool_call_result(accumulated_tool_calls):
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
                        # 获取当前事件循环（若已存在）
                        # loop = asyncio.get_event_loop()
                        tool_result = await mcp_client(mcp_data, 'call_tool',tool_call)
                        tool_res_list.append(tool_result)
                    else:
                        logger.warning(f"工具类型为{tool_data.get('type')},调用普通工具模块")

                except Exception as e2:
                    logger.error(f"工具{tool_call["function"]["name"]}调用错误:: {e2}")


        return tool_res_list
    except Exception as e:
        logger.error({"工具调用并返回结果错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return []



'''

[{'type': 'function', 'function': {'name': 'generate_area_chart/mcp-server-chart', 'description': "Generate a area chart to show data trends under continuous independent variables and observe the overall data trend, such as, displacement = velocity (average or instantaneous) × time: s = v × t. If the x-axis is time (t) and the y-axis is velocity (v) at each moment, an area chart allows you to observe the trend of velocity over time and infer the distance traveled by the area's size.", 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'time': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['time', 'value']}, 'minItems': 1, 'description': "Data for area chart, such as, [{ time: '2018', value: 99.9 }]."}, 'stack': {'type': 'boolean', 'default': False, 'description': "Whether stacking is enabled. When enabled, area charts require a 'group' field in the data."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_bar_chart/mcp-server-chart', 'description': 'Generate a bar chart to show data for numerical comparisons among different categories, such as, comparing categorical data and for horizontal comparisons.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'category': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['category', 'value']}, 'minItems': 1, 'description': "Data for bar chart, such as, [{ category: '分类一', value: 10 }]."}, 'group': {'type': 'boolean', 'default': False, 'description': "Whether grouping is enabled. When enabled, bar charts require a 'group' field in the data. When `group` is true, `stack` should be false."}, 'stack': {'type': 'boolean', 'default': True, 'description': "Whether stacking is enabled. When enabled, bar charts require a 'group' field in the data. When `stack` is true, `group` should be false."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_column_chart/mcp-server-chart', 'description': 'Generate a column chart, which are best for comparing categorical data, such as, when values are close, column charts are preferable because our eyes are better at judging height than other visual elements like area or angles.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'category': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['category', 'value']}, 'minItems': 1, 'description': "Data for column chart, such as, [{ category: '北京' value: 825; group: '油车' }]."}, 'group': {'type': 'boolean', 'default': True, 'description': "Whether grouping is enabled. When enabled, column charts require a 'group' field in the data. When `group` is true, `stack` should be false."}, 'stack': {'type': 'boolean', 'default': False, 'description': "Whether stacking is enabled. When enabled, column charts require a 'group' field in the data. When `stack` is true, `group` should be false."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_dual_axes_chart/mcp-server-chart', 'description': 'Generate a dual axes chart which is a combination chart that integrates two different chart types, typically combining a bar chart with a line chart to display both the trend and comparison of data, such as, the trend of sales and profit over time.', 'parameters': {'type': 'object', 'properties': {'categories': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'description': "Categories for dual axes chart, such as, ['2015', '2016', '2017']."}, 'series': {'type': 'array', 'items': {'type': 'object', 'properties': {'type': {'type': 'string', 'enum': ['column', 'line'], 'description': "The optional value can be 'column' or 'line'."}, 'data': {'type': 'array', 'items': {'type': 'number'}, 'description': 'When type is column, the data represents quantities, such as [91.9, 99.1, 101.6, 114.4, 121]. When type is line, the data represents ratios and its values are recommended to be less than 1, such as [0.055, 0.06, 0.062, 0.07, 0.075].'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of the chart series.'}}, 'required': ['type', 'data']}, 'minItems': 1}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}}, 'required': ['categories', 'series'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_fishbone_diagram/mcp-server-chart', 'description': 'Generate a fishbone diagram chart to uses a fish skeleton, like structure to display the causes or effects of a core problem, with the problem as the fish head and the causes/effects as the fish bones. It suits problems that can be split into multiple related factors.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'$ref': '#/properties/data/properties/children/items'}}}, 'required': ['name']}}}, 'required': ['name'], 'description': "Data for fishbone diagram chart, such as, { name: 'main topic', children: [{ name: 'topic 1', children: [{ name: 'subtopic 1-1' }] }."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_flow_diagram/mcp-server-chart', 'description': 'Generate a flow diagram chart to show the steps and decision points of a process or system, such as, scenarios requiring linear process presentation.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'nodes': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}, 'minItems': 1}, 'edges': {'type': 'array', 'items': {'type': 'object', 'properties': {'source': {'type': 'string'}, 'target': {'type': 'string'}, 'name': {'type': 'string', 'default': ''}}, 'required': ['source', 'target']}}}, 'required': ['nodes', 'edges'], 'description': "Data for flow diagram chart, such as, { nodes: [{ name: 'node1' }, { name: 'node2' }], edges: [{ source: 'node1', target: 'node2', name: 'edge1' }] }."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_histogram_chart/mcp-server-chart', 'description': 'Generate a histogram chart to show the frequency of data points within a certain range. It can observe data distribution, such as, normal and skewed distributions, and identify data concentration areas and extreme points.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'number'}, 'minItems': 1, 'description': 'Data for histogram chart, such as, [78, 88, 60, 100, 95].'}, 'binNumber': {'anyOf': [{'type': 'number'}, {'not': {}}, {'type': 'null'}], 'default': None, 'description': 'Number of intervals to define the number of intervals in a histogram.'}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_line_chart/mcp-server-chart', 'description': "Generate a line chart to show trends over time, such as, the ratio of Apple computer sales to Apple's profits changed from 2000 to 2016.", 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'time': {'type': 'string'}, 'value': {'type': 'number'}}, 'required': ['time', 'value']}, 'minItems': 1, 'description': "Data for line chart, such as, [{ time: '2015', value: 23 }]."}, 'stack': {'type': 'boolean', 'default': False, 'description': "Whether stacking is enabled. When enabled, line charts require a 'group' field in the data."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_mind_map/mcp-server-chart', 'description': 'Generate a mind map chart to organizes and presents information in a hierarchical structure with branches radiating from a central topic, such as, a diagram showing the relationship between a main topic and its subtopics.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'$ref': '#/properties/data/properties/children/items'}}}, 'required': ['name']}}}, 'required': ['name'], 'description': "Data for mind map chart, such as, { name: 'main topic', children: [{ name: 'topic 1', children: [{ name:'subtopic 1-1' }] }."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_network_graph/mcp-server-chart', 'description': 'Generate a network graph chart to show relationships (edges) between entities (nodes), such as, relationships between people in social networks.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'nodes': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}, 'minItems': 1}, 'edges': {'type': 'array', 'items': {'type': 'object', 'properties': {'source': {'type': 'string'}, 'target': {'type': 'string'}, 'name': {'type': 'string', 'default': ''}}, 'required': ['source', 'target']}}}, 'required': ['nodes', 'edges'], 'description': "Data for network graph chart, such as, { nodes: [{ name: 'node1' }, { name: 'node2' }], edges: [{ source: 'node1', target: 'node2', name: 'edge1' }] }"}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_pie_chart/mcp-server-chart', 'description': 'Generate a pie chart to show the proportion of parts, such as, market share and budget allocation.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'category': {'type': 'string'}, 'value': {'type': 'number'}}, 'required': ['category', 'value']}, 'minItems': 1, 'description': "Data for pie chart, such as, [{ category: '分类一', value: 27 }]."}, 'innerRadius': {'type': 'number', 'default': 0, 'description': 'Set the innerRadius of pie chart, the value between 0 and 1. Set the pie chart as a donut chart. Set the value to 0.6 or number in [0 ,1] to enable it.'}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_radar_chart/mcp-server-chart', 'description': 'Generate a radar chart to display multidimensional data (four dimensions or more), such as, evaluate Huawei and Apple phones in terms of five dimensions: ease of use, functionality, camera, benchmark scores, and battery life.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['name', 'value']}, 'minItems': 1, 'description': "Data for radar chart, such as, [{ name: 'Design', value: 70 }]."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_scatter_chart/mcp-server-chart', 'description': 'Generate a scatter chart to show the relationship between two variables, helps discover their relationship or trends, such as, the strength of correlation, data distribution patterns.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'x': {'type': 'number'}, 'y': {'type': 'number'}}, 'required': ['x', 'y']}, 'minItems': 1, 'description': 'Data for scatter chart, such as, [{ x: 10, y: 15 }].'}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_treemap_chart/mcp-server-chart', 'description': 'Generate a treemap chart to display hierarchical data and can intuitively show comparisons between items at the same level, such as, show disk space usage with treemap.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'number'}, 'children': {'type': 'array', 'items': {'$ref': '#/properties/data/items'}}}, 'required': ['name', 'value']}, 'minItems': 1, 'description': "Data for treemap chart, such as, [{ name: 'Design', value: 70, children: [{ name: 'Tech', value: 20 }] }]."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_word_cloud_chart/mcp-server-chart', 'description': 'Generate a word cloud chart to show word frequency or weight through text size variation, such as, analyzing common words in social media, reviews, or feedback.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'text': {'type': 'string'}, 'value': {'type': 'number'}}, 'required': ['text', 'value']}, 'minItems': 1, 'description': "Data for word cloud chart, such as, [{ value: '4.272', text: '形成' }]."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}]

'''






