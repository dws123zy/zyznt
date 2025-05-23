# _*_coding:utf-8 _*_

import traceback
import logging
import time
import uuid
from datetime import datetime

from mod.llm import openai_llm
from data.data import get_zydict



'''此模块为智能体流的基础组件库'''


'''日志'''

logger = logging.getLogger(__name__)



'''start开始组件'''

def start_mod(indata, flowdata):
    try:
        '''
        初始化数据
        '''
        redata = {"system": {"user_input": "", "data": {}, "start_time": "", "end_time": "", "user": "", "session": ""},
                  "custom": {}}
        # 判断是否有会话id，如果有说明是老会话，id直接用,如果没有则生成
        if indata.get('session', ''):
            redata['system']['session'] = indata.get('session')
        else:
            redata['system']['session'] = f"flow-{str(int(round(time.time() * 1000)))}-{str(uuid.uuid4())[:8]}"
        # 保存api请求过来的data数据
        redata['system']['data'] = indata.get('data', {})
        # 生成开始时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        redata['system']['start_time'] = str(now)
        # 存入user用户信息
        redata['system']['user'] = indata.get('user', '')
        # 存入user_input
        redata['system']['user_input'] = indata.get('user_input', '')
        # 存入custom用户自定义数据
        redata['custom'] = flowdata.get('custom', {})
        # 返回执行状态和结果
        return {"code": "200", "msg": "success", "data": redata}

    except Exception as e:
        logger.error({"start_mod错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点start_mod执行错误，错误信息：{e}'}



'''end结束组件  end_mod'''

def end_mod(indata, flowdata):
    try:
        pass
    except Exception as e:
        logger.error({"end_mod错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点end_mod执行错误，错误信息：{e}'}




'''LLM组件  llm_mod'''

def llm_mod(indata, flowdata):
    try:
        # 调用LLM大模型
        msg = [{"role": "system", "content": flowdata.get('prompt', '')},
               {"role": "user", "content": indata.get('user_input', '')}]
        llmid = indata.get('llm')
        llmdata = get_zydict('llm', llmid)
        rdata = openai_llm(msg, llmdata.get('apikey', ''), llmdata.get('url', ''), llmdata.get('mod', ''),
                           tools=indata.get('tools', ''))
        return str(rdata)
    except Exception as e:
        logger.error({"llm_mod错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点llm_mod执行错误，错误信息：{e}'}



'''http  api接口调用组件   http_mod'''

def http_mod(indata, flowdata):
    try:
        pass
    except Exception as e:
        logger.error({"http_mod错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点http_mod执行错误，错误信息：{e}'}



'''if elif else 条件组件  if_mod'''

def if_mod(indata, flowdata):
    try:
        pass
    except Exception as e:
        logger.error({"if_mod错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点if_mod执行错误，错误信息：{e}'}


'''data数据处理组件  data_processing'''

def data_processing(indata, flowdata):
    try:
        pass
    except Exception as e:
        logger.error({"data_processing错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点data_processing执行错误，错误信息：{e}'}


'''code代码解释器 执行代码块返回结果  code_mod'''

def code_mod(indata, flowdata):
    try:
        pass
    except Exception as e:
        logger.error({"code_mod错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点code_mod执行错误，错误信息：{e}'}


'''note 注释模块，不用执行'''



'''数据组合功能函数，根据数据要求和入参配置，返回可以使用的输入参数合集'''

def param_data(all_data, flowdata):
    try:
        '''
        all_data 全局所有数据
        flowdata  节点配置数据
        '''
        redata = {}
        # 遍历flowdata中的input配置
        inputdata = flowdata.get('input', {})
        for f in inputdata:
            try:
                # 判断此变量的值是引用全局数据还是自定义输入
                if 'quote/' in str(inputdata.get(f, '')):  # 引用全局数据
                    vs = inputdata.get(f, '').replace('quote/', '')  # 原始值去掉引用字符
                    vlist = vs.split('/')  # 引用字段列表
                    vdata = ''  # 引用字段数据
                    nub = 0
                    for i in vlist:
                        try:
                            nub += 1  # 记录第几次循环
                            if nub == 1:  # 第一次循环时直接从alldata全局数据中取
                                vdata = all_data.get(i, '')
                            else:  # 非第一次
                                # 判断上次结束后的数据类型
                                if type(vdata) in [dict]:  # 字典数据走get
                                    vdata = vdata.get(i, '')
                                elif type(vdata) in [list]:  # 列表数据走index,i必须为整数
                                    vdata = vdata[int(i)]
                                elif type(vdata) in [str]:  # 字符串数据
                                    vdata = vdata[:int(i)]
                                else:
                                    pass
                        except Exception as e2:
                            logger.error({"取引用值错误:": e2})
                            logger.error(e2)
                            logger.error(traceback.format_exc())
                            return {"code": "502", "msg": "error", "data": f'获取数据错误，参数：{f}，值：{vs}'}
                    # 存入结果
                    redata[f] = vdata
                else:  # 自定义输入，直接用对应的值即可
                    redata[f] = inputdata.get(f, '')
            except Exception as e3:
                logger.error({"param_data错误:": e3})
                logger.error(e3)
                logger.error(traceback.format_exc())
                return {"code": "501", "msg": "error", "data": f'节点param_data执行错误，错误信息：{e3}'}
        # 返回结果
        return {"code": "200", "msg": "success", "data": redata}
    except Exception as e:
        logger.error({"param_data错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {"code": "501", "msg": "error", "data": f'节点param_data执行错误，错误信息：{e}'}

















