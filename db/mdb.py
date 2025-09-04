# _*_coding:utf-8 _*_

import pymysql
# from pymysql.constants import CLIENT
from pymysql.err import OperationalError, ProgrammingError
import logging
import random
import traceback
from mod.tool import openfile  # 文件打开
from db.my import msqlc, sql3sz


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.warning('*****卓越数据库初始化程序*****')


'''项目配置文件'''

conf_data = {}
try:
    if '{' in str(openfile('../file/conf.txt')):
        conf_data = eval(openfile('../file/conf.txt'))
except:
    conf_data = {}


# 数据库连接配置
DB_CONFIG = {
    'host': conf_data.get('my_host', '127.0.0.1'),
    'user': conf_data.get('my_user', 'root'),
    'password': conf_data.get('my_password', 'zyznt'),
    'port': conf_data.get('my_port', 3306),
}

# 数据库名称
DB_NAME = 'zyai'

'''
表字段定义说明：

1. 数据类型相关属性
UNSIGNED：仅用于数值类型，表示无符号数
age INT UNSIGNED
ZEROFILL：数值不足显示宽度时用0填充
id INT(5) ZEROFILL
2. 约束属性
NOT NULL：不允许NULL值
username VARCHAR(50) NOT NULL

NULL：允许NULL值（默认）
description TEXT NULL

DEFAULT：设置默认值
status TINYINT DEFAULT 0
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

AUTO_INCREMENT：自动递增（通常用于主键）
id INT PRIMARY KEY AUTO_INCREMENT

PRIMARY KEY：设置为主键
id INT PRIMARY KEY

UNIQUE：唯一约束
email VARCHAR(100) UNIQUE

3. 字符集和排序规则
CHARACTER SET：指定字符集
name VARCHAR(50) CHARACTER SET utf8mb4

COLLATE：指定排序规则
name VARCHAR(50) COLLATE utf8mb4_unicode_ci
4. 注释
COMMENT：字段注释
phone VARCHAR(20) COMMENT '用户手机号'
'''

'''公司表company'''

company = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('name', 'varchar(50) default "" comment "公司名称"'),
            ('phone', 'varchar(30) default "" comment "联系电话"'),
            ('address', 'varchar(50) default "" comment "公司地址"'),
            ('price', 'decimal(6, 3) default 0.000 comment "价格"'),
            ('money', 'decimal(14, 3) default 0.000 comment "帐号余额"'),
            ('appid', 'varchar(20) default "" comment "公司id"'),
            ('apikey', 'varchar(50) default "" comment "api密匙"'),
            ('ipbmd', 'varchar(200) default "" comment "api接口的白名单ip，不填则无限制，多个以，分隔"'),
            ('state', 'varchar(5) default "t" comment "帐号状态，t为开，f为关，默认t"'),
            ('verify', 'varchar(6) default "t" comment "帐号登录人机验证，t为开，email为邮箱验证，f为关，默认t"'),
            ('date', 'varchar(20) default "" comment "开户时间"'),
            ('user', 'varchar(35) default "" comment "归属人帐号"'),
            ('remarks', 'varchar(100) default "" comment "备注、注释"')
        ],
        'indexes': [
            ('idx_appid', 'appid')
        ]
    }

'''用户表user'''

user = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "公司id"'),
            ('user', 'varchar(50) default "" comment "登录帐号"'),
            ('password', 'varchar(50) default "" comment "帐号密码"'),
            ('userid', 'varchar(20) default "" comment "工号"'),
            ('name', 'varchar(20) default "" comment "姓名"'),
            ('sex', 'varchar(5) default "w" comment "姓别，m男，w女"'),
            ('phone', 'varchar(30) default "" comment "联系电话"'),
            ('email', 'varchar(50) default "" comment "邮箱"'),
            ('role', 'varchar(20) default "" comment "用户的角色，用于个性化菜单、功能、权限等"'),
            ('department', 'varchar(30) default "" comment "部门"'),
            ('state', 'varchar(5) default "t" comment "帐号状态，t为开，f为关，默认t"'),
            ('date', 'varchar(20) default "" comment "创建时间"'),
            ('remarks', 'varchar(100) default "" comment "备注、注释"'),
            ('token', 'varchar(35) default "" comment "token，每次登录时生成"'),
            ('expire', 'varchar(13) default "" comment "过期时间，单位秒"'),
        ],
        'indexes': [
            ('idx_user', 'user')
        ]
}

'''数据字典zydict'''

zydict = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('name', 'varchar(30) default "" comment "数据名称"'),
            ('dictid', 'varchar(20) default "" comment "数据id"'),
            ('type', 'varchar(30) default "" comment "数据分类1"'),
            ('type2', 'varchar(30) default "" comment "数据分类2"'),
            ('type3', 'varchar(30) default "" comment "数据分类3"'),
            ('data', 'text default "{}" comment "配置数据,以json格式存储"')
        ],
        'indexes': [
            ('idx_dictid', 'dictid')
        ]
}


'''知识库rag表'''

