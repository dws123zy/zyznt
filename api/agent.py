# _*_coding:utf-8 _*_

import time
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Response
import logging
from pydantic import BaseModel, Field
import os
from datetime import datetime
import json
import traceback
import random
import string
import copy
from typing import Union

# 本地模块
from db import my, mv
from data.data import tokenac, get_filter, get_zydict, get_rag
from mod.file import fileanalysis, partjx, zyembd


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
        sql = my.sqlc3(filterdata, 'agent', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('data'):
                    d['data'] = eval(d['data'])
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
                data2['data'] = str(data2['data'])
        except Exception as e:
            logger.error(f" agent新增时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 存入mysql数据库
        sql = my.sqlz(data2, 'agent')
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'创建向量数据库表成功{agentid}')
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}

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
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data2['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if data2.get('data'):
                data2['data'] = str(data2['data'])
        except Exception as e:
            logger.error(f" agent修改时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'appid': data2.get('appid', ''), 'agentid': agentid}

        # 存入mysql数据库
        sql = my.sqlg(data2, 'agent', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            # 禁止修改向量数据库中的表、字段、索引、bm25，只有删除重建
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}
        logger.warning(f'修改知识库失败{agentid}')
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

        # 组合检索项
        filterdata = {'agentid': agentid}

        # 存入mysql数据库
        sql = my.sqls('agent', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'删除向量数据库表、mysql数据库成功{agentid}')
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
        sql = my.sqlc3(filterdata, 'zydict', data.get('page'), data.get('limit'), '')
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
            # 禁止修改向量数据库中的表、字段、索引、bm25，只有删除重建
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

        # 组合检索项
        filterdata = {'dictid': dictid}

        # 存入mysql数据库
        sql = my.sqls('zydict', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'删除向量数据库表、mysql数据库成功{dictid}')
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'删除datadict数据字典失败{dictid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"datadict数据字典删除接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}
















