aa = {
  "user": "dws@zy",
  "appid": "zy001",
  "token": "d8685773c6d2b04215e24fca9138e307",
  "time": "string",
  "data": {
    "ragdata": {"ragid": "rag1746599379166"},
    "data":{"id": "457832990638360632","text": "测试呼叫中心知识,操作手册","state": "t","q_text": "","keyword": "","metadata":{"filename": "逻辑试题 -带答案.txt"}}
}}


agent = [
  {'field': 'name', 'text': '智能体名称', 'default': '', 'placeholder': '给您的智能体取名', 'type': 'input', 'required': 't', 'update': 't'},
  {'field': 'remarks', 'text': '描述介绍', 'default': '', 'placeholder': '介绍下您的智能体', 'type': 'text', 'required': 'f', 'update': 't'},
  {'field': 'agentid', 'text': '智能体id', 'default': 'in', 'placeholder': '智能体id', 'type': 'input', 'required': 'f', 'update': 't', 'show': 'f'},
  {'field': 'icon', 'text': '智能体图标', 'default': '', 'placeholder': '图标', 'type': 'input', 'required': 'f', 'update': 't'},
  {'field': 'user', 'text': '创建人', 'default': '', 'placeholder': '创建人', 'type': 'input', 'required': 'f', 'update': 't'},
  {'field': 'appid', 'text': '公司id', 'default': '', 'placeholder': '公司id', 'type': 'input', 'required': 'f', 'update': 't', 'show': 'f'},
  {'field': 'state', 'text': '状态', 'default': '', 'placeholder': '智能体状态', 'type': 'input', 'required': 'f', 'update': 't'},
  {'field': 'time', 'text': '更新时间', 'default': '', 'placeholder': '更新时间', 'type': 'input', 'required': 'f', 'update': 't'},
  {'field': 'data', 'text': '配置数据', 'default': '', 'placeholder': '智能体配置', 'type': 'data', 'required': 'f', 'update': 't',
   'data': [
            {'field': 'prompt', 'text': '提示词', 'default': '', 'placeholder': '智能体提示词', 'type': 'text', 'required': 't', 'update': 't'},
            {'field': 'prologue', 'text': '开场白', 'default': '', 'placeholder': '开场白', 'type': 'text', 'required': 'f', 'update': 't'},
            {'field': 'context', 'text': 'llm上下文', 'default': '', 'placeholder': 'llm上下文', 'type': 'text', 'required': 'f', 'update': 't'},
            {'field': 'memory', 'text': '记忆对话', 'default': 't', 'placeholder': '多轮对话', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]},
            {'field': 'llm', 'text': 'LLM大模型', 'default': '', 'placeholder': '选择大模型', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': 'qwen-plus', 'value': 'qwen-plus'}, {'label': 'deepseek-v3', 'value': 'deepseek-v3'}]},
            {'field': 'tools', 'text': '工具列表', 'default': '', 'placeholder': '工具列表，多选', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]},
            {'field': 'temperature', 'text': '回复热度', 'default': '0.8', 'placeholder': 'LLM大模型生成文本的多样性，取值范围： [0, 2)，值越高文本越多样', 'type': 'input', 'required': 'f', 'update': 't'},
            {'field': 'stream', 'text': '流式输出', 'default': 't', 'placeholder': '回复以流式输出', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]},
            {'field': 'enable_thinking', 'text': '模型推理', 'default': 'f', 'placeholder': '部分模型可配置推理，不以持配置的无效,推理模型此配置也无效', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]},
            {'field': 'up_file', 'text': '文件上传', 'default': 'f', 'placeholder': '开户后可上传文件', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]},
            {'field': 'img_show', 'text': '多态显示', 'default': 't', 'placeholder': '开户后自动显示url图片、文件、图表', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]},
             {'field': 'rag', 'text': 'rag知识库', 'default': '', 'placeholder': '知识库列表，多选', 'type': 'select',
              'required': 'f', 'update': 't', 'options': []},
             {'field': 'file', 'text': '文件知识库', 'default': '', 'placeholder': '文件列表，多选,所有文件总字数建议不超过5000', 'type': 'select',
              'required': 'f', 'update': 't', 'options': []},
             {'field': 'website', 'text': '网页搜索', 'default': '', 'placeholder': '网页搜索知识', 'type': 'select',
              'required': 'f', 'update': 't', 'options': []},
             {'field': 'asr', 'text': '语音识别模型', 'default': '', 'placeholder': '语音获取和识别', 'type': 'select',
              'required': 'f', 'update': 't', 'options': []},
             {'field': 'tts', 'text': 'TTS模型', 'default': '', 'placeholder': '文本转语音', 'type': 'select',
              'required': 'f', 'update': 't', 'options': []},
   ]}
]

