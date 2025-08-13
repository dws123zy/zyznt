# _*_coding:utf-8 _*_

from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Response
from fastapi.responses import FileResponse
import logging
from pydantic import BaseModel, Field
import traceback
from typing import Union, Any
import time
import random
import string

# 本地模块
from db.sa import db_connection, export_db_schema, sa_sql_query
from data.data import tokenac, get_zydict
from db import my


'''此程序为智能数据Bi功能模块'''


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


class biconnectarg(publicarg):  # data中的个性化参数
    data: Any = Field(frozen=True, description="db连接的配置完整数据或db_id配置id")


class cxzharg(publicarg):  # 通用查询类组合，公共+data
    data: cxdataarg



'''db url 连接检测接口'''

@router.post("/db/connect", tags=["智能Bi db_url连接检测"])
def db_connect(mydata: biconnectarg):
    """db url 连接检测"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'db_connect收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        db_data = data_dict.get('data', {})
        # 获取db 连接的用的模块
        db_mod = db_data.get('db_mod', '')
        # 根据模块调用对应的模块检测db url连接
        if db_mod in ['SQLAlchemy', 'sa', 'sqlalchemy']:  # SQLAlchemy
            jg = db_connection(db_data.get('db_url', ''), timeout=db_data.get('timeout', 30))
            if jg in ['OK', 'ok']:
                logger.info(f"数据库连接成功")
                return {"msg": "数据库连接成功", "code": "200", "data": ""}
            else:
                logger.warning(f"连接数据库时出错: {jg}")
                return {"msg": f"连接数据库时出错: {jg}", "code": "152", "data": ""}
        else:
            logger.warning(f'db_mod参数错误')
            return {"msg": "db_mod参数错误", "code": "151", "data": ""}

    except Exception as e:
        logger.error(f"db url 连接检测接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''获取数据库结构数据'''

@router.post("/db/get_db_schema", tags=["智能Bi获取db结构数据"])
def get_db_schema(mydata: biconnectarg):
    """获取数据库结构数据"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'get_db_schema收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        db_data = data_dict.get('data', {})
        # 判断db data格式，如果是str，则判断为db_id，此时从zydict中获取完整的db data
        if isinstance(db_data, str):
            db_data = get_zydict('db', db_data)
        # 获取db 连接的用的模块
        db_mod = db_data.get('db_mod', '')
        # 根据模块调用对应的模块检测db url连接
        if db_mod in ['SQLAlchemy', 'sa', 'sqlalchemy']:  # SQLAlchemy
            db_schema = export_db_schema(db_data.get('db_url', ''), timeout=db_data.get('timeout', 30))
            if type(db_schema) in [str]:
                logger.warning(f"获取数据库结构数据错误: {db_schema}")
                return {"msg": f"连接数据库时出错: {db_schema}", "code": "152", "data": ""}
            else:
                logger.info(f"获取数据库结构数据成功")
                return {"msg": "success", "code": "200", "data": db_schema}
        else:
            logger.warning(f'db_mod参数错误')
            return {"msg": "db_mod参数错误", "code": "151", "data": ""}

    except Exception as e:
        logger.error(f"db url 连接检测接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}

''''sql语句执行模型'''

class sqldataarg(BaseModel):  # 查询时data中的标准参数
    sql: Any = Field(frozen=True, description="要执行的sql语句, 格式示例：[{}]")
    limit: int = Field(200, description="每页显示的数量")
    page: int = Field(1, description="页码，第几页")


class sqlzharg(publicarg):  # 通用查询类组合，公共+data
    data: sqldataarg


'''执行sql语句'''

@router.post("/db/sql_get_data", tags=["智能Bi-SQL语句执行接口"])
def sql_get_db_data(mydata: sqlzharg):
    """执行sql语句"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'sql_get_db_data收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        db_data = data_dict.get('data', {})
        limit = db_data.get('limit', 200)
        page = db_data.get('page', 1)
        # 获取db 连接的用的模块
        sql_list = db_data.get('sql', [])
        rdata = []
        for s in sql_list:
            # 获取db_id，然后拿到db的连接配置数据
            db_data = get_zydict('db', s.get('db_id', ''))
            db_mod = db_data.get('db_mod', '')
            # 根据模块调用对应的模块检测db url连接
            if db_mod in ['SQLAlchemy', 'sa', 'sqlalchemy']:  # SQLAlchemy
                data = sa_sql_query(db_data.get('db_url', ''), s.get('sql', ''),timeout=db_data.get('timeout', 30))
                if data.get('code') in [200, '200']:
                    logger.info(f"执行sql语句成功")
                    s['data'] = data.get('data')
                    s['code'] = 200
                    s['limit'] = limit
                    s['page'] = page
                    s['nub'] = data.get('total', 0)
                    rdata.append(s)
                else:
                    logger.info(f"执行sql语句失败")
                    s['data'] = data.get('msg')
                    s['code'] = 500
                    rdata.append(s)
            else:
                logger.warning(f'db_mod参数错误')

        return {"msg": "数据查询成功", "code": "200", "data": rdata}

    except Exception as e:
        logger.error(f"sql_get_db_data执行sql语句错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}



'''数据模型管理功能模块'''



'''数据模型通用新增、修改、删除'''

class datamodarg3(BaseModel):
    id: str = Field('', description="本条数据的id,修改删除时必填")
    data: Any = Field({}, description="增加或修改的数据[{}, {}]，增加修改时必填，删除时的检索项数据")
    appid: str = Field('', description="企业id，不填写时默认使用当前请求的appid")
    db_id: str = Field('', description="源数据库配置id")
    data_id: str = Field('', description="数据模型名称，新增加必填")

class datamodarg(publicarg):  # 通用增加和修改组合，公共+data
    data: datamodarg3


# '''数据模型查询接口'''
#
# @router.post("/data/get_model", tags=["数据模型查询"])
# def data_get_model(mydata: cxzharg):
#     """数据模型查询"""
#     try:
#         data_dict = mydata.model_dump()
#         logger.warning(f'data_get_model收到的请求数据={data_dict}')
#         # 验证token、user
#         if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
#             logger.warning(f'token验证失败')
#             return {"msg": "token或user验证失败", "code": "403", "data": ""}
#         data = data_dict.get('data', {})
#
#         # 写sql
#         filterdata = data.get('filter', {})
#         if not filterdata.get('appid', ''):  # 如果检索项中没有appid，则使用当前user的appid
#             filterdata['appid'] = data_dict.get('appid', '')
#
#         sql = f"SELECT data_name,COUNT(*) AS data_count FROM data_model WHERE appid = {filterdata.get('appid')} GROUP BY data_name;"
#         if filterdata.get('data_name'):
#             sql = f"SELECT data_name,COUNT(*) AS data_count FROM data_model WHERE appid = {filterdata.get('appid')} AND data_name LIKE '%{filterdata.get('data_name')}%' GROUP BY data_name;"
#
#         datac= my.msqlc(sql)  # 查询数据
#
#         # 获取表单数据form
#         # formdata = get_zydict('form', 'rag_form')
#
#         return {"msg": "success", "code": "200", "data": {"data": datac}}
#     except Exception as e:
#         logger.error(f"数据模型查询错误: {e}")
#         logger.error(traceback.format_exc())
#         return {"msg": "error", "code": "501", "data": ""}


'''数据集查询接口'''

@router.post("/dataset/get", tags=["智能Bi数据集查询"])
def dataset_get(mydata: cxzharg):
    """数据集查询"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'data_get_set收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data = data_dict.get('data', {})

        # 写sql
        filterdata = data.get('filter', {})
        if not filterdata.get('appid', ''):  # 如果检索项中没有appid，则使用当前user的appid
            filterdata['appid'] = data_dict.get('appid', '')

        sql = my.sqlc3like(filterdata, 'data_set', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('data'):
                    d['data'] = eval(d['data'])
            except Exception as e:
                logger.error(f" 数据集查询时转字典错误: {e}")
                logger.error(traceback.format_exc())

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit')}}
    except Exception as e:
        logger.error(f"数据集查询错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''数据集新增接口'''

@router.post("/dataset/add", tags=["智能Bi数据集新增"])
def dataset_add(mydata: datamodarg):
    """数据集新增"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'dataset_add收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要新增的配置数据
        data = data_dict.get('data', {})
        if not data.get('appid'):
            data['appid'] = data_dict.get('appid', '')
        table_data = data.get('data', [])

        # 遍历table_data，增加数据到数据库
        rdata = []
        for d in table_data:
            # 获取当前时间
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            tb_type = d.get('type', 'table')
            table_label = d.get('table_label', '') if tb_type in ['table'] else d.get('view_label', '')
            table_name =  d.get('table_name', '') if tb_type in ['table'] else d.get('view_name', '')
            # 初始化要新增的数据
            add_data = {"db_id": data.get('db_id', ''), "data_id": data.get('data_id', ''),
                        "appid": data.get('appid', ''), "time": nowtime, "table_name": table_name,
                        "table_label": table_label, "type": tb_type, "user": data_dict.get('user', ''),
                        "data": str(d)}

            # 存入mysql数据库
            sql = my.sqlz(add_data, 'data_set')
            jg = my.msqlzsg(sql)
            rdata.append(jg)

        # 返回结果
        return {"msg": "success", "code": "200", "data": rdata}
    except Exception as e:
        logger.error(f"数据集新增接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''智能Bi数据集修改'''

@router.put("/dataset/update", tags=["智能Bi数据集修改"])
def dataset_update(mydata: datamodarg):
    """数据集修改接口"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'dataset_update收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要修改的数据
        data = data_dict.get('data', {})
        dataset = data.get('data', {})
        # 获取id
        set_id  = data.get('id', '')
        if not set_id:
            set_id = dataset.get('id', '')
            if not set_id:
                logger.warning(f'id为空了')
                return {"msg": "id不能为空", "code": "151", "data": ""}
        # 字段id不能修改
        if 'id' in dataset:
            del dataset['id']
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dataset['time'] = nowtime

        # 把部分字段值的字典转字符
        try:
            if dataset.get('data'):
                dataset['data'] = str(dataset['data'])
        except Exception as e:
            logger.error(f" 智能Bi数据集修改时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'id': set_id}

        # 存入mysql数据库
        sql = my.sqlg(dataset, 'data_set', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'数据集修改成功')
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}
        else:
            logger.warning(f'数据集修改失败')
            return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"数据集修改失败接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''智能Bi数据集删除'''

@router.delete("/dataset/del", tags=["智能Bi数据集删除"])
def dataset_del(mydata: datamodarg):
    """数据集删除接口"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'dataset_del收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 获取id
        set_id = data_dict.get('data', {}).get('id', '')
        if not set_id:
            return {"msg": "id不正确", "code": "151", "data": ""}

        # 组合检索项
        filterdata = {'id': set_id}

        # mysql数据库删除数据
        sql = my.sqls('data_set', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'删除数据集成功{set_id}')
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}
        else:
            logger.warning(f'删除数据集失败{set_id}')
            return {"msg": "db error", "code": "150", "data": ''}

    except Exception as e:
        logger.error(f"删除数据集接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}



'''智能数据Bi数据查询功能模块'''



'''智能数据Bi数据查询通用新增、修改、删除'''

class dataqueryarg3(BaseModel):
    query_id: str = Field('', description="数据查询id,修改删除时必填")
    data: dict = Field({}, description="增加或修改的数据，增加修改时必填")

class dataqueryarg(publicarg):  # 通用增加和修改组合，公共+data
    data: dataqueryarg3


'''智能数据Bi数据查询接口'''

@router.post("/data_query/get", tags=["智能Bi数据查询"])
def data_query_get(mydata: cxzharg):
    """智能Bi数据查询"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'data_query_get收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        data = data_dict.get('data', {})

        # 写sql
        filterdata = data.get('filter', {})
        if not filterdata.get('appid', ''):  # 如果检索项中没有appid，则使用当前user的appid
            filterdata['appid'] = data_dict.get('appid', '')
        sql = my.sqlc3like(filterdata, 'query', data.get('page'), data.get('limit'), '')
        datac, nub = my.msqlcxnum(sql)  # 查询数据

        # 把部分字段值的json字符串转字典
        for d in datac:
            try:
                if d.get('data'):
                    d['data'] = my.safe_base64_to_list(d['data'])
            except Exception as e:
                logger.error(f" agent查询时转字典错误: {e}")
                logger.error(traceback.format_exc())

        # 获取表单数据form
        # formdata = get_zydict('form', 'agent_form')

        return {"msg": "success", "code": "200",
                "data": {"data": datac, "nub": nub, "page": data.get('page'),"limit": data.get('limit')}}
    except Exception as e:
        logger.error(f"智能数据Bi数据查询接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''智能Bi数据查询新增接口'''

@router.post("/data_query/add", tags=["智能Bi数据查询新增"])
def data_query_add(mydata: dataqueryarg):
    """智能数据查询新增接口"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'data_query_add收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要新增的配置数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})
        # query_id
        query_id  = 'query'+str(int(time.time()))+''.join(random.choice(string.digits) for _ in range(3))
        data2['query_id'] = query_id
        # 获取当前时间
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data2['time'] = nowtime
        # 判断data2中是否有appid，如果没有则使用当前user的appid
        if not data2.get('appid', ''):
            data2['appid'] = data_dict.get('appid', '')
        # 判断data2中是否有user，如果没有则使用当前user
        if not data2.get('user', ''):
            data2['user'] = data_dict.get('user', '')
        # 判断是否有data的值
        if not data2.get('data', ''):
            data2['data'] = {}

        # 把部分字段值的字典转字符
        try:
            if data2.get('data'):
                b64rdata = my.list_to_safe_base64(data2['data'])
                data2['data'] = b64rdata
        except Exception as e:
            logger.error(f"智能数据查询新增时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 存入mysql数据库
        sql = my.sqlz(data2, 'query')
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'存入数据库成功{query_id}')
            # 返回结果
            return {"msg": "success", "code": "200", "data": {"query_id": query_id}}

        # 返回结果
        logger.warning(f'智能数据查询新增失败{query_id}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"智能数据查询新增接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}


'''智能Bi数据查询修改接口'''

@router.put("/data_query/update", tags=["智能Bi数据查询修改"])
def data_query_update(mydata: dataqueryarg):
    """智能数据查询修改接口"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'data_query_update收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 拿到要修改的数据
        data = data_dict.get('data', {})
        data2 = data.get('data', {})
        # 获取query_id
        query_id  = data.get('query_id', '')
        if not query_id:
            query_id = data2.get('query_id', '')
            if not query_id:
                logger.warning(f'query_id不能为空')
                return {"msg": "query_id不能为空", "code": "151", "data": ""}
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
            logger.error(f"智能Bi数据查询修改时json转str错误: {e}")
            logger.error(traceback.format_exc())

        # 组合检索项
        filterdata = {'appid': data2.get('appid', ''), 'query_id': query_id}

        # 存入mysql数据库
        sql = my.sqlg(data2, 'query', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}
        logger.warning(f'智能Bi数据查询修改失败{query_id}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"智能Bi数据查询修改接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "error", "code": "501", "data": ""}


'''智能Bi数据查询删除接口'''

@router.delete("/data_query/del", tags=["智能Bi数据查询删除"])
def data_query_del(mydata: dataqueryarg):
    """智能数据查询删除接口"""
    try:
        data_dict = mydata.model_dump()
        logger.warning(f'data_query_del收到的请求数据={data_dict}')
        # 验证token、user
        if not tokenac(data_dict.get('token', ''), data_dict.get('user', '')):
            logger.warning(f'token验证失败')
            return {"msg": "token或user验证失败", "code": "403", "data": ""}
        # 获取query_id
        query_id = data_dict.get('data', {}).get('query_id', '')
        if not query_id:
            return {"msg": "query_id不正确", "code": "151", "data": ""}

        # 组合检索项
        filterdata = {'query_id': query_id}

        # 存入mysql数据库
        sql = my.sqls('query', filterdata)
        jg = my.msqlzsg(sql)
        if jg:
            logger.warning(f'删除数据库表、mysql数据库成功{query_id}')
            # 返回结果
            return {"msg": "success", "code": "200", "data": ''}

        # 返回结果
        logger.warning(f'智能Bi数据查询删除失败{query_id}')
        return {"msg": "db error", "code": "150", "data": ''}
    except Exception as e:
        logger.error(f"智能Bi数据查询删除接口错误: {e}")
        logger.error(traceback.format_exc())
        return {"msg": "data error", "code": "501", "data": ""}




















