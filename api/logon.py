# _*_coding:utf-8 _*_

import time
from fastapi import APIRouter
import logging
from pydantic import BaseModel, Field
from captcha.image import ImageCaptcha
import random
from PIL import Image
import os
import io
import base64
import string
import traceback

from mod.tool import openfile, writefile  # 文件打开和写入
from data.data import logonac


'''此模块用于用户登录管理'''


'''日志'''

logger = logging.getLogger(__name__)


'''人机验证开关配置'''

verify = eval(openfile('../file/conf.txt')).get('verify', 1)


'''人机验证码生成'''

def generate_math_captcha():
    try:
        # 生成简单的数学题
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        operator = random.choice(['+', '-', '*'])

        if operator == '+':
            answer = a + b
        elif operator == '-':
            answer = a - b
        else:
            answer = a * b

        question = f"{a} {operator} {b} = ?"

        # 创建验证码图像
        image = ImageCaptcha(width=200, height=100)
        data = image.generate(question)
        img = Image.open(data)

        # # 确保 png 文件夹存在
        # os.makedirs("png", exist_ok=True)
        #
        # # 保存图片到本地
        # img_filename = f"png/math_captcha_{a}{operator}{b}.png"
        # img.save(img_filename)
        # print(f"验证码图片已保存到: {img_filename}")

        # 将图片转换为 Base64 编码
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = 'data:image/png;base64,' + base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 生成问题id
        characters = string.ascii_letters + string.digits
        # 随机选择字符并拼接成字符串
        imgid = str(int(time.time()))+''.join(random.choice(characters) for _ in range(6))

        # 存入本地文件
        writefile(f'../file/img/{imgid}.txt', str(answer))

        # 返回 Base64 编码的图片、问题和答案
        return img_base64, question, str(answer), imgid
    except Exception as e:
        logger.error(f"生成验证码时出错: {e}")
        return '', '', '', ''




'''定义子模块路由'''

router = APIRouter()


'''
返回的影响标准

成功
{'msg': 'success', 'code': '200', 'data': ''}
失败
{'msg': 'error', 'code': '404', 'data': ''}

BaseModel

frozen  是否必填，如果非必填，在这个位值给个默认值即可
description 描述
'''


'''获取验证图片传入参数定义'''

class verifyarg(BaseModel):
    cmd: str = Field(frozen=True, description="值固定verify")


'''验证码图片获取  verify '''

@router.post("/verify", tags = ["验证码图片获取"])
def img_verify(mydata: verifyarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        if data_dict['cmd'] in ['verify']:
            if verify:
                img_base64, question, answer, imgid = generate_math_captcha()
                item = {'msg': 'success', 'code': '200', 'data': {'img': img_base64, 'imgid': imgid}}
                return item
            else:  # 验证码关闭,返回空字典
                item = {'msg': 'success', 'code': '200', 'data': {}}
                return item
        else:
            item = {'msg': 'error', 'code': '404', 'data': ''}
            return item
    except Exception as e:
        logger.error(f"验证码获取时出错: {e}")
        logger.error(traceback.format_exc())
        item = {'msg': 'error', 'code': '501', 'data': ''}
        return item


'''用户登录入参定义'''

class loginarg(BaseModel):
    user: str = Field(frozen=True, description="用户名")
    password: str = Field(frozen=True, description="密码")
    verify: str = Field('', description="验证码")
    time: str = Field(frozen=True, description="当前时间戳,精确到秒，也就是10位")
    imgid: str = Field('', description="验证码图片id")


'''用户登录'''

@router.post("/logon/{cmd}", tags=["用户登录登出 in/out"])
def logon(mydata: loginarg, cmd: str):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}, cmd={cmd}')
        if cmd in ['in']:
            jg = logonac(data_dict)  # 登录验证
            return jg
        elif cmd in ['out'] and data_dict.get('user'):  # 登出
            return {"msg": "success", "code": "200", "data": ""}
        else:
            return {"msg": "error", "code": "403", "data": ""}

    except Exception as e:
        logger.error(f"用户登录时出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}











