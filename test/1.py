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




