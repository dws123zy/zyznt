# _*_coding:utf-8 _*_
# from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import traceback
# from datetime import datetime
import random
import time
import logging
from logging.handlers import RotatingFileHandler
import coloredlogs

# 导入api子模块
from api import logon
from api import rag
from api import agent
from api import agentapi
from api import admin
from api import bi


'''定义日志程序'''


'''日志文件名函数'''

def logfilename():
    try:
        nowtime = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))  # 获取当前时间
        pid = os.getpid()  # 获取进程ID
        random_number = round(random.uniform(100, 999))  # 生成随机数
        return f'{nowtime}_{pid}_{random_number}'
    except Exception as e:
        print("处理日志文件名错误:")
        print(e)
        print(traceback.format_exc())
        return ''


'''配置日志文件名、大小、数量、错误日志多文件、颜色'''

try:
    # 创建处理器并设置格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 普通日志处理器（INFO及以上，自动轮转）
    file_handler = RotatingFileHandler(f'../log/zyzntai_{logfilename()}.log', maxBytes=10*1024*1024,
                                       backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 错误日志处理器（ERROR及以上，单独文件）
    error_file_handler = RotatingFileHandler(
        f'../log/znt_error{logfilename()}.log', maxBytes=1024*1024, backupCount=5, encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 一次性配置全局日志
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, error_file_handler, console_handler]
    )

    # 测试日志输出
    logger = logging.getLogger(__name__)

    coloredlogs.install(level='DEBUG', logger=logger,
                        fmt='%(asctime)s [%(levelname)s] %(message)s',
                        level_styles={
                            'debug': {'color': 'cyan'},
                            'info': {'color': 'green'},
                            'warning': {'color': 'yellow'},
                            'error': {'color': 'red'},
                            'critical': {'color': 'red', 'bold': True}
                        })

    logger.debug('调试信息（不可见）')
    logger.info('普通信息（出现在log文件和控制台）')
    logger.warning('警告信息（出现在log文件和控制台）')
    logger.error('错误信息（同时出现在正常log、错误log和控制台）')
    logger.critical('严重错误（同时出现在正常log、错误log和控制台）')

    logger.info('\n\n**********欢迎启动卓越智能体平台**********\n\n')
except Exception as e:
    print("日志配置错误:")
    print(e)
    print(traceback.format_exc())


'''初始化后端api框架Fast-app'''

app = FastAPI()

'''跨域支持'''

# 设置允许的源列表
origins = ['*']  # * 允许所有
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3000",
#     "https://your-frontend-domain.com",
# ]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的源列表
    allow_credentials=True,  # 允许携带凭证（如 cookies）
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)


'''api路由模块处理'''

app.include_router(logon.router)  # 引入登录、登出子路由
app.include_router(rag.router)  # 引入rag知识库相关子路由
app.include_router(agent.router)  # 引入agent智能体相关子路由
app.include_router(agentapi.router)  # 引入agent智能体交互运行相关子路由
app.include_router(admin.router)  # 引入admin管理功能相关子路由
app.include_router(bi.router)  # 引入智能数据bi管理功能相关子路由























