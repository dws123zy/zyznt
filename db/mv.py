# _*_coding:utf-8 _*_
from asyncio import timeout

from pymilvus import MilvusClient
from pymilvus import DataType, FieldSchema, CollectionSchema, Function, FunctionType
from pymilvus import AnnSearchRequest, WeightedRanker, RRFRanker
import traceback
import time
import logging


'''日志'''

logger = logging.getLogger(__name__)


'''检查数据库zyai是否存在，不存在就创建'''

dbname = 'zyai'

dburl = 'http://139.196.36.245:19530'

dbtoken = ''


def milvus_init(vdburl=dburl, vdbtoken=dbtoken):
    try:
        client = MilvusClient(uri=vdburl, token=vdbtoken)  # , db_name="zyai")
        # client = MilvusClient("db/zyrag.db")
        try:
            # print('mdb已链接=', client)
            # 查询所有的数据库名
            dblist = client.list_databases()
            # print('已有的数据库=', dblist)

            # 判断zyai数据库是否存在
            if 'zyai' in dblist:
                logger.warning(f'{dbname}向量数据库已存在，无需创建')
            else:
                logger.warning(f'{dbname}不存在，第一次启动要建创')
                client.create_database(db_name="zyai")

            # 关闭数据库
            client.close()
        except Exception as e:
            logger.error(f"初始化向量数据库出错: {e}")
            logger.error(traceback.format_exc())
        finally:
            client.close()
    except Exception as e2:
        logger.error(f"初始化向量数据库连接出错: {e2}")
        logger.error(traceback.format_exc())

milvus_init()  # 初始化向量数据库


'''建表collection'''

def create_collections(schema, tbname, index_param, vdburl=dburl, vtoken=dbtoken, vdbname=dbname):
    try:
        client = MilvusClient(uri=vdburl, token=vtoken, db_name=vdbname)
        try:
            client.create_collection(
                collection_name=tbname,
                schema=schema,
                index_params=index_param
            )
            exists = client.has_collection(collection_name=tbname)
            print('exists=', exists)
            if exists:
                logger.warning(f'{tbname}向量表创建成功mv')
                return 1
            else:
                logger.warning(f'{tbname}向量表创建失败mv')
                return 0
        except Exception as e:
            logger.error(f"建向量表出错: {e}")
            logger.error(traceback.format_exc())
            return 0
        finally:
            client.close()
    except Exception as e2:
        logger.error(f"建向量表连接出错: {e2}")
        logger.error(traceback.format_exc())
        return 0


'''组合schema，index用于建表'''

