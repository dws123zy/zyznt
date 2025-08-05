# _*_coding:utf-8 _*_

import traceback
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import json
from sqlalchemy import create_engine, MetaData, inspect, Table, Column, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import CreateTable, CreateIndex, ForeignKeyConstraint
from sqlalchemy.dialects import postgresql, mysql, sqlite
from sqlalchemy.types import TypeDecorator

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import RelationshipProperty  # 导入正确的类型


'''日志'''

logger = logging.getLogger(__name__)



"""测试db_url连接性"""

def db_connection(db_url, timeout=30):
    """测试db_url连接性"""
    engine = ''
    try:
        # 创建引擎（不立即连接）
        engine = create_engine(db_url, connect_args={"connect_timeout": int(timeout)})

        # 尝试建立连接
        with engine.connect() as conn:
            return 'OK'
    except OperationalError as e:
        return str(e)
    finally:
        # 清理引擎资源
        engine.dispose()


'''获取源数据库中的表结构、视图、外键、sql dll等信息'''

def export_db_schema(db_url, timeout=30):
    """
    获取源数据库中的表结构、视图、外键、sql dll等信息
    :param db_url: 数据库连接字符串
    """
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": int(timeout)})
        inspector = inspect(engine)
        metadata = MetaData()

        # 反射整个数据库
        metadata.reflect(engine)

        # 使用自定义命名规则解决属性冲突
        def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
            # 为关系属性添加后缀避免与列名冲突
            return referred_cls.__name__.lower() + "_rel"

        def name_for_collection_relationship(base, local_cls, referred_cls, constraint):
            # 为集合关系属性添加后缀
            return referred_cls.__name__.lower() + "s_rel"
        # 使用automap自动生成基础映射
        Base = automap_base(metadata=metadata)
        Base.prepare(
            name_for_scalar_relationship=name_for_scalar_relationship,
            name_for_collection_relationship=name_for_collection_relationship
        )

        # 收集数据库结构信息
        schema_data = {
            "tables": {},
            "views": {},
            "dialect": engine.dialect.name
        }

        # 处理表结构
        for table_name in inspector.get_table_names():
            table = metadata.tables[table_name]

            # 收集列信息（包含注释）
            columns = []
            for column in table.columns:
                comment = column.comment if column.comment else ""
                col_info = {
                    "name": column.name,
                    "type": str(column.type),
                    "primary_key": column.primary_key,
                    "nullable": column.nullable,
                    "default": str(column.default) if column.default else '',
                    "autoincrement": column.autoincrement,
                    "comment": comment,  # 添加列注释
                    "label": comment  # 标签
                }
                columns.append(col_info)

            # 收集索引信息
            indexes = []
            for index in inspector.get_indexes(table_name):
                index_info = {
                    "name": index["name"],
                    "columns": index["column_names"],
                    "unique": index["unique"],
                    # "type": index.get("type", "index")
                }
                indexes.append(index_info)

            # 收集外键信息
            foreign_keys = []
            for fk in inspector.get_foreign_keys(table_name):
                print('外键=', fk)
                fk_info = {
                    "name": fk["name"],
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                    "options": fk["options"]
                }
                foreign_keys.append(fk_info)

            # 收集约束信息、关系映射
            relationships = generate_relationships(Base, table_name)

            # 收集表注释
            table_comment = inspector.get_table_comment(table_name) or {}

            schema_data["tables"][table_name] = {
                "columns": columns,
                "table_label": table_comment.get("text", ""),
                "table_name": table_name,
                "indexes": indexes,
                "foreign_keys": foreign_keys,
                "relationships": relationships,
                "comment": table_comment.get("text", ""),
                "ddl": str(CreateTable(table).compile(engine)),
                "type": "table",
            }

        # 处理视图（包含注释）
        for view_name in inspector.get_view_names():
            # print("视图= ", view_name)
            view_info = {
                "view_name": view_name,
                "view_label": inspector.get_table_comment(view_name).get("text", ""),
                "definition": inspector.get_view_definition(view_name),
                "comment": inspector.get_table_comment(view_name).get("text", ""),
                "columns": [],
                "dependencies": [],
                "type": "view"
            }

            # 获取列详细信息
            for column in inspector.get_columns(view_name):
                col_info = {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": column["default"],
                    # "comment": inspector.get_column_comment(view_name, column["name"])
                }
                view_info["columns"].append(col_info)
            schema_data["views"][view_name] = view_info

        # print("数据库结构：", schema_data)
        return schema_data
    except Exception as e:
        logger.warning(f'获取数据库结构数据失败: {e}，{traceback.format_exc()}')
        return f'获取数据库结构数据失败: {e}'


'''获取映射关系'''

def generate_relationships(base, table_name):
    try:
        Base = base
        # 获取对应的ORM类（处理可能的命名不一致）
        model_class = None
        for cls in Base.classes:
            if cls.__table__.name == table_name:
                model_class = cls
                break

        if not model_class:
            return ''

        # 收集关系信息
        relationships_info = []
        # 检查所有类属性
        for attr_name in dir(model_class):
            # 跳过特殊方法和内置属性
            if attr_name.startswith('__') or attr_name in ['metadata', 'registry']:
                continue

            attr = getattr(model_class, attr_name)
            # 使用RelationshipProperty检查关系属性
            if hasattr(attr, 'property') and isinstance(attr.property, RelationshipProperty):
                rel_prop = attr.property

                # 获取目标模型名称
                target_model = rel_prop.entity.class_.__name__

                # 确定关系类型
                rel_type = "many-to-one"
                if hasattr(rel_prop, 'direction'):
                    if rel_prop.direction.name == "ONETOMANY":
                        rel_type = "one-to-many"
                    elif rel_prop.direction.name == "MANYTOMANY":
                        rel_type = "many-to-many"

                # 获取关联列信息
                local_cols = []
                if rel_prop.local_columns:
                    local_cols = [c.name for c in rel_prop.local_columns]

                remote_cols = []
                if rel_prop.remote_side:
                    remote_cols = [c.name for c in rel_prop.remote_side]

                rel_info = {
                    "name": attr_name,
                    "type": rel_type,
                    "target_model": target_model,
                    "local_columns": local_cols,
                    "remote_columns": remote_cols
                }
                # 添加到关系信息列表
                relationships_info.append(rel_info)


        # 返回关系信息
        return relationships_info
    except Exception as e:
        logger.warning(f'获取映射关系数据失败: {e}，{traceback.format_exc()}')
        return f"获取映射关系数据失败:{str(e)}"






