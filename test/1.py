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