rag = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('name', 'varchar(30) default "" comment "知识库名"'),
            ('ragid', 'varchar(20) default "" comment "知识库id"'),
            ('remarks', 'varchar(100) default "" comment "知识库描述"'),
            ('time', 'varchar(20) default "" comment "更新时间"'),
            ('user', 'varchar(50) default "" comment "创建人"'),
            ('department', 'varchar(50) default "" comment "部门"'),
            ('state', 'varchar(5) default "t" comment "知识库状态，t为开，f为关，默认t"'),
            ('db', 'varchar(20) default "milvus" comment "向量数据库名，默认milvus"'),
            ('tb', 'varchar(50) default "" comment "向量表名，一个知识库一张表"'),
            ('tbdata', 'varchar(50) default "" comment "向量表配置，字段、索引等"'),
            # ('field', 'varchar(30) default "ragfield" comment "向量表内的字段定义，默认ragfield,数据字典中的id"'),
            # ('ragindex', 'varchar(30) default "ragindex" comment "向量表内的索引，默认ragindex,数据字典中的id"'),
            # ('bm25fn', 'varchar(30) default "bm25fn" comment "稀疏的函数名，默认bm25fn"'),
            ('embedding', 'varchar(30) default "" comment "向量化的emd模型，数据字典id"'),
            ('rerank', 'varchar(30) default "" comment "重排序模型，数据字典id"'),
            ('search', 'varchar(300) default "{}" comment "搜索方式,json格式"'),
            ('split', 'varchar(300) default "{}" comment "文本切片方式，json格式"'),
            ('type', 'varchar(20) default "in" comment "知识库类型，内部和外部 in/out"'),
            ('mcp', 'varchar(500) default "{}" comment "rag知识库mcp server配置数据"'),
            ('img', 'varchar(5) default "t" comment "是否从文件中提取图片保存并把原图片替换为url，t为开，f为关，默认t"')
        ],
        'indexes': [
            ('idx_ragid', 'ragid'),
            ('idx_appid_user', 'appid, user')
        ]
}


'''文件表'''

file = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('name', 'varchar(200) default "" comment "文件名"'),
            ('fileid', 'varchar(20) default "" comment "文件id，用于关联向量库中的片"'),
            ('ragid', 'varchar(20) default "" comment "知识库id"'),
            ('size', 'varchar(50) default "" comment "知识库id"'),
            ('remarks', 'varchar(100) default "" comment "文件描述"'),
            ('time', 'varchar(20) default "" comment "上传时间"'),
            ('user', 'varchar(50) default "" comment "上传人"'),
            ('department', 'varchar(50) default "" comment "部门"'),
            ('state', 'varchar(5) default "t" comment "知识库状态，t为开，f为关，默认t"'),
            ('analysis', 'varchar(20) default "no analysis" comment "文件的解析状态如：no analysis未解析、OK解析成功、error解析错误、work解析中"'),
            ('reason', 'varchar(200) default "" comment "文件解析失败的原因"'),
            ('split', 'varchar(300) default "{}" comment "文本切片方式,json格式"'),
            ('metadata', 'varchar(200) default "{}" comment "元数据，json格式"'),
            ('type', 'varchar(10) default "file" comment "数据类型，文件/网关url/录入/文件url，默认文件"'),
            ('number', 'varchar(30) default "0" comment "文件切片后的总数量"'),
            ('text', 'text default "" comment "文档文本数据，用于只提取内容不转向量的文件使用"')
        ],
        'indexes': [
            ('idx_fileid', 'fileid'),
            ('idx_appid_user', 'appid, user')
        ]
}


agent = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('type', 'varchar(20) default "agent" comment "智能体类型，agent、flow"'),
            ('name', 'varchar(200) default "" comment "智能体名称"'),
            ('agentid', 'varchar(20) default "" comment "智能体id"'),
            ('icon', 'varchar(200) default "favicon.ico" comment "图标名"'),
            ('remarks', 'varchar(100) default "" comment "智能体描述"'),
            ('time', 'varchar(20) default "" comment "更新时间"'),
            ('user', 'varchar(50) default "" comment "创建人"'),
            ('department', 'varchar(50) default "" comment "部门"'),
            ('state', 'varchar(5) default "t" comment "智能体状态，t为开，f为关，默认t"'),
            ('data', 'text default "{}" comment "智能体配置数据,以json格式存储"'),
            ('mcp', 'varchar(500) default "{}" comment "agent智能体mcp server配置数据"')
        ],
        'indexes': [
            ('idx_agentid', 'agentid'),
            ('idx_appid_user', 'appid, user')
        ]
}



agent_record = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('type', 'varchar(20) default "agent" comment "智能体类型，agent、flow"'),
            ('name', 'varchar(200) default "" comment "智能体名称"'),
            ('agentid', 'varchar(20) default "" comment "智能体id"'),
            ('title', 'varchar(300) default "" comment "此轮对话标题，取第一个问题的前60个字符"'),
            ('start_time', 'varchar(20) default "" comment "开始时间"'),
            ('last_time', 'varchar(20) default "" comment "最后对话时间"'),
            ('user', 'varchar(50) default "" comment "创建人"'),
            ('department', 'varchar(50) default "" comment "部门"'),
            ('session', 'varchar(50) default "" comment "对话id，唯一"'),
            ('tokens', 'int default 0 comment "消耗的tokens数量"'),
            ('data', 'text default "{}" comment "对话和运行数据,以json格式存储"')
        ],
        'indexes': [
            ('idx_session', 'session'),
            ('idx_time_appid_user_agentid', 'start_time, appid, user, agentid')
        ]
}


