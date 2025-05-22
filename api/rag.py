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
from mod.file import fileanalysis, partjx, zyembd, file_read


'''此模块用于rag知识库数据配置、查询与管理'''


'''日志'''

logger = logging.getLogger(__name__)


'''全局参数'''

upload_dir = '../file/'


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


表单、表头、检索项统一定义标准：

字段 ： field
显示文本：text
是否显示：show  值为f时不显示，其它都显示
是否必填：required  值为t时必填，其它都不是必填
是否可修改：update  值为f时不可修改，其它可修改
类型：type（select下拉，文本框text、输入框input、split rag的文本分段、search rag的向量检索、）
默认值：default
字段的描述：placeholder


下拉选项：options
下拉显示：label
下拉值：value

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

@router.post("/filter/{cmd}", tags=["动态检索项获取接口,'file 文件', 'rag知识库', 'part文本段', agent智能体"])
def getfilter(mydata: publicarg, cmd: str):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}, cmd={cmd}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 处理cmd，返回对应的检索项数据
        if cmd in ['file', 'rag', 'part']:  # 按用户和cmd获取检索项
            filterdata = get_filter(cmd, data_dict.get('user', ''))
            return {"msg": "success", "code": "200", "data": {"filter": filterdata}}
        elif cmd in ['cs']:  # 按cmd获取检索项
            filterdata = get_filter(cmd)
            return {"msg": "success", "code": "200", "data": {"filter": filterdata}}
        else:  # cmd错误，无此检索项
            return {"msg": "cmd is error", "code": "404", "data": ""}

    except Exception as e:
        logger.error(f"rag动态检索项获取接口错误: {e}")
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
def rag_get(mydata: cxzharg):
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
                    d['split'] = eval(d['split'])
                if d.get('search'):
                    d['search'] = eval(d['search'])
            except Exception as e:
                logger.error(f" rag查询时转字典错误: {e}")
                logger.error(traceback.format_exc())

        # 获取表单数据form
        formdata = get_zydict('form', 'rag_form')

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit'),
                         "form": formdata}}
    except Exception as e:
        logger.error(f"rag查询接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''rag新增接口'''

@router.post("/rag/add", tags=["RAG知识库新增"])
def rag_add(mydata: ragzgsarg):
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
            logger.error(f" rag新增时json转str错误: {e}")
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
        logger.error(f"rag新增接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''rag修改接口'''

@router.put("/rag/update", tags=["RAG知识库修改"])
def rag_update(mydata: ragzgsarg):
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
                ragdata['split'] = str(ragdata['split'])
            if ragdata.get('search'):
                ragdata['search'] = str(ragdata['search'])
        except Exception as e:
            logger.error(f" rag修改时json转str错误: {e}")
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
        logger.error(f"rag修改接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''rag删除接口'''


@router.delete("/rag/del", tags=["RAG知识库删除"])
def rag_del(mydata: ragzgsarg):
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
        logger.error(f"rag删除接口错误: {e}")
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
def file_get(mydata: cxzharg):
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
                    d['split'] = eval(d['split'])
            except Exception as e:
                logger.error(f" 文件查询时转字典错误: {e}")
                logger.error(traceback.format_exc())

        # 获取表头
        tbdata = get_zydict('tb', 'file_tb')
        fileformat = get_zydict('file', 'fileformat')
        keys_list = list(fileformat.keys())  # 获取支持的文件格式
        keys_list.remove("size")  # size不是文件格式，所以不用再返回了
        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit'), "tb": tbdata,
                         "fileformat":  keys_list, "size":fileformat.get('size', 10)}}
    except Exception as e:
        logger.error(f"文件查询接口错误: {e}")
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
                text = ''
                if data_dict.get('data', {}).get('type') in ['agent']:
                    text = file_read(f.get('filename', ''), ragid, data_dict.get('appid', ''))
                filedata = {'name': f.get('filename', ''), 'size': f.get('size', 0), 'time': nowtime, 'text': text,
                            'metadata': str({"format": f.get('format', '')}), 'appid': data_dict.get('appid', ''),
                            'user': data_dict.get('user', ''), 'ragid': ragid, 'fileid': fileid,
                            'type': data_dict.get('type', 'file'), 'split': str(data_dict.get("split", ''))}
                # 组合sql语句
                sql = my.sql3sz(filedata, 'file')
                jg = my.msqlzsg(sql)  # 执行sql语句，增加文件到数据库
                logger.warning(f'文件上传入库结果={jg}，sql={sql}')

        return {"msg": "文件上传完成", "code": "200", "data": results}
    except Exception as e:
        logger.error(f"文件上传时错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''文件修改接口'''

@router.put("/file/update", tags=["RAG文件修改"])
def file_update(mydata: filezgsarg):
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
                data2['split'] = eval(data2['split'])
        except Exception as e:
            logger.error(f" rag修改时json转str错误: {e}")
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
        logger.error(f"文件修改接口误错: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''文件删除接口'''

@router.delete("/file/del", tags=["RAG文件删除"])
def file_del(mydata: filezgsarg):
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
        logger.error(f"文件删除接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}




'''******文件解析、向量化******'''


class filedataarg4(BaseModel):
    filedata: list[dict] = Field(frozen=True, description="要解析的文件数据[{文件数据1},{文件数据2}]，可以多个，必填")
    ragdata: dict = Field(frozen=True, description="要解析的文件所属知识库的数据，必填")

class filejxarg(publicarg):  # 通用增加和修改组合，公共+data
    data: filedataarg4



'''文件解析接口,解析状态：no 未解析，work 解析中，ok已解析'''

@router.api_route("/file/analysis", methods=["POST"], tags=["文件解析"])
def file_analysis(mydata: filejxarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})
        # 调用解析模块执行解析
        jglist = fileanalysis(data2.get('filedata', []), data2.get('ragdata', {}))
        # 返回发起解析的结果
        return {"msg": "success", "code": "200", "data": jglist}
    except Exception as e:
        logger.error(f"文件解析接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''向量文本块part查询'''

@router.api_route("/part/get", methods=["POST"], tags=["文本段查询"])
def part_get(mydata: cxzharg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})

        # 获取数据，从向量数据库中查询
        filterdata = data2.get('filter', {})
        vfilter = copy.deepcopy(filterdata)
        if 'ragid' in vfilter:
            del vfilter['ragid']  # 删除ragid，因为向量库里没有ragid字段可检索
        jsondata = data2.get('filterjson', {})
        vjg = mv.query_data(filterdata.get('ragid'), filterdata= vfilter, page=data2.get('page'), limit=data2.get('limit'),
                                   count=1, jsondata=jsondata)  # 查询数据

        datac = vjg.get('data', [])
        nub = vjg.get('nub', 0)
        logger.warning(f'查询到数据={datac}，现在返回, nub={nub}')
        # 把datac中的id的值转为字符串，以解决大数限制的问题
        for d in datac:
            d['id'] = str(d['id'])

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data2.get('page'),"limit": data2.get('limit')}}
        # return Response(content=json.dumps(rdata), media_type="application/json")
    except Exception as e:
        logger.error(f"向量文本块part查询错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''文本段通用新增、修改、删除'''

class partdataarg4(BaseModel):
    ragdata: dict = Field(frozen=True, description="知识库数据,必填")
    id: list = Field([0], description="文本段id列表,删除时使用")
    data: Union[list, dict] = Field({}, description="增加修改时必填，修改时格式[{}, {}],支持多条，增加时{}，支持单条，删除时可传检索项{}")

class partzgsarg(publicarg):  # 通用增加和修改组合，公共+data
    data: partdataarg4


'''向量文本块part新增'''

@router.api_route("/part/add", methods=["POST"], tags=["文本段新增"])
def part_add(mydata: partzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})
        # 判断是否为问答
        partdata = data2.get('data', {})
        # 调取转向量函数，转换并入库
        jg = partjx(partdata, data2.get('ragdata', {}))

        if jg:
            return {"msg": "success", "code": "200", "data": ''}
        else:
            return {"msg": "error", "code": "150", "data": ""}
    except Exception as e:
        logger.error(f"向量文本块part新增错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''向量文本块part修改'''

@router.api_route("/part/update", methods=["POST"], tags=["文本段修改"])
def part_update(mydata: partzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})
        # 判断是否为问答
        partdata = data2.get('data', {})
        if partdata and type(partdata) in [dict]:  # 当为单条数据更新时，转为列表，多条时传过来的就是列表
            partdata = [partdata]

        # 获取embedding数据
        ragdata = data2.get('ragdata', {})
        embdid = ragdata.get('embedding').split('/')[1] if ragdata.get('embedding') else 'bge-large-zh-v1.5'
        embddata = get_zydict('embd', embdid)
        # 遍历修改的数据，重新转换向量，判断是否有问，如果有问为向量文本
        for part in partdata:
            # 修改id值为int
            part['id'] = int(part['id'])
            # 处理文本转向量
            s_text = part.get('s_text', '')
            q_text = part.get('q_text', '')
            if not s_text:  # 向量化检索
                logger.warning(f'向量化检索数据处理开始')
                # 判断是否为问答或llm泛化问答
                if q_text:  # 问答时t的数据格式为{q: ,a: }
                    part['vector'] = zyembd(q_text, embddata)
                else:  # 非问答时，t就是文本内容
                    part['vector'] = zyembd(part.get('text', ''), embddata)
            else:  # 全文检索  向量+稀疏向量检索
                logger.warning(f'向量+稀疏向量检索数据处理开始')
                # 判断是否为问答或llm泛化问答
                if q_text:  # 问答时t的数据格式为{q: ,a: }
                    part['s_text'] = q_text
                    part['vector'] = zyembd(q_text, embddata)
                else:  # 非问答时，t就是文本内容
                    part['s_text'] = part.get('text', '')
                    part['vector'] = zyembd(part.get('text', ''), embddata)

        # 调取转向量函数，转换并入库
        jg = mv.upsert_data(partdata, data2.get('ragdata', {}).get('ragid', ''))

        if jg:
            return {"msg": "success", "code": "200", "data": ''}
        else:
            return {"msg": "error", "code": "150", "data": ""}
    except Exception as e:
        logger.error(f"向量文本块part修改错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''向量文本块part删除'''

@router.api_route("/part/del", methods=["DELETE"], tags=["文本段删除"])
def part_del(mydata: partzgsarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data2 = data_dict.get('data', {})
        # 判断是否为问答
        filterdata = data2.get('data', {})
        # 调取转向量函数，转换并入库
        jg = mv.del_data(data2.get('ragdata', {}).get('ragid', ''), ids=data2.get('id', []), filterdata=filterdata)
        if jg:
            return {"msg": "success", "code": "200", "data": jg}
        else:
            return {"msg": "error", "code": "150", "data": ""}
    except Exception as e:
        logger.error(f"向量文本块part删除错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}




'''向量知识搜索查询'''

class vdataarg5(BaseModel):
    ragid: str = Field(frozen=True, description="知识库的id,必填")
    text: str = Field(frozen=True, description="查询的文本")
    score: float = Field(0.1, description="相似度阀值")
    limit: int = Field(10, description="返回的文本段数量")
    filter: dict = Field({}, description="检索项，格式：{'字段名':'字段值'}")
    filter_json: dict = Field({}, description="json字段检索项，格式：{'字段名':{字段名：值}}")
    rerank: str = Field('', description="rerank重排序模型")

class ragvarg(publicarg):  # rag知识搜索
    data: vdataarg5


'''rag知识搜索功能，向量、稀疏向量计算相似度+搜索'''

@router.api_route("/rag/search", methods=["POST"], tags=["rag知识搜索"])
def rag_search(mydata: ragvarg):
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data = data_dict.get('data', {})
        # 获取检索条件
        filterdata = data.get('filter', {})
        # 获取ragid
        ragid = data.get('ragid', '')
        # 获取rag配置数据
        ragdata = get_rag(ragid)
        search_fun = ragdata.get('search', {}).get('search_fun', 'vector')
        # 获取embedding数据
        embdid = ragdata.get('embedding').split('/')[1] if ragdata.get('embedding') else 'bge-large-zh-v1.5'
        embddata = get_zydict('embd', embdid)
        datac = []
        logger.warning(f'获取到的数据:search_fun={search_fun}, embddata={embddata}')
        if search_fun in ['vector', 'sparse']:  # 单向量搜索
            if search_fun in ['vector']:  # 密集向量搜索
                logger.warning(f'向量搜索开始')
                # 把text转为向量后传入搜索函数
                textv = zyembd(data.get('text', ''), embddata)
                datac = mv.vector_search(ragdata.get('ragid', ''), [textv], 'vector',
                                         limit=data.get('limit', 10), radius=data.get('score', 0.1))
            else:  # 稀疏向量搜索
                logger.warning(f'稀疏向量搜索开始')
                datac = mv.vector_search(ragdata.get('ragid', ''), [data.get('text', '')], 'sparse',
                                         limit=data.get('limit', 10),  radius=data.get('score', 0.1))
        elif search_fun in ['vs']:  # 混合搜索
            logger.warning(f'混合搜索开始')
            # 把text转为向量后传入搜索函数
            textv = zyembd(data.get('text', ''), embddata)
            # 组合重排序
            rerank = 'RRFRanker'
            rrv = '60'
            search_data = ragdata.get('search', {})
            if 'wr' in search_data:
                rrv = search_data.get('wr', '0.8/0.5')
                rerank = 'WeightedRanker'
            elif 'rr' in search_data:
                rrv = search_data.get('rr', '60')
                rerank = 'RRFRanker'
            # 执行混合搜索
            datac = mv.hybrid_search(ragdata.get('ragid', ''), [textv], [data.get('text', '')],
                                 limit=data.get('limit', 5), reranking=rerank, rrv=rrv)
        logger.warning(f'搜索结果={datac}')
        return {"msg": "success", "code": "200", "data": datac}
    except Exception as e:
        logger.error(f"rag知识搜索错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}