print(agent)


ll = [['a', 'b'], ['c', 'd']]

print('\n'.join('\n'.join(l) for l in ll))


ab = '900100'

print(ab[:2])

llm = {'id': 'chatcmpl-32a3cda6-d359-9b5e-842b-67e2f284eed8',
       'choices': [{'finish_reason': 'tool_calls', 'index': 0, 'logprobs': None,
                    'message': {'content': '', 'refusal': None, 'role': 'assistant', 'annotations': None, 'audio': None, 'function_call': None,
                                'tool_calls': [{'id': 'call_dc913fd551ef4d7e9fc7b0', 'function': {'arguments': '{}', 'name': 'get_current_time/ksdewlkjfoi156'}, 'type': 'function', 'index': 0}]
                                }
                    }], 'created': 1747360072, 'model': 'qwen2.5-7b-instruct-1m', 'object': 'chat.completion', 'service_tier': None, 'system_fingerprint': None, 'usage': {'completion_tokens': 24, 'prompt_tokens': 384, 'total_tokens': 408, 'completion_tokens_details': None, 'prompt_tokens_details': None}}

nr={'id': 'chatcmpl-da9491ff-112b-998e-8384-311a325a059a',
    'choices': [{'delta': {'content': '好的，您的', 'function_call': None, 'refusal': None, 'role': None, 'tool_calls': None}, 'finish_reason': None, 'index': 0, 'logprobs': None}], 'created': 1747364003, 'model': 'qwen-max-2025-01-25', 'object': 'chat.completion.chunk', 'service_tier': None, 'system_fingerprint': None, 'usage': None}


nrlist = [{'id': 'chatcmpl-285f0b2d-1647-9751-b886-30c391077f83', 'choices': [{'delta': {'content': None, 'function_call': None, 'refusal': None, 'role': 'assistant', 'tool_calls': [{'index': 0, 'id': 'call_9d466125dfa140b4b7c0a5', 'function': {'arguments': '{"location":', 'name': 'get_current_weather'}, 'type': 'function'}]}, 'finish_reason': None, 'index': 0, 'logprobs': None}], 'created': 1747365353, 'model': 'qwen2.5-7b-instruct-1m', 'object': 'chat.completion.chunk', 'service_tier': None, 'system_fingerprint': None, 'usage': None},
          {'id': 'chatcmpl-285f0b2d-1647-9751-b886-30c391077f83', 'choices': [{'delta': {'content': None, 'function_call': None, 'refusal': None, 'role': None, 'tool_calls': [{'index': 0, 'id': '', 'function': {'arguments': ' "周口"}', 'name': ''}, 'type': 'function'}]}, 'finish_reason': None, 'index': 0, 'logprobs': None}], 'created': 1747365353, 'model': 'qwen2.5-7b-instruct-1m', 'object': 'chat.completion.chunk', 'service_tier': None, 'system_fingerprint': None, 'usage': None},
          {'id': 'chatcmpl-285f0b2d-1647-9751-b886-30c391077f83', 'choices': [{'delta': {'content': None, 'function_call': None, 'refusal': None, 'role': None, 'tool_calls': [{'index': 0, 'id': '', 'function': {'arguments': None, 'name': None}, 'type': 'function'}]}, 'finish_reason': None, 'index': 0, 'logprobs': None}], 'created': 1747365353, 'model': 'qwen2.5-7b-instruct-1m', 'object': 'chat.completion.chunk', 'service_tier': None, 'system_fingerprint': None, 'usage': None}]

import json

# 初始化累积工具调用的数组
accumulated_tool_calls = []

for chunk_dict in nrlist:
    # 将 chunk 转换为 JSON 字符串，再解析为字典
    # chunk_dict = json.loads(chunk.model_dump_json())  # 关键步骤
    if chunk_dict.get("choices"):
        for choice in chunk_dict["choices"]:
            delta = choice.get("delta", {})
            tool_calls = delta.get("tool_calls", [])
            for tool_call in tool_calls:
                index = tool_call.get("index", 0)
                # 扩展数组以容纳新索引
                while len(accumulated_tool_calls) <= index:
                    accumulated_tool_calls.append({
                        "id": "",
                        "type": "function",
                        "function": {
                            "name": "",
                            "arguments": ""
                        }
                    })
                current_tool_call = accumulated_tool_calls[index]

                # 合并 id
                if "id" in tool_call and tool_call["id"]:
                    current_tool_call["id"] += tool_call["id"]
                # 合并 function name
                if "function" in tool_call and "name" in tool_call["function"] and tool_call["function"]["name"]:
                    current_tool_call["function"]["name"] += tool_call["function"]["name"]
                # 合并 arguments
                if "function" in tool_call and "arguments" in tool_call["function"] and tool_call["function"]["arguments"]:
                    current_tool_call["function"]["arguments"] += tool_call["function"]["arguments"]