'''智能BI数据模型表data_model'''

data_set = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('table_name', 'varchar(30) default "" comment "表名"'),
            ('table_label', 'varchar(30) default "" comment "表标签"'),
            ('db_id', 'varchar(20) default "" comment "数据源连接的配置id"'),
            ('type', 'varchar(10) default "table" comment "表类型，实体表table 、视图view"'),
            ('time', 'varchar(20) default "" comment "更新时间"'),
            ('user', 'varchar(50) default "" comment "创建人"'),
            ('data_id', 'varchar(50) default "" comment "数据模型id"'),
            ('data', 'text default "{}" comment "数据模型数据,以json格式存储"')
        ],
        'indexes': [
            ('idx_data_id', 'data_id'),
            ('idx_appid_user', 'appid, user')
        ]
}


'''智能BI数据常用查询表query'''

query = {
        'columns': [
            ('id', 'int auto_increment primary key'),
            ('appid', 'varchar(20) default "" comment "appid"'),
            ('name', 'varchar(30) default "" comment "查询名称"'),
            ('query_id', 'varchar(30) default "" comment "查询id"'),
            ('type', 'varchar(10) default "bi" comment "查询类型，chat(对话)、bi（数据分析）、chart（图表）、dashboard（仪表盘）"'),
            ('time', 'varchar(20) default "" comment "更新时间"'),
            ('user', 'varchar(50) default "" comment "创建人"'),
            ('data', 'text default "{}" comment "查询的配置数据，以json格式存入"')
        ],
        'indexes': [
            ('idx_query_id', 'query_id'),
            ('idx_appid_user', 'appid, user')
        ]
}


'''' 表结构总数据  '''

TABLE_DEFINITIONS = {
    'zydict': zydict,  # 数据字典表
    'company': company,  # 公司表
    'user': user,  # 用户表
    'rag': rag,  # rag知识库表
    'file': file,  # 文件表
    'agent': agent,  # 智能体
    'agent_record': agent_record,  # 智能体对话记录
    'data_set': data_set,  # 数据集表
    'query': query,  # 常用查询表
}


'''连接数据库函数'''

def get_db_connection(database=None):
    """获取数据库连接"""
    config = DB_CONFIG.copy()
    if database:
        config['database'] = database
    return pymysql.connect(**config)


'''检查数据库或创建'''
def check_and_create_database():
    """检查并创建数据库"""
    try:
        # 尝试连接zyai数据库
        conn = get_db_connection(DB_NAME)
        conn.close()
        logger.info(f"数据库 {DB_NAME} 已存在")
    except OperationalError as e:
        # 如果数据库不存在，则创建
        if e.args[0] == 1049:  # Unknown database error code
            logger.info(f"数据库 {DB_NAME} 不存在，正要创建...")
            # jg = input(f'数据库{DB_NAME}, 不存在，是否创建？y/n\n')
            # if jg == 'y':
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.commit()
                logger.info(f"数据库 {DB_NAME} 创建成功")
            conn.close()
            # else:
            #     logger.warning('您选择的是不创建，现在退出数据库初始化流程')
        else:
            logger.error(f"连接数据库时出错: {e}")
            raise


