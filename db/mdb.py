import pymysql
from pymysql.constants import CLIENT
from pymysql.err import OperationalError, ProgrammingError
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.warning('*****卓越数据库初始化程序*****')


# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Dws666888',
    'port': 3306
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
            ('type', 'varchar(20) default "in" comment "知识库类型，内部和外部 in/out"')
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
            ('analysis', 'varchar(10) default "未解析" comment "文件的解析状态如：68%、完成、未解析"'),
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
            ('icon', 'varchar(20) default "favicon.ico" comment "图标名"'),
            ('remarks', 'varchar(100) default "" comment "智能体描述"'),
            ('time', 'varchar(20) default "" comment "更新时间"'),
            ('user', 'varchar(50) default "" comment "创建人"'),
            ('department', 'varchar(50) default "" comment "部门"'),
            ('state', 'varchar(5) default "t" comment "智能体状态，t为开，f为关，默认t"'),
            ('data', 'text default "{}" comment "智能体配置数据,以json格式存储"')
        ],
        'indexes': [
            ('idx_agentid', 'agentid'),
            ('idx_appid_user', 'appid, user')
        ]
}




'''' 表结构总数据  '''

TABLE_DEFINITIONS = {
    'company': company,  # 公司表
    'user': user,  # 用户表
    'zydict': zydict,  # 数据字典表
    'rag': rag,  # rag知识库表
    'file': file,  # 文件表
    'agent': agent,  # 智能体
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
            jg = input(f'数据库{DB_NAME}, 不存在，是否创建？y/n\n')
            if jg == 'y':
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    conn.commit()
                    logger.info(f"数据库 {DB_NAME} 创建成功")
                conn.close()
            else:
                logger.warning('您选择的是不创建，现在退出数据库初始化流程')
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
                jg = input(f'表{table_name}, 不存在，是否创建？y/n\n')
                if jg == 'y':
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
            else:
                # 表存在，检查结构是否一致
                logger.info(f"表 {table_name} 已存在，正在检查结构...")
                update_needed = False

                # 获取现有列信息
                cursor.execute(f"DESCRIBE {table_name}")
                allzd = cursor.fetchall()
                print('所有字段allzd='+str(allzd))
                existing_columns = {row[0]: row[1] for row in allzd}
                logger.warning(f'现在表{table_name}所有的列='+str(existing_columns))
                logger.warning(f'现在设计的表{table_name}所有的列='+str(definition['columns']))

                '''检查列，也就是字段'''
                for col_name, col_def in definition['columns']:
                    if col_name not in existing_columns:
                        print(f"列 {col_name} 不存在，正要添加...")
                        jg = input(f'列{col_name}, 属性={col_def}，是否添加？y/n\n')
                        if jg == 'y':
                            logger.info(f"添加新列 {col_name} {col_def}")
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                            update_needed = True
                        else:
                            logger.warning(f"您选择的是不添加，现在跳过创建字段{col_name}")
                    else:
                        # 暂不做修改和删除功能
                        # 这里可以添加更详细的列定义比较逻辑
                        logger.warning(f'未发现不同{col_name}')

                ''''# 检查索引'''
                cursor.execute(f"SHOW INDEX FROM {table_name}")
                allindex = cursor.fetchall()
                logger.warning(f'现在表{table_name}查到的所有的索引='+str(allindex))
                existing_indexes = {}  # 存储表中现有索引
                for row in allindex:
                    print(f'索引={row}')
                    # 只关注我们定义的索引，主键索引不看
                    if row[2] not in ["PRIMARY"]: # .startswith('idx_'):  # 主键不检查
                        if row[2] not in existing_indexes:  # 如果索引名不存在，则创建
                            existing_indexes[row[2]] = [[row[4]]]
                        else:  # 如果索引名已存在，则添加列
                            existing_indexes[row[2]] =  existing_indexes[row[2]]+[row[4]]

                # 获取定义的索引
                defined_indexes = definition['indexes']


                logger.info(f'配置的索引={defined_indexes}')
                logger.info(f'现有索引={existing_indexes}')

                # 添加缺失的索引  暂不判断修改和删除
                for index_d in defined_indexes:
                    index_name = index_d[0]
                    column = index_d[1]
                    if index_name not in existing_indexes:
                        logger.info(f"添加索引 {index_d} ")
                        jg = input(f'索引{index_d}, 是否添加？y/n\n')
                        if jg == 'y':

                            sqlindex = f"CREATE INDEX {index_name} ON {table_name} ({column})"
                            logger.warning('sql='+str(sqlindex))
                            cursor.execute(sqlindex)
                            update_needed = True
                            logger.info(f"添加新索引 {index_name} 成功")
                        else:
                            logger.warning(f"您选择的是不添加，现在跳过创建索引{index_name}")


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


if __name__ == "__main__":
    initialize_database()