# 流处理结束后，提取工具调用信息
for tool_call in accumulated_tool_calls:
    if tool_call["function"]["arguments"]:
        try:
            args = json.loads(tool_call["function"]["arguments"])
            print(f"调用工具 {tool_call['function']['name']}，参数：{args}")
            # 执行工具调用，例如：get_weather(city=args["city"])
        except json.JSONDecodeError:
            print("参数解析失败:", tool_call["function"]["arguments"])


print(accumulated_tool_calls)



agent01 = {'prompt': '你是一个智能助手，你的名字是小卓，回答呼叫中心系统和天气相关问题，如果用户的问题偏离主题，请拉回主题，回复尽量简洁，控制在50字左右', 'llm': 'qwen-plus', 'tools': [{'type': 'function', 'function': {'name': 'map_weather', 'description': '天气查询服务: 通过行政区划或是经纬度坐标查询实时天气信息及未来5天天气预报(注意: 使用经纬度坐标需要高级权限).', 'parameters': {'type': 'object', 'required': [], 'properties': {'location': {'type': 'string', 'description': '经纬度, 经度在前纬度在后, 逗号分隔 (需要高级权限)'}, 'district_id': {'type': 'integer', 'description': '行政区划代码, 需保证为6位无符号整数'}}}}}]}

print(f'agent01={agent01}')





al = [{'label': 'LLM大模型', 'value': 'llm', 'placeholder': """LLM大模型配置:\n skd： openai、ollama或其它支持的类型，默认openai，必填  \n url：连接LLM的url地址，必填 \n apikey：LLM平台鉴权的api_key，必填 \n module：LLM模型名称，必填 \n maxtext：模型支持的最大上下文，非必填 \n provider：模型提供商，非必填 \n remarks：模型描述，非必填 \n 配置示例：{"sdk": "openai", "sdkdir": "", "url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "apikey": "***************b82cf", "module": "qwen-plus", "maxtext": "", "provider": "阿里云百炼", "remarks": ""}"""}, {'label': 'embd模型', 'value': 'embd', 'placeholder': 'embd向量模型配置:\n'}, {'label': 'MCP服务', 'value': 'mcp', 'placeholder': 'mcp服务配置:'}, {'label': '检索项', 'value': 'filter', 'placeholder': '动态检索项配置:\n'}, {'label': '动态表单', 'value': 'form', 'placeholder': '动态表单配置:'}]

mcp_data = {'mcpServers': {'baidu-maps': {'url': 'https://mcp.map.baidu.com/sse?ak=oqIwmwH7yNI9v1EQQXbTIoo3VB1hPsFk'}},
            'name': 'baidu-maps', 'mcp_type': 'sse', 'tools': []}




# from pydantic import BaseModel, EmailStr, ValidationError, Field
#
# class UserCreate(BaseModel):
#     name: str = Field(..., min_length=1, max_length=50)
#     age: int = Field(..., gt=0)
#     email: EmailStr
#
#
# def create_user(data):
#     try:
#         user_data = UserCreate(**data)
#         print(f"用户创建成功：{user_data.name}, {user_data.age}, {user_data.email}")
#         print(data.get('name'))
#         return user_data
#     except ValidationError as e:
#         print(f"校验错误：{e.errors()}")
#         for error in e.errors():
#             print(f"字段：{error['loc'][0]}, 错误：{error['msg']}")
#         return e.errors()
#
#
# # 正确示例
# valid_data = {
#     "name": "Alice",
#     "age": 30,
#     "email": "alice@example.com"
# }
# create_user(valid_data)

# 错误示例（年龄不符合）
# invalid_data = {
#     "name": "Bob",
#     "age": -5,
#     "email": "bob@example"
# }
# create_user(invalid_data)

print("智能体流配置数据")

start = {"type": "mod", "module": "start_mod", "module_name": "开始",
         "description": "开始，初始化系统变量和自定义变量，创建会话工作id，初始化空间",
         "input": "", "output": ""}

