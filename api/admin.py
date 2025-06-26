# _*_coding:utf-8 _*_

import time
from fastapi import APIRouter
import logging
from pydantic import BaseModel, Field
import traceback

# 本地模块
from db import my
from data.data import tokenac, get_zydict


'''此模块用于rag知识库数据配置、查询与管理'''


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


class reportarg(BaseModel):  # 查询时data中的标准参数
    filter: dict = Field({}, description="查询条件,检索项，以键值对方式传过来")
    cmd: str = Field(frozen=True, description="报表命令")
    limit: int = Field(200, description="每页显示的数量")
    page: int = Field(1, description="页码，第几页")


class report(publicarg):  # 通用查询类组合，公共+data
    data: reportarg



'''我的统计7天统计接口'''

@router.post("/report", tags=["报表统计接口"])
def report_get(mydata: report):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})
        # 处理cmd，返回对应的检索项数据
        cmd = data2.get('cmd', '')
        if cmd in ['7day']:  # 我的统计
            report_data = get_7day(data2)
            return {"msg": "success", "code": "200", "data": report_data}
        elif cmd in ['cs']:  # 其它报表统计
            report_data = get_7day(data2)
            return {"msg": "success", "code": "200", "data": report_data}
        else:  # cmd错误，无此检索项
            return {"msg": "cmd is error", "code": "404", "data": ""}

    except Exception as e:
        logger.error(f"rag动态检索项获取接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''报表统计函数集'''


'''我的统计'''

def get_7day(data2):
    try:
        cmd = data2.get('cmd', '')
        sqlcmd = get_zydict('report', cmd).get('sqla', '')
        logger.warning(f'sqlcmd={sqlcmd}, cmd={cmd}')
        datac = my.msqlc(sqlcmd)  # 查询数据
        logger.warning(f'get_7day数据统计={datac}')
        # 获取今天日期取出对应的数据
        today = time.strftime("%Y-%m-%d", time.localtime())
        # 从datac中拿出今天的数据
        today_data = {'chat': 0, 'user': 0, 'chat_7day': 0}
        # 7天数据转为图表格式的数据
        day7_data = {'datas':[], 'chats': [], 'users': []}
        for d in datac:
            # 处理当天组合
            if d.get('date', '') in [today]:
                today_data['chat'] = d.get('chat', 0)
                today_data['user'] = d.get('user', 0)
            # 计算7天对话数据总和
            today_data['chat_7day'] += d.get('chat', 0)
            # 处理7天组合
            day7_data['datas'] = day7_data['datas'] + [d.get('date', '')]
            day7_data['chats'] = day7_data['chats'] + [d.get('chat', 0)]
            day7_data['users'] = day7_data['users'] + [d.get('user', 0)]

        # 组合数据
        report_data = {'today': today_data, 'day7': day7_data}
        # 返回数据
        return report_data
    except Exception as e:
        logger.error(f"我的统计错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}







































