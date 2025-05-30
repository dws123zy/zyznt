# _*_coding:utf-8 _*_

import time
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import logging
from pydantic import BaseModel, Field
import traceback
import asyncio

# 本地模块
from data.data import apikeyac, get_agent
from mod.agent_run import agent_stream, agent_flow_start



'''此模块用于agent智能体运行与交互，处理主要处理网络sse websocket post api接口交互，前端和api接口调用*'''


'''日志'''

logger = logging.getLogger(__name__)


'''定义子模块路由'''

router = APIRouter()


'''统一总入参格式类定义'''

class agentpublicarg(BaseModel):  # 公共参数，所有接口必传
    user: str = Field('visitor', description="用户名,默认游客visitor")
    agentid: str = Field(frozen=True, description="对话的智能体id")
    apikey: str = Field(frozen=True, description="安全验证")
    session: str = Field('', description="当前对话id")
    msg: list = Field(frozen=True, description="对话列表")
    stream: bool = Field(False, description="流式交互")
    data: dict = Field({}, description="自定义数据")


'''******agent智能体运行******'''

'''agent智能体交互接口'''

@router.post("/agent/v1", tags=["agent智能体交互，支持流式sse与非流式"])
async def agent_stream_post(request: Request, mydata: agentpublicarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        appid = get_agent(data_dict.get('agentid', {})).get('appid', '')
        if not apikeyac(data_dict.get('apikey', ''), appid):
            logger.warning(f'apikey验证失败')
            return {"msg": "apikey或agent验证失败", "code": "403", "data": ""}

        # 判断是否流式返回
        if data_dict.get('stream', False):
            logger.warning(f'流式返回')
            return StreamingResponse(
                agent_stream(request, data_dict),  # 传递 request 参数
                media_type="text/event-stream"
            )
        else:
            logger.warning(f'非流式返回')
            rdata = ''
            async for a in agent_stream(request, data_dict):
                rdata = rdata+str(a)
            return {"msg": "success", "code": "200", "data": rdata}
    except Exception as e:
        logger.error(f"agent交互接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''EventSource原生流式接口'''

@router.get("/agent/event", response_class=StreamingResponse, tags=["agent智能体event-sse交互"])
async def agent_event(request: Request, agentid: str='', apikey: str='', user: str='', session: str='', msg: str='[]'):
    try:
        data_dict = {
            'agentid': agentid,  # 智能体id
            'apikey': apikey,
            'user': user,
            'msg': eval(msg),
            'session': session  # 会话id
        }
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        appid = get_agent(data_dict.get('agentid', {})).get('appid', '')
        if not apikeyac(data_dict.get('apikey', ''), appid):
            logger.warning(f'apikey验证失败')
            rdata = {"msg": "apikey或agent验证失败", "code": "403", "data": ""}
            return StreamingResponse(
            f"data：{rdata}",
            media_type="text/event-stream")
        # 流式响应
        async def event_generator():
            async for chunk in agent_stream(request, data_dict):
                yield f"data: {chunk}\n\n"
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"agent_event错误: {e}")
        print(traceback.format_exc())
        return StreamingResponse(
            f"data: msg:error, 出现错误 \n\n",  # 传递 request 参数
            media_type="text/event-stream"
        )


'''agent flow智能体流交互接口'''

@router.post("/agent/flow", tags=["agent flow智能体交互"])
async def agent_flow_post(request: Request, mydata: agentpublicarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        appid = get_agent(data_dict.get('agentid', {})).get('appid', '')
        if not apikeyac(data_dict.get('apikey', ''), appid):
            logger.warning(f'apikey验证失败')
            return {"msg": "apikey或agent验证失败", "code": "403", "data": ""}

        # 判断是否流式返回
        if data_dict.get('stream', False):
            logger.warning(f'流式返回，暂不支持，开发中')
            return StreamingResponse(
                agent_flow_start(data_dict),  # 传递 request 参数
                media_type="text/event-stream"
            )
        else:
            logger.warning(f'非流式返回')
            rdata = agent_flow_start(data_dict)
            return {"msg": "success", "code": "200", "data": rdata}
    except Exception as e:
        logger.error(f"agent交互接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}