print(f"start={start}")


start_flow = {"type": "mod", "module": "start_mod", "module_name": "开始",
         "description": "开始，初始化系统变量和自定义变量，创建会话工作id，初始化空间",
          "name": "开始", "node_id": "a01", "note": "",
              "status": "", "nub": "0", "next": "a02", "upper": "",
              "input": {"system": {"user_input": "", "data": {}, "start_time": "", "end_time": "", "user": "", "session": ""},
                        "custom":{"a": "3"}},
              "output": ""}

print(f"start_flow={start_flow}")


end = {"type": "mod", "module": "end_mod", "module_name": "结束",
      "description": "结束，结束会话，保存会话记录，清空内存运行数据", "input": "", "output": ""}


print(f"end={end}")

end_flow = {"type": "mod", "module": "end_mod", "module_name": "结束",
         "description": "结束，结束会话，保存会话记录，清空内存运行数据",
          "name": "结束", "node_id": "a03", "note": "",
              "status": "", "nub": "0", "next": "", "upper": "", "input": "",
              "output": {"system": {"user_input": "", "data": {}, "start_time": "", "end_time": "", "user": "", "session": ""}, }
}

print(f"end_flow={end_flow}")



llm_mod = {"type": "mod", "module": "llm_mod", "module_name": "LLM大模型", "description": "LLM大模型调用并执行任务",
          "input": {"user_input": "", "llm": "LLM大模型", "prompt": "提示词", "tools": []}, "output": {"content": ""}}


print(f"llm_mod={llm_mod}")

llm_flow = {"type": "mod", "module": "llm_mod", "module_name": "LLM大模型", "description": "LLM大模型调用并执行任务",
          "name": "LLM大模型", "node_id": "a02", "note": "输入提示词让llm按你的要求工作",
              "status": "", "nub": "0", "next": "a03", "upper": "",
              "input": {"user_input": "quote/system/user_input", "llm": "qwen-plus", "prompt": "你是一个数据处理员，把此数据以/分隔一下", "tools": []},
            "output": {"content": ""}
}

print(f"llm_flow={llm_flow}")



agentflow = {"flow_data": {"a01": start_flow, "a02": llm_flow, "a03": end_flow}}

print(f"agentflow={agentflow}")


import uuid

uuid1 = uuid.uuid4()

print(uuid1)

print(str(uuid1)[:8])


ag = {'prompt': '你是一个智能助手，帮助用户实现他想要的', 'llm': 'qwen-plus', 'tools': []}

a3= {'prompt': '你是一个智能助手，帮助用户实现他想要的，当用户问软电话配置时，回复：您好，下图是软电话配置示例：![软电话配置示例图](https://zy-wendang.oss-cn-hangzhou.aliyuncs.com/img/rdh.png)，此图是标准的软电话配置。', 'llm': 'qwen-plus', 'tools': []}


t = {"mcpServers": {"mcp-server-chart": {"url": "http://139.196.36.245:1122/mcp"}},"name": "mcp-server-chart","mcp_type": "http","tools": []}


