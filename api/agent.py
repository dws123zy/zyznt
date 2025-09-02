# _*_coding:utf-8 _*_

import time
from fastapi import APIRouter  #, File, UploadFile, Form, Depends, HTTPException, Response
import logging
from pydantic import BaseModel, Field
from typing import Union, Any
# import os
# from datetime import datetime
# import json
import traceback
import random
import string
# import copy
# from typing import Union
from urllib.parse import urlparse, parse_qs

# 本地模块
from db import my  #, mv
from data.data import tokenac, get_zydict, loadzydict, loadagent, get_rag, get_agent
# from mod.file import fileanalysis, partjx, zyembd
from mod.zymcp import mcp_client
from mod.llm import openai_llm


'''此模块用于agent智能体、智能流数据配置与管理'''


'''日志'''

logger = logging.getLogger(__name__)


'''定义子模块路由'''

router = APIRouter()


'''统一总入参格式类定义'''

class publicarg(BaseModel):  # 公共参数，所有接口必传
    user: str = Field(frozen=True, description="用户名")
    appid: str = Field(frozen=True, description="企业id")
    token: str = Field(frozen=True, description="验证token")
    time: str = Field(frozen=True, description="当前时间戳,精确到秒，也就是10位")
    # data: dict = Field({}, description="交互数据，")


class cxdataarg(BaseModel):  # 查询时data中的标准参数
    filter: dict = Field({}, description="查询条件,检索项，以键值对方式传过来")
    limit: int = Field(200, description="每页显示的数量")
    page: int = Field(1, description="页码，第几页")


class cxzharg(publicarg):  # 通用查询类组合，公共+data
    data: cxdataarg


'''agent通用新增、修改、删除'''

class agentdataarg3(BaseModel):
    agentid: str = Field('', description="智能体的id,修改删除时必填")
    data: dict = Field({}, description="增加或修改的数据，增加修改时必填")

class agentzgsarg(publicarg):  # 通用增加和修改组合，公共+data
    data: agentdataarg3


'''******agent智能体管理******'''

'''agent智能体查询接口'''

