# _*_coding:utf-8 _*_

import time
from fastapi import APIRouter, File, UploadFile, Form, Depends
import logging
from pydantic import BaseModel, Field
import os
from datetime import datetime
import json
import traceback
import random
import string

# 本地模块
from db import my, mv
from data.data import tokenac, get_filter, get_zydict
from mod.file import fileanalysis


'''日志'''

logger = logging.getLogger(__name__)


'''全局参数'''

upload_dir = 'file/'


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


class dataarg2(BaseModel):  # data中的个性化参数
    ragid: str = Field('', description="知识库的id")


class cxzharg(publicarg):  # 通用查询类组合，公共+data
    data: cxdataarg



'''rag动态检索项查询接口'''

@router.post("/filter/{cmd}", tags=["rag动态检索项获取接口"])
def getfilter(mydata: publicarg, cmd: str):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}, cmd={cmd}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 处理cmd，返回对应的检索项数据
        if cmd in ['file', 'rag']:  # 按用户和cmd获取检索项
            filterdata = get_filter(cmd, data_dict.get('user', ''))
            return {"msg": "success", "code": "200", "data": {"filter": filterdata}}
        elif cmd in ['cs']:  # 按cmd获取检索项
            filterdata = get_filter(cmd)
            return {"msg": "success", "code": "200", "data": {"filter": filterdata}}
        else:  # cmd错误，无此检索项
            return {"msg": "cmd is error", "code": "404", "data": ""}

    except Exception as e:
        logger.error(f"rag动态检索项获取接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''rag通用新增、修改、删除'''

class ragdataarg3(BaseModel):
    ragid: str = Field('', description="知识库的id,修改删除时必填")
    data: dict = Field({}, description="增加或修改的数据，增加修改时必填")

class ragzgsarg(publicarg):  # 通用增加和修改组合，公共+data
    data: ragdataarg3


'''******知识库管理******'''

'''rag查询接口'''

@router.post("/rag/get", tags=["RAG知识库查询"])
def ragzskcx(mydata: cxzharg):
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
        sql = my.sqlc3(filterdata, 'rag', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('split'):
                    d['split'] = json.loads(d['split'])
                if d.get('search'):
                    d['search'] = json.loads(d['search'])
            except Exception as e:
                logger.error(f" rag查询时json.loads出错: {e}")
                logger.error(traceback.format_exc())

        # 获取表单数据form
        formdata = get_zydict('form', 'rag_form')

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit'),
                         "form": formdata}}
    except Exception as e:
        logger.error(f"rag查询接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''rag新增接口'''

@router.post("/rag/add", tags=["RAG知识库新增"])
def ragzskxz(mydata: ragzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要新增的配置数据
        data = data_dict.get('data', {})
        ragdata = data.get('data', {})
        # 生成ragid
        ragid  = 'rag'+str(int(time.time()))+''.join(random.choice(string.digits) for _ in range(3))
        ragdata['ragid'] = ragid
        ragdata['tb'] = ragid  # 向量表与ragid同值
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        ragdata['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if ragdata.get('split'):
                ragdata['split'] = str(ragdata['split'])
            if ragdata.get('search'):
                ragdata['search'] = str(ragdata['search'])
        except Exception as e:
            logger.error(f" rag新增时json转str出错: {e}")
            logger.error(traceback.format_exc())

        # 存入mysql数据库
        sql = my.sqlz(ragdata, 'rag')
        jg = my.msqlzsg(sql)
        if jg:
            # 创建向量数据库中的表、字段、索引、bm25原始文本字段必须'enable_analyzer':True 才可
            tbdata = ragdata.get('tbdata', 'm_tbdata')
            # 从数据字典中拿到tbdata的配置数据
            tb_dict = get_zydict('db', tbdata).get('tbdata', '{}')
            dim = 1024
            if ragdata.get('embedding'):
                dim = get_zydict('embd', ragdata.get('embedding').split('/')[1]).get('dim', 1024)
            if tb_dict:
                schema, index_param = mv.schema_create(tb_dict, dim)
                logger.warning(f'创建向量数据库表参数={schema}, \n\n\n{index_param}')
                if schema and index_param:
                    vjg = mv.create_collections(schema, ragid, index_param)
                    print('vjg=', vjg)
                    if vjg:
                        logger.warning(f'创建向量数据库表成功{ragid}')
                        # 返回结果
                        return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'创建知识库失败{ragid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"rag新增接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''rag修改接口'''

@router.put("/rag/update", tags=["RAG知识库修改"])
def ragzskxg(mydata: ragzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要修改的数据
        data = data_dict.get('data', {})
        ragdata = data.get('data', {})
        # 生成ragid
        ragid  = data.get('ragid', '')
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        ragdata['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if ragdata.get('split'):
                ragdata['split'] = str(d['split'])
            if ragdata.get('search'):
                ragdata['search'] = str(d['search'])
        except Exception as e:
            logger.error(f" rag修改时json转str出错: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'appid': ragdata.get('appid', ''), 'ragid': ragid}

        # 存入mysql数据库
        sql = my.sqlg(ragdata, 'rag', filterdata)
        jg = my.msqlzsg(sql)

        # 禁止修改向量数据库中的表、字段、索引、bm25，只有删除重建
        # 返回结果
        return {"msg": "success", "code": "200", "data": ''}
    except Exception as e:
        logger.error(f"rag修改接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''rag删除接口'''


@router.delete("/rag/del", tags=["RAG知识库删除"])
def ragzsksc(mydata: ragzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 获取ragid
        ragid = data_dict.get('data', {}).get('ragid', '')

        # 组合检索项
        filterdata = {'ragid': ragid}

        # 存入mysql数据库
        sql = my.sqls('rag', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            # 删除向量数据库中的表、字段
            vjg = mv.drop_collections(ragid)
            if vjg:
                logger.warning(f'删除向量数据库表、mysql数据库成功{ragid}')
                # 返回结果
                return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'删除知识库失败{ragid}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"rag删除接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''******文件管理******'''


'''文件管理通用新增、修改、删除'''

class filedataarg3(BaseModel):
    fileid: str = Field('', description="文件id,修改删除时必填")
    data: dict = Field({}, description="增加或修改的数据，增加修改时必填")

class filezgsarg(publicarg):  # 通用增加和修改组合，公共+data
    data: filedataarg3


'''文件查询接口'''

@router.post("/file/get", tags=["RAG文件查询"])
def filecx(mydata: cxzharg):
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
        sql = my.sqlc3(filterdata, 'file', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('split'):
                    d['split'] = json.loads(d['split'])
            except Exception as e:
                logger.error(f" 文件查询时json.loads出错: {e}")
                logger.error(traceback.format_exc())

        # 获取表头
        tbdata = get_zydict('tb', 'file_tb')
        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit'), "tb": tbdata}}
    except Exception as e:
        logger.error(f"文件查询接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''文件上传增加接口'''

@router.post("/file/add", tags=["RAG文件上传"])
async def upload_files(mydata: str=Form(''), files: list[UploadFile] = File(...)):
    try:
        data_dict = json.loads(mydata)
        logger.warning(f'收到的请求数据={data_dict}')
        results = []

        # 组合文件路径
        fdir = upload_dir + str(data_dict.get('appid', ''))+'/'+str(data_dict.get('ragid', ''))
        os.makedirs(fdir, exist_ok=True)
        for file in files:
            try:
                # 为每个文件创建保存路径
                file_path = os.path.join(fdir, file.filename)

                # 检查文件是否已存在
                if os.path.exists(file_path):
                    raise HTTPException(status_code=400, detail=f"文件 {file.filename} 已存在")

                # 实时写入文件
                with open(file_path, "wb") as buffer:
                    # 分块读取并写入文件
                    while chunk := await file.read(1024 * 1024):  # 每次读取1MB
                        buffer.write(chunk)

                results.append({
                    "filename": file.filename,
                    "size": str(round(os.path.getsize(file_path)/1024, 2))+'KB',
                    "format": file.content_type,
                    "status": "success"
                })

            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": str(e),
                    "status": "failed"
                })
        logger.warning(f'上传文件结果={results}')
        # 遍历文件列表，把上传成功的存入mysql数据库的fiel表中
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 获取当前时间
        for f in results:
            if f['status'] == 'success':
                # 随机选择字符并拼接成字符串
                characters = string.ascii_letters + string.digits
                fileid = str(int(time.time()*1000))+''.join(random.choice(characters) for _ in range(3))
                ragid = data_dict.get('data', {}).get('ragid') if data_dict.get('data', {}).get('ragid') else ''
                filedata = {'name': f.get('filename', ''), 'size': f.get('size', 0), 'time': nowtime,
                            'metadata': str({"format": f.get('format', '')}), 'appid': data_dict.get('appid', ''),
                            'user': data_dict.get('user', ''), 'ragid': ragid, 'fileid': fileid,
                            'type': data_dict.get('type', 'file'), 'split': str(data_dict.get("split", ''))}
                # 组合sql语句
                sql = my.sql3sz(filedata, 'file')
                jg = my.msqlzsg(sql)  # 执行sql语句，增加文件到数据库
                logger.warning(f'文件上传入库结果={jg}，sql={sql}')

        return {"msg": "文件上传完成", "code": "200", "data": results}
    except Exception as e:
        logger.error(f"文件上传时出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''文件修改接口'''

@router.put("/file/update", tags=["RAG文件修改"])
def ragfilexg(mydata: filezgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要修改的数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})  # data中的data
        # 获取文件id
        fileid  = data.get('fileid', '')
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data2['time'] = nowtime

        # 把部分字段值的json字符串转字典
        try:
            if data2.get('split'):
                data2['split'] = json.loads(data2['split'])
        except Exception as e:
            logger.error(f" rag修改时json转str出错: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'appid': data2.get('appid', ''), 'fileid': fileid}

        # 存入mysql数据库
        sql = my.sqlg(data2, 'file', filterdata)
        jg = my.msqlzsg(sql)

        # 修改向量数据库中的表、字段、索引、bm25

        # 返回结果
        return {"msg": "success", "code": "200", "data": ''}
    except Exception as e:
        logger.error(f"文件修改接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''文件删除接口'''

@router.delete("/file/del", tags=["RAG文件删除"])
def ragzsksc(mydata: filezgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 获取数据id
        fileid = data_dict.get('data', {}).get('fileid', '')

        # 组合检索项
        filterdata = {'fileid': fileid}

        # 存入mysql数据库
        sql = my.sqls('file', filterdata)
        jg = my.msqlzsg(sql)

        # 删除向量数据库中的表、字段、索引、bm25

        # 返回结果
        return {"msg": "success", "code": "200", "data": ''}
    except Exception as e:
        logger.error(f"文件删除接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}




'''******文件解析、向量化******'''


class filedataarg4(BaseModel):
    filedata: list[dict] = Field(frozen=True, description="要解析的文件数据[{文件数据1},{文件数据2}]，可以多个，必填")
    ragdata: dict = Field(frozen=True, description="要解析的文件所属知识库的数据，必填")

class filejxarg(publicarg):  # 通用增加和修改组合，公共+data
    data: filedataarg4



'''文件解析接口'''

@router.post("/file/analysis", tags=["文件解析"])
def filejx(mydata: filejxarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})
        # 检验文件状态为未解析，否则去除对应文件并返回错误

        # 调用解析模块执行解析
        jglist = fileanalysis(data2.get('filedata', []), data2.get('ragdata', {}))

        # 把解析中的文件状态写入mysql，状态改为解析中

        # 返回发起解析的结果
        return {"msg": "success", "code": "200", "data": ''}
    except Exception as e:
        logger.error(f"文件解析接口出错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''向量块管理，增删改查'''




'''rag知识搜索功能，向量计算'''