def schema_create(schema_data, dim=1024):
    try:
        '''创建schema'''
        schema = MilvusClient.create_schema()
        '''组合表字段、索引、bm25函数'''
        schema_data = eval(schema_data)

        # 创建字段schema
        for f in schema_data.get('fields'):
            dtype = f.get("type", '')
            print(dtype)

            if dtype in [DataType.INT64]:  # 整型字段主键字段
                schema.add_field(field_name=f.get("name"), datatype=dtype, is_primary=f.get("is_primary", False),
                                 auto_id=f.get("auto_id", False), description=f.get("description"),)

            elif dtype in [DataType.FLOAT_VECTOR, DataType.BINARY_VECTOR]:  # 向量字段
                schema.add_field(field_name=f.get("name"), datatype=dtype, description=f.get("description"),
                                 dim=dim)
            elif dtype in [DataType.VARCHAR]:  # 字符串字段
                schema.add_field(
                    field_name=f.get("name"),
                    datatype=dtype,
                    max_length=f.get("max_length", 65535),
                    description=f.get("description"),
                    default_value=f.get("default_value", ''),
                    enable_analyzer=f.get("enable_analyzer", False)
                )
            elif dtype in [DataType.SPARSE_FLOAT_VECTOR]:  # bm25字段
                schema.add_field(
                    field_name=f.get("name"),
                    datatype=dtype,
                    description=f.get("description"),
                )
            elif dtype in [DataType.JSON]:  # json字段
                schema.add_field(
                    field_name=f.get("name"),
                    datatype=dtype,
                    description=f.get("description"),
                    max_length=f.get("max_length", 65535),
                    nullable=f.get("nullable", True)
                )
            # else:
            #     schema.add_field(
            #         field_name=f.get("name"),
            #         datatype=dtype,
            #         is_primary=f.get("is_primary", False)
            #     )

        # 创建集合schema
        func = schema_data.get('functions')
        if func:  # 判断是否有函数
            # 定义并添加BM25函数
            bm25_function = Function(
                name=func.get('name'),
                input_field_names=func.get('input_field_names'),
                output_field_names=func.get('output_field_names'),
                function_type=FunctionType.BM25
            )

            # 添加函数到schema
            schema.add_function(bm25_function)



        # print(type(schema_data), schema_data)
        #
        # schema = CollectionSchema.construct_from_dict(schema_data)

        print(schema)

        '''验证schema,有问题会抛异常'''
        schema.verify()

        '''组合索引'''
        # 准备索引参数
        index_param = MilvusClient.prepare_index_params()

        for i in schema_data.get('index_params'):
            if i.get('metric_type'):
                index_param.add_index(
                    field_name=i.get('field_name'),
                    index_type=i.get('index_type'),
                    metric_type=i.get('metric_type'),
                )
            else:
                index_param.add_index(
                    field_name=i.get('field_name'),
                    index_type=i.get('index_type'),
                )

        '''检测可用性'''
        print(index_param)
        # index_param.verify()

        return schema, index_param

    except Exception as e:
        logger.error(f"组合schema出错: {e}")
        logger.error(traceback.format_exc())
        return '', ''


'''删除表'''

def drop_collections(tbname, vdburl=dburl, vtoken=dbtoken, vdbname=dbname):
    try:
        client = MilvusClient(uri=vdburl, token=vtoken, db_name=vdbname)
        try:
            client.drop_collection(collection_name=tbname)
            exists = client.has_collection(collection_name=tbname)
            print('exists=', exists)
            if not exists:
                logger.warning(f'{tbname}向量表删除成功')
                return 1
            else:
                logger.warning(f'{tbname}向量表删除失败')
                return 0
        except Exception as e:
            logger.error(f"删向量表出错: {e}")
            return 0
        finally:
            client.close()
    except Exception as e2:
        logger.error(f"删向量表连接出错: {e2}")
        logger.error(traceback.format_exc())
        return 0


'''增加、插入数据'''

def insert_data(data, tbname, vdburl=dburl, vtoken=dbtoken, vdbname=dbname):
    try:
        client = MilvusClient(uri=vdburl, token=vtoken, db_name=vdbname)
        try:
            res = client.insert(
                collection_name=tbname,
                data=data
            )

            print(res)
            if res:
                logger.warning(f'{tbname}向量数据新增成功')
                return 1
            else:
                logger.warning(f'{tbname}向量数据新增失败')
                return 0
        except Exception as e:
            logger.error(f"向量数据新增出错: {e}")
            return 0
        finally:
            client.close()
    except Exception as e2:
        logger.error(f"向量数据新增连接出错: {e2}")
        logger.error(traceback.format_exc())
        return 0



'''处理json检索项组合'''


def filter_data(filterdata, jsondata):
    try:
        filter_template = ''
        filter_params = {}  # 就是传进来的字典
        # 先组合filterdata数据
        if filterdata:
            filter_params = filterdata  # 就是传进来的字典
            # 组合filter_template
            for k, v in filterdata.items():
                if filter_template:
                    filter_template += f"and {k} == {v} "
                else:
                    filter_template = f"{k} == {v} "
        # 组合json检索项数据
        if jsondata:
            if filter_params:  # 此时已有检索项数据
                filter_params = {**filter_params, **jsondata}
            else:
                filter_params = jsondata
            # 组合filter_template-json检索项
            for k, v in jsondata.items():
                for m,  n in v.items():
                    if filter_template:
                        filter_template += f"and {k}[{m}] == {n} "
                    else:
                        filter_template = f"{k}[{m}] == {n} "

        return filter_template, filter_params
    except Exception as e:
        logger.error(f"组合filter_template出错: {e}")
        logger.error(traceback.format_exc())
        return '', ''



