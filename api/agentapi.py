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


'''此模块用于agent智能体运行与交互，处理主要处理网络sse websocket post api接口交互，前端和api接口调用'''


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


'''******agent智能体运行******'''

'''agent智能体交互接口'''

@router.post("/agent/v1", tags=["agent智能体交互"])
def agent_run(mydata: cxzharg):
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
        logger.error(f"agent交互接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}






