d = {'prompt': '你是一个智能助手，帮助用户实现他想要的，当用户问软电话配置时，回复：您好，下图是软电话配置示例：![软电话配置示例图](https://zy-wendang.oss-cn-hangzhou.aliyuncs.com/img/rdh.png)，此图是标准的软电话配置。', 'llm': 'qwen-plus', 'tools': [{'type': 'function', 'function': {'name': 'generate_area_chart/mcp-server-chart', 'description': "Generate a area chart to show data trends under continuous independent variables and observe the overall data trend, such as, displacement = velocity (average or instantaneous) × time: s = v × t. If the x-axis is time (t) and the y-axis is velocity (v) at each moment, an area chart allows you to observe the trend of velocity over time and infer the distance traveled by the area's size.", 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'time': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['time', 'value']}, 'minItems': 1, 'description': "Data for area chart, such as, [{ time: '2018', value: 99.9 }]."}, 'stack': {'type': 'boolean', 'default': False, 'description': "Whether stacking is enabled. When enabled, area charts require a 'group' field in the data."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_bar_chart/mcp-server-chart', 'description': 'Generate a bar chart to show data for numerical comparisons among different categories, such as, comparing categorical data and for horizontal comparisons.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'category': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['category', 'value']}, 'minItems': 1, 'description': "Data for bar chart, such as, [{ category: '分类一', value: 10 }]."}, 'group': {'type': 'boolean', 'default': False, 'description': "Whether grouping is enabled. When enabled, bar charts require a 'group' field in the data. When `group` is true, `stack` should be false."}, 'stack': {'type': 'boolean', 'default': True, 'description': "Whether stacking is enabled. When enabled, bar charts require a 'group' field in the data. When `stack` is true, `group` should be false."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_column_chart/mcp-server-chart', 'description': 'Generate a column chart, which are best for comparing categorical data, such as, when values are close, column charts are preferable because our eyes are better at judging height than other visual elements like area or angles.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'category': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['category', 'value']}, 'minItems': 1, 'description': "Data for column chart, such as, [{ category: '北京' value: 825; group: '油车' }]."}, 'group': {'type': 'boolean', 'default': True, 'description': "Whether grouping is enabled. When enabled, column charts require a 'group' field in the data. When `group` is true, `stack` should be false."}, 'stack': {'type': 'boolean', 'default': False, 'description': "Whether stacking is enabled. When enabled, column charts require a 'group' field in the data. When `stack` is true, `group` should be false."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_dual_axes_chart/mcp-server-chart', 'description': 'Generate a dual axes chart which is a combination chart that integrates two different chart types, typically combining a bar chart with a line chart to display both the trend and comparison of data, such as, the trend of sales and profit over time.', 'parameters': {'type': 'object', 'properties': {'categories': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'description': "Categories for dual axes chart, such as, ['2015', '2016', '2017']."}, 'series': {'type': 'array', 'items': {'type': 'object', 'properties': {'type': {'type': 'string', 'enum': ['column', 'line'], 'description': "The optional value can be 'column' or 'line'."}, 'data': {'type': 'array', 'items': {'type': 'number'}, 'description': 'When type is column, the data represents quantities, such as [91.9, 99.1, 101.6, 114.4, 121]. When type is line, the data represents ratios and its values are recommended to be less than 1, such as [0.055, 0.06, 0.062, 0.07, 0.075].'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of the chart series.'}}, 'required': ['type', 'data']}, 'minItems': 1}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}}, 'required': ['categories', 'series'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_fishbone_diagram/mcp-server-chart', 'description': 'Generate a fishbone diagram chart to uses a fish skeleton, like structure to display the causes or effects of a core problem, with the problem as the fish head and the causes/effects as the fish bones. It suits problems that can be split into multiple related factors.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'$ref': '#/properties/data/properties/children/items'}}}, 'required': ['name']}}}, 'required': ['name'], 'description': "Data for fishbone diagram chart, such as, { name: 'main topic', children: [{ name: 'topic 1', children: [{ name: 'subtopic 1-1' }] }."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_flow_diagram/mcp-server-chart', 'description': 'Generate a flow diagram chart to show the steps and decision points of a process or system, such as, scenarios requiring linear process presentation.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'nodes': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}, 'minItems': 1}, 'edges': {'type': 'array', 'items': {'type': 'object', 'properties': {'source': {'type': 'string'}, 'target': {'type': 'string'}, 'name': {'type': 'string', 'default': ''}}, 'required': ['source', 'target']}}}, 'required': ['nodes', 'edges'], 'description': "Data for flow diagram chart, such as, { nodes: [{ name: 'node1' }, { name: 'node2' }], edges: [{ source: 'node1', target: 'node2', name: 'edge1' }] }."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_histogram_chart/mcp-server-chart', 'description': 'Generate a histogram chart to show the frequency of data points within a certain range. It can observe data distribution, such as, normal and skewed distributions, and identify data concentration areas and extreme points.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'number'}, 'minItems': 1, 'description': 'Data for histogram chart, such as, [78, 88, 60, 100, 95].'}, 'binNumber': {'anyOf': [{'type': 'number'}, {'not': {}}, {'type': 'null'}], 'default': None, 'description': 'Number of intervals to define the number of intervals in a histogram.'}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_line_chart/mcp-server-chart', 'description': "Generate a line chart to show trends over time, such as, the ratio of Apple computer sales to Apple's profits changed from 2000 to 2016.", 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'time': {'type': 'string'}, 'value': {'type': 'number'}}, 'required': ['time', 'value']}, 'minItems': 1, 'description': "Data for line chart, such as, [{ time: '2015', value: 23 }]."}, 'stack': {'type': 'boolean', 'default': False, 'description': "Whether stacking is enabled. When enabled, line charts require a 'group' field in the data."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_mind_map/mcp-server-chart', 'description': 'Generate a mind map chart to organizes and presents information in a hierarchical structure with branches radiating from a central topic, such as, a diagram showing the relationship between a main topic and its subtopics.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'children': {'type': 'array', 'items': {'$ref': '#/properties/data/properties/children/items'}}}, 'required': ['name']}}}, 'required': ['name'], 'description': "Data for mind map chart, such as, { name: 'main topic', children: [{ name: 'topic 1', children: [{ name:'subtopic 1-1' }] }."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_network_graph/mcp-server-chart', 'description': 'Generate a network graph chart to show relationships (edges) between entities (nodes), such as, relationships between people in social networks.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {'nodes': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}, 'minItems': 1}, 'edges': {'type': 'array', 'items': {'type': 'object', 'properties': {'source': {'type': 'string'}, 'target': {'type': 'string'}, 'name': {'type': 'string', 'default': ''}}, 'required': ['source', 'target']}}}, 'required': ['nodes', 'edges'], 'description': "Data for network graph chart, such as, { nodes: [{ name: 'node1' }, { name: 'node2' }], edges: [{ source: 'node1', target: 'node2', name: 'edge1' }] }"}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_pie_chart/mcp-server-chart', 'description': 'Generate a pie chart to show the proportion of parts, such as, market share and budget allocation.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'category': {'type': 'string'}, 'value': {'type': 'number'}}, 'required': ['category', 'value']}, 'minItems': 1, 'description': "Data for pie chart, such as, [{ category: '分类一', value: 27 }]."}, 'innerRadius': {'type': 'number', 'default': 0, 'description': 'Set the innerRadius of pie chart, the value between 0 and 1. Set the pie chart as a donut chart. Set the value to 0.6 or number in [0 ,1] to enable it.'}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_radar_chart/mcp-server-chart', 'description': 'Generate a radar chart to display multidimensional data (four dimensions or more), such as, evaluate Huawei and Apple phones in terms of five dimensions: ease of use, functionality, camera, benchmark scores, and battery life.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'number'}, 'group': {'type': 'string'}}, 'required': ['name', 'value']}, 'minItems': 1, 'description': "Data for radar chart, such as, [{ name: 'Design', value: 70 }]."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_scatter_chart/mcp-server-chart', 'description': 'Generate a scatter chart to show the relationship between two variables, helps discover their relationship or trends, such as, the strength of correlation, data distribution patterns.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'x': {'type': 'number'}, 'y': {'type': 'number'}}, 'required': ['x', 'y']}, 'minItems': 1, 'description': 'Data for scatter chart, such as, [{ x: 10, y: 15 }].'}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}, 'axisXTitle': {'type': 'string', 'default': '', 'description': 'Set the x-axis title of chart.'}, 'axisYTitle': {'type': 'string', 'default': '', 'description': 'Set the y-axis title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_treemap_chart/mcp-server-chart', 'description': 'Generate a treemap chart to display hierarchical data and can intuitively show comparisons between items at the same level, such as, show disk space usage with treemap.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'number'}, 'children': {'type': 'array', 'items': {'$ref': '#/properties/data/items'}}}, 'required': ['name', 'value']}, 'minItems': 1, 'description': "Data for treemap chart, such as, [{ name: 'Design', value: 70, children: [{ name: 'Tech', value: 20 }] }]."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}, {'type': 'function', 'function': {'name': 'generate_word_cloud_chart/mcp-server-chart', 'description': 'Generate a word cloud chart to show word frequency or weight through text size variation, such as, analyzing common words in social media, reviews, or feedback.', 'parameters': {'type': 'object', 'properties': {'data': {'type': 'array', 'items': {'type': 'object', 'properties': {'text': {'type': 'string'}, 'value': {'type': 'number'}}, 'required': ['text', 'value']}, 'minItems': 1, 'description': "Data for word cloud chart, such as, [{ value: '4.272', text: '形成' }]."}, 'width': {'type': 'number', 'default': 600, 'description': 'Set the width of chart, default is 600.'}, 'height': {'type': 'number', 'default': 400, 'description': 'Set the height of chart, default is 400.'}, 'title': {'type': 'string', 'default': '', 'description': 'Set the title of chart.'}}, 'required': ['data'], '$schema': 'http://json-schema.org/draft-07/schema#'}}}]}



s1 = '123456789'

print(s1[:15])

ag2 = {"mcpServers": {"baidu-maps": {"url": "https://mcp.map.baidu.com/sse?ak=oqIwmwH7yNI9v1EQQXbTIoo3VB1hPsFk"}},"name": "baidu-maps","mcp_type": "sse","tools": []}