'''查询函数, count值为真时，统计总条数返回'''

def query_data(tbname, filterdata='', page=1, limit=10, count='', output_fields=['*'], timeout=180.0, jsondata = ''):
    try:
        client = MilvusClient(uri=vdburl, token=vtoken, db_name=vdbname)
        try:
            # 组合分页
            offset = (page-1)*limit
            # 组合查询数据
            filter_template = ''
            filter_params = {}
            if filterdata or jsondata:  # 此时有检索项数据或有json检索项数据
                filter_template,  filter_params = filter_data(filterdata, jsondata)

            # 执行查询
            resdata = client.query(
                collection_name=tbname,
                filter=filter_template,
                filter_params=filter_params,
                output_fields=output_fields,  # 默认返回所有字段
                offset=offset,  # 从第一条记录开始
                limit=limit,  # 每页返回10条
                timeout=timeout  # 默认180秒
            )
            # 判断是否需要统计总数
            resnub = 0  # 默认0
            if count:
                # 统计总数
                rescount = client.query(
                    collection_name=tbname,
                    filter=filter_template,
                    filter_params=filter_params,
                    output_fields=["count(*)"],  # 使用count(*)来获取总数
                    timeout=timeout
                )
                # 返回结果格式为 [{'count(*)': 数量}]
                resnub = rescount[0]['count(*)']

            res = {
                "data": resdata,
                "nub": resnub
            }

            return res
        except Exception as e:
            logger.error(f"分页查询出错: {e}")
            logger.error(traceback.format_exc())
            return {}
        finally:
            client.close()
    except Exception as e:
        logger.error(f"查询出错: {e}")
        logger.error(traceback.format_exc())
        return {}



'''向量计算搜索函数，单向量搜索，支持向量和全文bm25'''

def vector_search(tbname, text_vector, vector_field, filterdata='', limit=10, output_fields=['*'],
                  timeout=180.0, jsondata = ''):
    try:
        '''
        tbname collection_name表名
        text_vector # 查询向量列表，就是文本转后的向量，支持多个，列表格式
        vector_field  向量字段
        '''
        client = MilvusClient(uri=vdburl, token=vtoken, db_name=vdbname)
        try:
            # 组合分页
            offset = (page-1)*limit
            # 组合查询数据
            filter_template = ''
            filter_params = {}
            if filterdata or jsondata:  # 此时有检索项数据或有json检索项数据
                filter_template,  filter_params = filter_data(filterdata, jsondata)

            # 执行查询
            resdata = client.search(
                collection_name=tbname,
                data=text_vector,  # 查询向量列表，就是文本转后的向量
                anns_field=vector_field,  # 向量字段名称
                filter=filter_template,  # 标量过滤表达式,默认为空
                filter_params=filter_params,  #  就是传进来的字典
                output_fields=output_fields,  # 默认返回所有字段
                limit=limit,  # 每页返回10条
                timeout=timeout  # 默认180秒
            )
            # 将结果转换为列表格式
            formatted_results = []
            for hits in resdata:
                hits_list = []
                for hit in hits:
                    hit_dict = {
                        'id': hit.get('id', ''),
                        'distance': hit.get('distance', '0'),
                    }
                    # 添加输出字段
                    if hit.get('entity'):
                        hit_dict.update(hit.get('entity', {}))
                    hits_list.append(hit_dict)
                formatted_results.append(hits_list)
            # 返回结果
            return formatted_results
        except Exception as e:
            logger.error(f"向量计算搜索出错: {e}")
            logger.error(traceback.format_exc())
            return []
        finally:
            client.close()
    except Exception as e:
        logger.error(f"向量计算搜索出错: {e}")
        logger.error(traceback.format_exc())
        return []