'''检查并创建或更新表'''
def check_and_create_table(table_name, definition):
    """检查并创建或更新表"""
    conn = get_db_connection(DB_NAME)
    try:
        with conn.cursor() as cursor:
            '''检查表'''
            # 检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            exists = cursor.fetchone()

            if not exists:
                # 表不存在，创建新表
                print(f"表 {table_name} 不存在，正要创建...")
                # jg = input(f'表{table_name}, 不存在，是否创建？y/n\n')
                # if jg == 'y':
                columns_sql = ', '.join([f"{col[0]} {col[1]}" for col in definition['columns']])
                create_sql = f"CREATE TABLE {table_name} ({columns_sql})"
                logger.warning('sql='+str(create_sql))
                cursor.execute(create_sql)

                # 创建索引
                for index_name, column in definition['indexes']:
                    sqlindex = f"CREATE INDEX {index_name} ON {table_name} ({column})"
                    logger.warning('sql='+str(sqlindex))
                    cursor.execute(sqlindex)

                conn.commit()
                logger.info(f"表 {table_name} 创建成功")
                # 新表创建时，增加初始化数据
                if table_name in ['user']:
                    # 生成appid
                    appid = 'zyznt' + str(random.randint(100, 999))
                    # 增加公司
                    sql = f"INSERT INTO company (name, appid) VALUES ('卓越智能体', '{appid}');"
                    cursor.execute(sql)
                    # 增加用户
                    sql2 = f"INSERT INTO user (user, password, userid, appid, name, role) VALUES ('admin@zyznt', 'zyzntai', '8000', '{appid}', '管理员', 'admin');"
                    cursor.execute(sql2)
                    conn.commit()
                    # 增加apikey
                    sql3 = """INSERT INTO zydict (appid, name, dictid, type, type2, data) VALUES (%s, 'agent-apikey', 'apikey001', 'key', 'key', '{"apikey": "apikey001", "expire": "000"}');""" % appid
                    cursor.execute(sql3)
                    conn.commit()


            else:
                # 表存在，检查结构是否一致
                logger.info(f"表 {table_name} 已存在，正在检查结构...")
                update_needed = False

                # 获取现有列信息
                cursor.execute(f"DESCRIBE {table_name}")
                allzd = cursor.fetchall()
                # print('所有字段allzd='+str(allzd))
                existing_columns = {row[0]: row[1] for row in allzd}
                # logger.warning(f'现在表{table_name}所有的列='+str(existing_columns))
                # logger.warning(f'现在设计的表{table_name}所有的列='+str(definition['columns']))

                '''检查列，也就是字段'''
                for col_name, col_def in definition['columns']:
                    if col_name not in existing_columns:
                        print(f"列 {col_name} 不存在，正要添加...")
                        # jg = input(f'列{col_name}, 属性={col_def}，是否添加？y/n\n')
                        # if jg == 'y':
                        logger.info(f"添加新列 {col_name} {col_def}")
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                        update_needed = True
                        # else:
                        #     logger.warning(f"您选择的是不添加，现在跳过创建字段{col_name}")
                    # else:
                    #     # 暂不做修改和删除功能
                    #     # 这里可以添加更详细的列定义比较逻辑
                    #     logger.warning(f'未发现不同{col_name}')

                ''''# 检查索引'''
                cursor.execute(f"SHOW INDEX FROM {table_name}")
                allindex = cursor.fetchall()
                # logger.warning(f'现在表{table_name}查到的所有的索引='+str(allindex))
                existing_indexes = {}  # 存储表中现有索引
                for row in allindex:
                    # print(f'索引={row}')
                    # 只关注我们定义的索引，主键索引不看
                    if row[2] not in ["PRIMARY"]: # .startswith('idx_'):  # 主键不检查
                        if row[2] not in existing_indexes:  # 如果索引名不存在，则创建
                            existing_indexes[row[2]] = [[row[4]]]
                        else:  # 如果索引名已存在，则添加列
                            existing_indexes[row[2]] =  existing_indexes[row[2]]+[row[4]]

                # 获取定义的索引
                defined_indexes = definition['indexes']


                # logger.info(f'配置的索引={defined_indexes}')
                # logger.info(f'现有索引={existing_indexes}')

                # 添加缺失的索引  暂不判断修改和删除
                for index_d in defined_indexes:
                    index_name = index_d[0]
                    column = index_d[1]
                    if index_name not in existing_indexes:
                        logger.info(f"添加索引 {index_d} ")
                        # jg = input(f'索引{index_d}, 是否添加？y/n\n')
                        # if jg == 'y':

                        sqlindex = f"CREATE INDEX {index_name} ON {table_name} ({column})"
                        logger.warning('sql='+str(sqlindex))
                        cursor.execute(sqlindex)
                        update_needed = True
                        logger.info(f"添加新索引 {index_name} 成功")
                        # else:
                        #     logger.warning(f"您选择的是不添加，现在跳过创建索引{index_name}")


                # 删除多余的索引（谨慎操作，这里只是示例）
                # for index_name, column in (existing_indexes - defined_indexes):
                #     if index_name.startswith('idx_'):
                #         logger.info(f"删除多余索引 {index_name}")
                #         cursor.execute(f"DROP INDEX {index_name} ON {table_name}")
                #         update_needed = True

                # 修改索引

                if update_needed:
                    conn.commit()
                    logger.info(f"表 {table_name} 结构已更新")
                else:
                    logger.info(f"表 {table_name} 结构无需更新")
            # 检查数据字典，是否需要增加数据
            if table_name in ['zydict']:
                # 查询数据字典中所有的数据，判断是否有缺少的公共数据，如果有添加
                zydict_data = []
                try:
                    # 执行SQL语句
                    sqla = "select * from zydict"
                    dataczydict = msqlc(sqla)
                    if dataczydict:
                        for i in dataczydict:
                            zydict_data.append(i.get('dictid'))
                    else:
                        logger.warning('错误，未查到数据字典数据，reload失败')
                except Exception as sqlload:
                    logger.error("loaddict错误:")
                    logger.error(sqlload)
                    logger.error(traceback.format_exc())
                # 开始添加数据
                for z in dict_data:
                    if z['dictid'] not in zydict_data:
                        sql = sql3sz(z, 'zydict')
                        cursor.execute(sql)
                        conn.commit()
                        logger.info(f'添加数据字典 {z["dictid"]} 成功')
                    else:
                        logger.warning(f'数据字典已存在，无需添加 {z['dictid']}')

    except Exception as e:
        logger.error(f"处理表 {table_name} 时出错: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


'''初始化数据库和表结构,总函数'''
def initialize_database():
    """初始化数据库和表结构"""
    try:
        # 检查并创建数据库
        check_and_create_database()

        # 检查并创建/更新所有表
        for table_name, definition in TABLE_DEFINITIONS.items():
            check_and_create_table(table_name, definition)

        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise



# initialize_database()


'''数据字典公共数据'''

dict_data = [
    {'appid': 'zyggzj', 'name': '管理员', 'dictid': 'admin', 'type': 'role', 'type2': '角色', 'type3': '',
     'data': "{'menu': ['all'], 'filter': {'file': 'adminfile', 'rag': 'adminrag', 'part': 'adminpart', 'agent': 'adminagent'},'tb': {'file': 'khbt', 'rag': 'gdbt'},'form': {'file': 'khxq', 'rag': 'gdxq', 'agent': 'agent_form'}}"},
    {'appid': 'zyggzj', 'name': '知识库检索项', 'dictid': 'adminrag', 'type': 'filter', 'type2': '检索项', 'type3': '',
     'data': '[{"required":"f", "field": "name", "text": "知识库名", "type": "input"}]'},
    {'appid': 'zyggzj', 'name': '文件检索项', 'dictid': 'adminfile', 'type': 'filter', 'type2': '检索项', 'type3': '',
     'data': '[{"required":"f", "field": "name", "text": "文件名", "type": "input"}, {"required":"f", "field": "ragid", "text": "知识库", "type": "input", "show": "f"}, {"required":"t", "field": "appid", "text": "公司id", "type": "input", "show": "f"},{\'field\': \'state\', \'text\': \'状态\', \'default\': \'t\', \'placeholder\': \'文本块的状态\', \'type\': \'select\', \'required\': \'f\', \'update\': \'t\', \'options\': [{\'label\': \'启用\', \'value\': \'t\'}, {\'label\': \'停用\', \'value\': \'f\'}]}]'},
    {'appid': 'zyggzj', 'name': '文件列表表头', 'dictid': 'file_tb', 'type': 'head', 'type2': '表头', 'type3': '',
     'data': '[{"field": "name", "text": "文件名"}, {"field": "analysis", "text": "解析状态"}, {"field": "user", "text": "上传帐号"}, {"field": "size", "text": "大小"}, {"field": "state", "text": "状态"}, {"field": "time", "text": "上传时间"},{"field": "operate", "text": "操作"}]'},
    {'appid': 'zyggzj', 'name': '知识库表单', 'dictid': 'rag_form', 'type': 'form', 'type2': '表单', 'type3': '',
     'data': "[{'field': 'name', 'text': '知识库名称', 'default': '', 'placeholder': '给您的知识库取名', 'type': 'input', 'required': 't', 'update': 't'}, {'field': 'remarks', 'text': '描述介绍', 'default': '', 'placeholder': '介绍下您的知识库', 'type': 'text', 'required': 'f', 'update': 't'}, {'field': 'type', 'text': '内部/外部', 'default': 'in', 'placeholder': '知识库类型', 'type': 'select', 'required': 't', 'update': 't',  'options': [{'label': '内部', 'value': 'in'}, {'label': '外部', 'value': 'out'}]}, {'field': 'split', 'text': '文本分段', 'default': '', 'placeholder': '配置文本分段方法通用、问答、LLM', 'type': 'split', 'required': 't', 'update': 't'}, {'field': 'search', 'text': '知识检索配置', 'default': '', 'placeholder': '向量、全文、向量+全文', 'type': 'search', 'required': 't', 'update': 't'}, {'field': 'embedding', 'text': 'embedding模型', 'default': 'text-embedding-v4', 'placeholder': '把文本块向量化的模型', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': 'bge-large-zh-v1.5', 'value': 'bge-large-zh-v1.5'}, {'label': 'qwen3-embedding', 'value': 'text-embedding-v4'}]}, {'field': 'rerank', 'text': '重排序模型', 'default': '', 'placeholder': '重排序模型', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': 'qwen-rerank重排序', 'value': 'qwen-rerank'}]}, {'field': 'db', 'text': '向量数据库', 'default': 'milvus', 'placeholder': '向量数据库', 'type': 'select', 'required': 't', 'update': 't', 'options': [{'label': 'milvus向量数据库', 'value': 'milvus'}]}, {'field': 'tbdata', 'text': '向量表设计', 'default': 'm_tbdata', 'placeholder': '向量表字段索引配置', 'type': 'select', 'required': 't', 'update': 't', 'options': [{'label': 'milvus向量表配置字典', 'value': 'm_tbdata'}]}]"},
    {'appid': 'zyggzj', 'name': '向量数据库表配置', 'dictid': 'm_tbdata', 'type': 'db', 'type2': '向量表', 'type3': '',
     'data': '{\'tbdata\': "{\'fields\': [{\'name\': \'id\', \'description\': \'主键id\', \'type\': DataType.INT64, \'is_primary\': True, \'auto_id\': True},{\'name\': \'vector\', \'description\': \'向量数据\', \'type\': DataType.FLOAT_VECTOR},{\'name\':\'sparse\', \'description\': \'稀疏向量\',\'type\': DataType.SPARSE_FLOAT_VECTOR},{\'name\':\'text\', \'description\': \'文本数据\',\'type\': DataType.VARCHAR, \'max_length\': 10000, \'default_value\': \'\'},{\'name\':\'s_text\', \'description\': \'稀疏向量文本\',\'type\': DataType.VARCHAR, \'max_length\': 10000, \'default_value\': \'\',\'enable_analyzer\':True},{\'name\':\'q_text\', \'description\': \'问答模式的问文本，答在text\',\'type\': DataType.VARCHAR, \'max_length\': 10000, \'default_value\': \'\'},{\'name\':\'fileid\', \'description\': \'文件id，用于把块关联到文件\',\'type\': DataType.VARCHAR, \'max_length\': 30, \'default_value\': \'\'},{\'name\':\'state\', \'description\': \'文本块状态，t为开，f为关\',\'type\': DataType.VARCHAR, \'max_length\': 3, \'default_value\': \'t\'},{\'name\':\'keyword\', \'description\': \'关键词\',\'type\': DataType.VARCHAR, \'max_length\': 100, \'default_value\': \'\'},{\'name\':\'metadata\', \'description\': \'元数据，json格式，可用于检索\',\'type\': DataType.JSON, \'max_length\': 200, \'nullable\':True},],\'index_params\':[{\'field_name\': \'vector\', \'index_type\': \'FLAT\', \'metric_type\':\'COSINE\'},{\'field_name\': \'sparse\', \'index_type\': \'SPARSE_INVERTED_INDEX\', \'metric_type\':\'BM25\'},{\'field_name\': \'state\', \'index_type\': \'\'},{\'field_name\': \'fileid\', \'index_type\': \'\'}],\'enable_dynamic_field \': True,\'functions\': {\'name\': \'bm25\', \'description\': \'稀疏向量功能函数\', \'type\': FunctionType.BM25, \'input_field_names\': [\'s_text\'],\'output_field_names\': [\'sparse\'], \'params\': {}}}"}'},
    {'appid': 'zyggzj', 'name': '文本段检索项', 'dictid': 'adminpart', 'type': 'filter', 'type2': '检索项', 'type3': '',
     'data': '[{"required":"t", "field": "fileid", "text": "文件id", "type": "input", "show": "f"},  {\'field\': \'state\', \'text\': \'状态\', \'default\': \'t\', \'placeholder\': \'文本块的状态\', \'type\': \'select\', \'required\': \'f\', \'update\': \'t\', \'options\': [{\'label\': \'启用\', \'value\': \'t\'}, {\'label\': \'停用\', \'value\': \'f\'}]}]'},
    {'appid': 'zyggzj', 'name': '文件格式', 'dictid': 'fileformat', 'type': 'fileformat', 'type2': '文件格式',
     'type3': '',
     'data': "{'docx': 'read_docx', 'pdf': 'read_pdf', 'xlsx': 'read_excel', 'pptx': 'read_ppt', 'csv': 'read_csv', 'txt': 'read_file', 'py': 'read_file', 'docx_img': 'read_docx_img', 'size': 10}"},
    {'appid': 'zyggzj', 'name': '文件模块', 'dictid': 'filemod', 'type': 'filemod', 'type2': '文件模块', 'type3': '',
     'data': "[{'fun_name': 'read_file', 'dir': 'mod.file2text.file2text'}, {'fun_name': 'read_pdf', 'dir': 'mod.file2text.file2text'}, {'fun_name': 'read_docx', 'dir': 'mod.file2text.file2text'}, {'fun_name': 'read_docx_img', 'dir': 'mod.file2text.file2text'}, {'fun_name': 'read_excel', 'dir': 'mod.file2text.file2text'}, {'fun_name': 'read_ppt', 'dir': 'mod.file2text.file2text'},{'fun_name': 'read_csv', 'dir': 'mod.file2text.file2text'}]"},
    {'appid': 'zyggzj', 'name': 'agent智能体表单', 'dictid': 'agent_form', 'type': 'form', 'type2': '表单', 'type3': '',
     'data': "[{'field': 'name', 'text': '智能体名称', 'default': '', 'placeholder': '给您的智能体取名', 'type': 'input', 'required': 't', 'update': 't'}, {'field': 'remarks', 'text': '描述介绍', 'default': '', 'placeholder': '介绍下您的智能体', 'type': 'text', 'required': 'f', 'update': 't'}, {'field': 'agentid', 'text': '智能体id', 'default': '', 'placeholder': '智能体id', 'type': 'input', 'required': 'f', 'update': 't', 'show': 'f'}, {'field': 'icon', 'text': '智能体图标', 'default': 'https://zy-wendang.oss-cn-hangzhou.aliyuncs.com/img/ai-avatar.svg', 'placeholder': '图标', 'type': 'upload', 'required': 'f', 'update': 't'}, {'field': 'user', 'text': '创建人', 'default': '', 'placeholder': '创建人', 'type': 'input', 'required': 'f', 'update': 't', 'show': 'f'}, {'field': 'appid', 'text': '公司id', 'default': '', 'placeholder': '公司id', 'type': 'input', 'required': 'f', 'update': 't', 'show': 'f'}, {'field': 'time', 'text': '更新时间', 'default': '', 'placeholder': '更新时间', 'type': 'input', 'required': 'f', 'update': 't', 'show': 'f'}, {'field': 'data', 'text': '配置数据', 'default': '', 'placeholder': '智能体配置', 'type': 'data', 'required': 'f', 'update': 't', 'data': [{'field': 'prompt', 'text': '提示词', 'default': '', 'placeholder': '智能体提示词', 'type': 'text', 'required': 't', 'update': 't'}, {'field': 'prologue', 'text': '开场白', 'default': '', 'placeholder': '开场白，对话开始时智能体会先发送开场白内容', 'type': 'text', 'required': 'f', 'update': 't'}, {'field': 'context', 'text': 'llm上下文', 'default': '', 'placeholder': 'llm上下文，可以增加知识、行业特定专用词、事物逻辑等任何帮助大模型理解业务场景的内容', 'type': 'text', 'required': 'f', 'update': 't'}, {'field': 'memory', 'text': '多轮对话', 'default': 't', 'placeholder': '记忆对话', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]}, {'field': 'llm', 'text': 'LLM大模型', 'default': '', 'placeholder': '选择大模型', 'type': 'select', 'required': 't', 'update': 't', 'options': [{'label': 'qwen-plus', 'value': 'qwen-plus'}, {'label': 'deepseek-v3', 'value': 'deepseek-v3'}]}, {'field': 'tools', 'text': 'MCP工具', 'default': '', 'placeholder': '工具列表，多选', 'type': 'select', 'required': 'f', 'update': 't', 'options': [{'label': '开启', 'value': 't'}, {'label': '关闭', 'value': 'f'}]}, {'field': 'temperature', 'text': '回复热度', 'default': '0.7', 'placeholder': 'LLM大模型生成文本的多样性，取值范围： [0, 2)，值越高文本越多样', 'type': 'input', 'required': 'f', 'update': 't'}, {'field': 'rag', 'text': 'rag知识库', 'default': '', 'placeholder': '知识库列表，多选', 'type': 'select', 'required': 'f', 'update': 't', 'options': []}, {'field': 'file', 'text': '文件知识库', 'default': '', 'placeholder': '文件列表，多选,所有文件总字数建议不超过5000', 'type': 'upload', 'required': 'f', 'update': 't', 'options': []}, {'field': 'website', 'text': '网页搜索', 'default': '', 'placeholder': '网页搜索知识', 'type': 'select', 'required': 'f', 'update': 't', 'options': []}, {'field': 'asr', 'text': '语音识别模型', 'default': '', 'placeholder': '语音获取和识别', 'type': 'select', 'required': 'f', 'update': 't', 'options': []}, {'field': 'tts', 'text': 'TTS模型', 'default': '', 'placeholder': '文本转语音', 'type': 'select', 'required': 'f', 'update': 't', 'options': []}]}]"},
    {'appid': 'zyggzj', 'name': '数据字典检索项', 'dictid': 'adminzydict', 'type': 'filter', 'type2': '检索项',
     'type3': '',
     'data': '[{"required":"f", "field": "name", "text": "名称", "type": "input", \'default\': \'\'}, {"required":"t", "field": "type", "text": "数据类型", "type": "input", \'default\': \'llm\'}, {"required":"t", "field": "appid", "text": "公司", "type": "input", \'default\': \'zyggzj\'}]'},
    {'appid': 'zyggzj', 'name': '数据字典分类菜单', 'dictid': 'adminmenu', 'type': 'menu', 'type2': '菜单', 'type3': '',
     'data': '[{\'label\': \'LLM大模型\', \'value\': \'llm\', \'placeholder\': """LLM大模型配置:\\n skd： openai、ollama或其它支持的类型，默认openai，必填  \\n url：连接LLM的url地址，必填 \\n apikey：LLM平台鉴权的api_key，必填 \\n module：LLM模型名称，必填 \\n maxtext：模型支持的最大上下文，非必填 \\n provider：模型提供商，非必填 \\n remarks：模型描述，非必填 \\n 配置示例：{"sdk": "openai", "sdkdir": "", "url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "apikey": "***************b82cf", "module": "qwen-plus", "maxtext": "", "provider": "阿里云百炼", "remarks": ""}"""}, {\'label\': \'embd模型\', \'value\': \'embd\', \'placeholder\': \'embd向量模型配置:\\n\'}, {\'label\': \'MCP服务\', \'value\': \'mcp\', \'placeholder\': \'mcp服务配置:\'}, {\'label\': \'检索项\', \'value\': \'filter\', \'placeholder\': \'动态检索项配置:\\n\'}, {\'label\': \'动态表单\', \'value\': \'form\', \'placeholder\': \'动态表单配置:\'}]'},
    {'appid': 'zyggzj', 'name': '开始', 'dictid': 'start_mod', 'type': 'mod', 'type2': '组件', 'type3': '',
     'data': "{'type': 'mod', 'module': 'start_mod', 'module_name': '开始', 'description': '开始，初始化系统变量和自定义变量，创建会话工作id，初始化空间', 'input': '', 'output': ''}"},
    {'appid': 'zyggzj', 'name': '结束', 'dictid': 'end_mod', 'type': 'mod', 'type2': '组件', 'type3': '',
     'data': "{'type': 'mod', 'module': 'end_mod', 'module_name': '结束', 'description': '结束，结束会话，保存会话记录，清空内存运行数据', 'input': '', 'output': ''}"},
    {'appid': 'zyggzj', 'name': 'LLM', 'dictid': 'llm_mod', 'type': 'mod', 'type2': '组件', 'type3': '',
     'data': "{'type': 'mod', 'module': 'llm_mod', 'module_name': 'LLM大模型', 'description': 'LLM大模型调用并执行任务', 'input': {'user_input': '', 'llm': 'LLM大模型', 'prompt': '提示词', 'tools': []}, 'output': {'content': ''}}"},
    {'appid': 'zyggzj', 'name': '流组件运行模块', 'dictid': 'flowmod', 'type': 'flowmod', 'type2': '组件模块',
     'type3': '',
     'data': "[{'fun_name': 'start_mod', 'dir': 'mod.flow_mod'}, {'fun_name': 'end_mod', 'dir': 'mod.flow_mod'}, {'fun_name': 'param_data', 'dir': 'mod.flow_mod'}, {'fun_name': 'llm_mod', 'dir': 'mod.flow_mod'}, {'fun_name': 'http_mod', 'dir': 'mod.flow_mod'}, {'fun_name': 'if_mod', 'dir': 'mod.flow_mod'}, {'fun_name': 'data_processing', 'dir': 'mod.flow_mod'}, {'fun_name': 'code_mod', 'dir': 'mod.flow_mod'}, {'fun_name': 'mcp_mod', 'dir': 'mod.flow_mod'}]"},
    {'appid': 'zyggzj', 'name': '智能体检索项', 'dictid': 'adminagent', 'type': 'filter', 'type2': '检索项',
     'type3': '', 'data': '[{"required":"f", "field": "name", "text": "智能体名称", "type": "input"}]'},
    {'appid': 'zy001', 'name': '时间mcp', 'dictid': 'zytime', 'type': 'mcp', 'type2': 'mcp',
     'type3': '获取当前服务器时间', 'data': '{"mcpServers": {"zytime": {"url": "http://127.0.0.1:53003/mcp"}}}'},
    {'appid': 'zyggzj', 'name': '我的统计', 'dictid': '7day', 'type': 'report', 'type2': 'report', 'type3': '',
     'data': '{"sqla": "SELECT dates.date AS `date`, COUNT(ar.id) AS `chat`, COUNT(DISTINCT ar.user) AS `user`FROM (SELECT CURDATE() - INTERVAL 6 DAY AS date UNION SELECT CURDATE() - INTERVAL 5 DAY UNION SELECT CURDATE() - INTERVAL 4 DAY UNION SELECT CURDATE() - INTERVAL 3 DAY UNION SELECT CURDATE() - INTERVAL 2 DAY UNION SELECT CURDATE() - INTERVAL 1 DAY UNION SELECT CURDATE()) AS dates LEFT JOIN agent_record ar ON DATE(ar.start_time) = dates.date AND ar.appid = \'zy001\' GROUP BY dates.date ORDER BY dates.date;"}'},
    {'appid': 'zyggzj', 'name': '文本块表单', 'dictid': 'part_form', 'type': 'form', 'type2': '表单', 'type3': '',
     'data': '[{\'field\': \'fileid\', \'text\': \'文件id\', \'default\': \'\', \'placeholder\': \'文件id\', \'type\': \'input\', \'required\': \'t\', \'update\': \'t\',\'show\': \'f\'},{\'field\': \'text\', \'text\': \'文本\', \'default\': \'\', \'placeholder\': \'文本内容\', \'type\': \'text\', \'required\': \'t\', \'update\': \'t\'},{\'field\': \'q_text\', \'text\': \'问文本\', \'default\': \'\', \'placeholder\': \'对文本内容的常用提问或对话，可以填多个，此项有值时，向量检索相似度时以此项内容为准，结果以文本内容为准\', \'type\': \'text\', \'required\': \'f\', \'update\': \'t\'},{\'field\': \'state\', \'text\': \'状态\', \'default\': \'t\', \'placeholder\': \'文本状态\', \'type\': \'select\', \'required\': \'t\', \'update\': \'t\', \'options\': [{\'label\': \'启用\', \'value\': \'t\'}, {\'label\': \'停用\', \'value\': \'f\'}]},{\'field\': \'keyword\', \'text\': \'关键词\', \'default\': \'\', \'placeholder\': \'定义文本段的关键词，检索时可用\', \'type\': \'input\', \'required\': \'f\', \'update\': \'t\'},{\'field\': \'metadata\', \'text\': \'元数据\', \'default\': \'{"type": "手动增加"}\', \'placeholder\': \'文本元数据配置，json格式，内容可自定义\', \'type\': \'input\', \'required\': \'f\', \'update\': \'t\'}]'},
    {'appid': 'zy001', 'name': 'rag-mcp知识库', 'dictid': 'rag1753351498533', 'type': 'mcp', 'type2': 'mcp',
     'type3': '',
     'data': '{"mcpServers": {"rag1753351498533": {"url": "http://127.0.0.1:53005/mcp?type=rag&ragid=rag1753351498533&apikey=apikey001"}}}'},
    {'appid': 'zyggzj', 'name': '智能数据检索项', 'dictid': 'query', 'type': 'filter', 'type2': '检索项', 'type3': '',
     'data': '[{"required":"f", "field": "name", "text": "数据名称", "type": "input", \'default\': \'\'}, {"required":"f", "field": "type", "text": "数据类型", "type": "input", \'default\': \'\'}, {"required":"t", "field": "appid", "text": "公司", "type": "input", \'default\': \'zy001\', \'show\': \'f\'},{"required":"f", "field": "user", "text": "创建用户", "type": "input", \'default\': \'\'}]'},
    {'appid': 'zyggzj', 'name': '智能数据表头', 'dictid': 'query_tb', 'type': 'head', 'type2': '表头', 'type3': '',
     'data': '[{"field": "name", "text": "数据名称"}, {"field": "type", "text": "数据类型",\'options\': [{\'label\': \'AISQL\', \'value\': \'bi\'}, {\'label\': \'图表\', \'value\': \'chart\'}, {\'label\': \'数据大屏\', \'value\': \'dashboard\'}]}, {"field": "time", "text": "更新时间"}, {"field": "user", "text": "创建人"}, {"field": "operate", "text": "操作"}]'},
]