@router.post("/agent/get", tags=["agent智能体查询"])
def agent_get(mydata: cxzharg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data = data_dict.get('data', {})

        # 写sql
        filterdata = data.get('filter', {})
        if not filterdata.get('appid', ''):  # 如果检索项中没有appid，则使用当前user的appid
            filterdata['appid'] = data_dict.get('appid', '')
        sql = my.sqlc3like(filterdata, 'agent', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('data'):
                    if "{" in str(d.get('data')):
                        d['data'] = eval(d['data'])
                    else:
                        d['data'] = my.safe_base64_to_list(d['data'])
            except Exception as e:
                logger.error(f" agent查询时转字典错误: {e}")
                logger.error(traceback.format_exc())

        # 获取表单数据form
        formdata = get_zydict('form', 'agent_form')

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit'),
                         "form": formdata}}
    except Exception as e:
        logger.error(f"agent查询接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''agent智能体新增接口'''

@router.post("/agent/add", tags=["agent智能体新增"])
def agent_add(mydata: agentzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要新增的配置数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})
        # 生成ragid
        agentid  = 'agent'+str(int(time.time()))+''.join(random.choice(string.digits) for _ in range(3))
        data2['agentid'] = agentid
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data2['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if data2.get('data'):
                b64rdata = my.list_to_safe_base64(data2['data'])
                data2['data'] = b64rdata
        except Exception as e:
            logger.error(f" agent新增时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 存入mysql数据库
        sql = my.sqlz(data2, 'agent')
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'存入数据库成功{agentid}')
            loadagent()  # 更新agent数据到内存
            # 返回结果
            return {"msg": "success", "code": "200", "data": {"agentid": agentid}}

        # 返回结果
        logger.warning(f'创建知识库失败{agentid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"agent新增接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''agent智能体修改接口'''

@router.put("/agent/update", tags=["agent智能体修改"])
def agent_update(mydata: agentzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要修改的数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})
        # 获取agentid
        agentid  = data.get('agentid', '')
        if not agentid:
            agentid = data2.get('agentid', '')
            if not agentid:
                logger.warning(f'agentid不能为空')
                return {"msg": "agentid不能为空", "code": "151", "data": ""}
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data2['time'] = nowtime

        # data2中去除id字段，因为数据库不允许改id
        if 'id' in data2:
            del data2['id']

        # 把部分字段值的字典转字符
        try:
            if data2.get('data'):
                b64rdata = my.list_to_safe_base64(data2['data'])
                data2['data'] = b64rdata
        except Exception as e:
            logger.error(f" agent修改时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'appid': data2.get('appid', ''), 'agentid': agentid}

        # 存入mysql数据库
        sql = my.sqlg(data2, 'agent', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            loadagent()  # 更新agent数据到内存
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}
        logger.warning(f'修改智能体失败{agentid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"agent修改接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''agent智能体删除接口'''

@router.delete("/agent/del", tags=["agent智能体删除"])
def agent_del(mydata: agentzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 获取ragid
        agentid = data_dict.get('data', {}).get('agentid', '')
        if not agentid:
            return {"msg": "agentid不正确", "code": "151", "data": ""}

        # 组合检索项
        filterdata = {'agentid': agentid}

        # 存入mysql数据库
        sql = my.sqls('agent', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            loadagent()  # 更新agent数据到内存
            logger.warning(f'删除数据库表、mysql数据库成功{agentid}')
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'删除知识库失败{agentid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"agent删除接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}



'''数据字典管理'''



'''datadict数据字典通用新增、修改、删除'''

class datadictarg3(BaseModel):
    dictid: str = Field('', description="数据字典的id,修改删除时必填")
    data: dict = Field({}, description="增加或修改的数据，增加修改时必填")

class zydictzgsarg(publicarg):  # 通用增加和修改组合，公共+data
    data: datadictarg3


'''datadict数据字典查询接口'''

@router.post("/datadict/get", tags=["数据字典查询"])
def datadict_get(mydata: cxzharg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data = data_dict.get('data', {})

        # 写sql
        filterdata = data.get('filter', {})
        if not filterdata.get('appid', ''):  # 如果检索项中没有appid，则使用当前user的appid
            filterdata['appid'] = data_dict.get('appid', '')
        sql = my.sqlc3like(filterdata, 'zydict', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('data'):
                    d['data'] = eval(d['data'])
            except Exception as e:
                logger.error(f" datadict数据字典查询时转字典错误: {e}")
                logger.error(traceback.format_exc())

        # 获取表单数据form
        menu_data = get_zydict('menu', 'adminmenu')

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit'),
                         "menu_data": menu_data}}
    except Exception as e:
        logger.error(f"datadict数据字典查询接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''数据字典新增接口'''

@router.post("/datadict/add", tags=["数据字典新增"])
def datadict_add(mydata: zydictzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要新增的配置数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})
        # 生成dictid
        dictid  = 'dict'+str(int(time.time()))+''.join(random.choice(string.digits) for _ in range(3))
        data2['dictid'] = dictid
        # 获取当前时间
        # nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # data2['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if data2.get('data'):
                data2['data'] = str(data2['data'])
        except Exception as e:
            logger.error(f" datadict数据字典新增时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 存入mysql数据库
        sql = my.sqlz(data2, 'zydict')
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'创建datadict数据字典成功{dictid}')
            loadzydict()  # 更新datadict数据到内存
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'创建datadict数据字典失败{dictid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"datadict数据字典新增接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''数据字典修改接口'''

@router.put("/datadict/update", tags=["数据字典修改"])
def datadict_update(mydata: zydictzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要修改的数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})
        # 获取dictid
        dictid  = data.get('dictid', '')
        # 获取当前时间
        # nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # data2['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if data2.get('data'):
                data2['data'] = str(data2['data'])
        except Exception as e:
            logger.error(f" datadict数据字典修改时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'appid': data2.get('appid', ''), 'dictid': dictid}

        # 存入mysql数据库
        sql = my.sqlg(data2, 'zydict', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            loadzydict()  # 更新datadict数据到内存
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}
        logger.warning(f'修改datadict数据字典失败{dictid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"datadict数据字典修改接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''datadict数据字典删除接口'''

@router.delete("/datadict/del", tags=["数据字典删除"])
def datadict_del(mydata: zydictzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 获取ragid
        dictid = data_dict.get('data', {}).get('dictid', '')
        if not dictid:
            return {"msg": "dictid不正确", "code": "151", "data": ""}

        # 组合检索项
        filterdata = {'dictid': dictid}

        # 存入mysql数据库
        sql = my.sqls('zydict', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'删除向量数据库表、mysql数据库成功{dictid}')
            loadzydict()  # 更新datadict数据到内存
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'删除datadict数据字典失败{dictid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"datadict数据字典删除接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}



'''mcp 服务管理'''

'''mcp统一总入参格式类定义'''


class mcppublicarg(BaseModel):  # 公共参数，所有接口必传
    user: str = Field(frozen=True, description="用户名")
    appid: str = Field(frozen=True, description="企业id")
    token: str = Field(frozen=True, description="验证token")
    time: str = Field(frozen=True, description="当前时间戳,精确到秒，也就是10位")
    data: Any = Field(frozen=True, description="mcp数据data")


'''mcp工具列表获取接口'''

@router.post("/mcp/tools/get", tags=["mcp tools获取"])
async def mcp_tools_get(mydata: mcppublicarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        mcp_data = data_dict.get('data', {})
        # 调用mcp模块工具获取工具列表
        tools_data = await mcp_client(mcp_data,  'list_tool')
        if tools_data:
            logger.warning(f'mcp工具列表获取成功')
            mcp_server_name = list(mcp_data.get('mcpServers', {}).keys())[0]
            # 改写工具中的name，加上/mcp server name，判断是否有rag、agent的mcp服务，如果有，修改下工具描述
            for tool in tools_data:
                # 增加服务名
                # tool['function']['name'] = f"{tool['function']['name']}/{mcp_server_name}"
                # 增加rag agent工具描述
                if 'type=rag' in str(mcp_data):
                    # 获取mcp服务中的url
                    server_info = next(iter(mcp_data["mcpServers"].values()))
                    mcp_url = server_info["url"]
                    # 获取url中的ragid
                    parsed_url = urlparse(mcp_url)
                    query_params = parse_qs(parsed_url.query)
                    ragid = query_params.get('ragid', [''])[0]
                    # 获取描述
                    rag_data = get_rag(ragid)
                    description = rag_data.get('mcp', {}).get('description', '')

                    tool['function']['description'] = description
                elif 'type=agent' in str(mcp_data):
                    # 获取mcp服务中的url
                    server_info = next(iter(mcp_data["mcpServers"].values()))
                    mcp_url = server_info["url"]
                    # 获取url中的agentid
                    parsed_url = urlparse(mcp_url)
                    query_params = parse_qs(parsed_url.query)
                    agentid = query_params.get('agentid', [''])[0]
                    # 获取描述
                    agent_data = get_agent(agentid)
                    description = agent_data.get('mcp', {}).get('description', '')

                    tool['function']['description'] = description
            return {"msg": "success", "code": "200", "data": tools_data}
        else:
            return {"msg": "mcp error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"datadict数据字典查询接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''LLM 服务管理'''

'''LLM统一总入参格式类定义'''


class llmpublicarg(BaseModel):  # 公共参数，所有接口必传
    llm: str = Field(frozen=True, description="llm模型id")
    msg: Any = Field(frozen=True, description="与大模型交互的msg数据，示例[{'role': 'user','content': '你好'}]")


class llmzharg(publicarg):  # 通用查询类组合，公共+data
    data: llmpublicarg


'''llm交互接口'''

@router.post("/llm/msg", tags=["llm交互接口"])
def llm_msg_get(mydata: llmzharg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data = data_dict.get('data', {})
        msg = data.get('msg', [])  # 获取msg数据
        # 拿到llm模型数据
        llmdata = get_zydict('llm', data.get('llm', ''))
        if llmdata and msg:
            logger.warning(f'开始调用llm模型')
            sdk = llmdata.get('sdk', 'openai')
            if sdk == 'openai':
                llm_text = openai_llm(msg, llmdata.get('apikey', ''), llmdata.get('url', ''), llmdata.get('module', ''))
            else:
                logger.warning(f'不支持的llm模型={sdk}')
                return {"msg": "llm type error", "code": "151", "data": ''}
            return {"msg": "success", "code": "200", "data": llm_text}
        else:
            return {"msg": "llm error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"llm交互接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}