'''混合搜索，支持向量+全文bm25同时搜索，或加图片等其它'''

def hybrid_search(tbname, text_vector, text_sparse, vector_field='vector',sparse_field='sparse', filterdata='',
                  limit=10, output_fields=['*'], timeout=180.0, jsondata = '', reranking='RRFRanker', rrv='60',
                  radius=0.1):
    try:
        '''
        tbname collection_name表名
        text_vector # 查询向量列表，就是文本转后的向量，支持多个，列表格式
        vector_field  向量字段
        text_sparse  # 稀疏向量查询文本，bm25用文本，外部模型用向量值
        sparse_field  稀疏向量字段
        reranking  内置的重排序方法
        rrv 重排序权重
        '''

        client = MilvusClient(uri=vdburl, token=vtoken, db_name=vdbname)
        try:
            # 组合查询数据
            filter_template = ''
            filter_params = {}
            if filterdata or jsondata:  # 此时有检索项数据或有json检索项数据
                filter_template,  filter_params = filter_data(filterdata, jsondata)

            #  向量搜索
            vector_search = {
                "data": text_vector,
                "anns_field": vector_field,
                'limit': limit,
                "param": {
                    "metric_type": "COSINE",
                    "radius": radius,  # 相似度阈值
                }
            }
            vector_request_1 = AnnSearchRequest(**vector_search)

            # 稀疏向量搜索
            sparse_search = {
                "data": text_sparse,
                "anns_field": sparse_field,
                'limit': limit,
                "param": {
                    "metric_type": "BM25"
                }
            }
            sparse_request_2 = AnnSearchRequest(**sparse_search)

            reqs = [vector_request_1, sparse_request_2]

            # 重排序
            ranker = RRFRanker(60)
            if reranking == 'RRFRanker':
                ranker = RRFRanker(int(rrv))
            else:
                rrv = rrv.split('/')
                ranker = WeightedRanker(round(float(rrv[0]), 1), round(float(rrv[1]), 1))


            # 执行查询
            resdata = client.hybrid_search(
                collection_name=tbname,
                reqs=reqs,
                ranker=ranker,
                filter=filter_template,  # 标量过滤表达式,默认为空
                filter_params=filter_params,  # 就是传进来的字典
                output_fields=output_fields,  # 默认返回所有字段
                limit=limit,  # 每页返回10条
                timeout=timeout  # 默认180秒
            )
            # resdata = client.search(
            #     collection_name=tbname,
            #     data=text_vector,  # 查询向量列表，就是文本转后的向量
            #     anns_field=vector_field,  # 向量字段名称
            #     filter=filter_template,  # 标量过滤表达式,默认为空
            #     filter_params=filter_params,  #  就是传进来的字典
            #     output_fields=output_fields,  # 默认返回所有字段
            #     limit=limit,  # 每页返回10条
            #     timeout=timeout  # 默认180秒
            # )
            # 将结果转换为列表格式
            formatted_results = []
            for hits in resdata:
                hits_list = []
                for hit in hits:
                    hit_dict = {
                        'id': hit.get('id', ''),
                        'distance': hit.get('distance', '0'),
                    }
                    # 添加输出字段
                    if hit.get('entity'):
                        hit_dict.update(hit.get('entity', {}))
                    hits_list.append(hit_dict)
                formatted_results.append(hits_list)
            # 返回结果
            return formatted_results
        except Exception as e:
            logger.error(f"混合搜索出错: {e}")
            logger.error(traceback.format_exc())
            return []
        finally:
            client.close()
    except Exception as e:
        logger.error(f"混合搜索出错: {e}")
        logger.error(traceback.format_exc())
        return []


























