# _*_coding:utf-8 _*_

import pymysql
import traceback
import time
from pymysql.converters import escape_string
import logging
import json
import base64


'''日志'''

logger = logging.getLogger(__name__)


'''mysql函数,传入sql命令，返回数据和状态，数据已按列表字典组合完成'''


'''mysql查询执行函数，不带获取总条数'''

def msqlc(sqlcmd, mysqlip='127.0.0.1', dataname='zyai'):
    try:
        conn = pymysql.connect(host=mysqlip,
                               user="root",
                               password="Dws666888",
                               port=3306,  # 端口
                               database=dataname,
                               charset="utf8")
        cur = conn.cursor()
        try:
            # 执行SQL语句
            cur.execute(sqlcmd)
            desc = cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
            cur.close()
            conn.close()
            if desc:
                datac = [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]  # 列表表达式把数据组装起来
                return datac
            else:
                return 1

        except Exception as sqlerr2:
            cur.close()
            conn.close()
            # print("zysql错误:")
            # print(sqlerr2)
            # print(traceback.format_exc())
            logger.error(sqlcmd + '\n' + str(traceback.format_exc()))
            return 0
    except Exception as sqlerr:
        # print("zysql链接错误:")
        # print(sqlerr)
        # print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return 0


'''查询+获取总条数'''

def msqlcxnum(sqlcmd, mysqlip='127.0.0.1', dataname='zyai'):
    try:
        # print('sqlcmd=', sqlcmd)
        conn = pymysql.connect(host=mysqlip,
                               user="root",
                               password="Dws666888",
                               port=3306,  # 端口
                               database=dataname,
                               charset="utf8")
        cur = conn.cursor()
        try:
            cur.execute(sqlcmd)
            desc = cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
            datac = [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]  # 列表表达式把数据组装起来

            cur.execute("SELECT FOUND_ROWS() as total")
            results = cur.fetchall()
            cur.close()
            conn.close()

            return datac, results[0][0]

        except Exception as sqlerr2:
            cur.close()
            conn.close()
            # print("zysqlnum错误:")
            # print(sqlerr2)
            # print(traceback.format_exc())
            logger.error(sqlcmd + '\n' + str(traceback.format_exc()))
            return 0, 0
    except Exception as sqlerr:
        # print("zysql链接错误:")
        # print(sqlerr)
        # print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return 0, 0


'''插入、删除、修改用，带提交确认'''

def msqlzsg(sqlcmd, mysqlip='127.0.0.1', dataname='zyai'):
    try:
        # print('sqlcmd=', sqlcmd)
        conn = pymysql.connect(host=mysqlip,
                               user="root",
                               password="Dws666888",
                               port=3306,  # 端口
                               database=dataname,
                               charset="utf8")
        cur = conn.cursor()
        try:
            # 执行SQL语句,增加执行状态
            jg = cur.execute(sqlcmd)
            conn.commit()  # 二次确认
            cur.close()
            conn.close()
            return jg

        except Exception as sqlerr2:
            try:
                conn.rollback()  # 发生错误时回滚
            except Exception as sqlerrback:
                # print("回滚错误:")
                # print(sqlerrback)
                logger.error(sqlcmd + '\n' + str(traceback.format_exc()))
            cur.close()
            conn.close()
            # print("zysql错误:")
            # print(sqlerr2)
            logger.error(sqlcmd + '\n' + str(traceback.format_exc()))
            return 0
    except Exception as sqlerr:
        # print("zysql链接错误:")
        # print(sqlerr)
        # print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return 0


'''
****************
**sql命令组合专区*
****************
'''


'''sql查组合'''

def sqlc(data, name, p, lm, syx):
    try:
        # sql查的基础语句，放入表名name
        sq1 = "select SQL_CALC_FOUND_ROWS * from %s where " % name

        # 加上索引检索或需要放前面的检索
        sq2 = ""
        if syx:
            for s in syx:
                if syx[s]:
                    if sq2:
                        sq2 = sq2 + " and %s='%s'" % (s, syx[s])
                    else:
                        sq2 = "%s='%s'" % (s, syx[s])
        # 组合data里的检索项
        if data:
            for c in data:
                if data[c]:
                    if c in ['startTime', 'oDate2', 'uEndDate', 'oDate', 'uDate', 'cDate', 'evtime', 'plandate',
                             'logtime', 'cjtime']:
                        sq2 = sq2 + " and %s >='%s %s' and %s <='%s %s'" % (c, data[c][0], '00:00:00', c, data[c][1], '23:59:59')
                    # elif c in ['plandate']:  # 联系计划时间，迁移到上面，实现日期区间
                    #     sq2 = sq2 + " and %s >='%s %s'" % (c, data[c], '00:00:00')
                    elif c in ['billsec']:
                        sq2 = sq2 + " and %s >=%s" % (c, data[c])
                    else:
                        sq2 = sq2 + " and %s='%s'" % (c, data[c])

        fy = ""  # 处理分页，如有的话
        if p and lm:
            n = int(lm)
            m = (int(p) - 1) * n
            fy = " order by id desc limit %s,%s" % (m, n)
        print('组合后的sql=', sq1+sq2+fy)
        return sq1+sq2+fy
    except Exception as ek:
        print("sql查询组合命令错误:")
        print(ek)
        return 0


'''sql查询组合,时间带时分秒、支持多选[]的函数'''


def sqlc3(data, name, p, lm, syx):
    try:
        # sql查的基础语句，放入表名name
        sq1 = "select SQL_CALC_FOUND_ROWS * from %s where " % name

        # 加上索引检索或需要放前面的检索
        sq2 = ""
        if syx:
            for s in syx:
                if syx[s]:
                    if sq2:
                        sq2 = sq2 + " and %s='%s'" % (s, syx[s])
                    else:
                        sq2 = "%s='%s'" % (s, syx[s])
        # 组合data里的检索项
        if data:
            for c in data:
                if data[c]:
                    if c in ['start_time']:
                        if sq2:
                            sq2 = sq2 + " and %s >='%s' and %s <='%s'" % (c, data[c][0], c, data[c][1])
                        else:
                            sq2 = "%s >='%s' and %s <='%s'" % (c, data[c][0], c, data[c][1])
                    else:
                        if sq2:
                            sq2 = sq2 + " and %s='%s'" % (c, data[c])
                        else:
                            sq2 = "%s='%s'" % (c, data[c])

        fy = ""  # 处理分页，如有的话
        if p and lm:
            n = int(lm)
            m = (int(p) - 1) * n
            fy = " order by id desc limit %s,%s" % (m, n)
        print('组合后的sql=', sq1+sq2+fy)
        return sq1+sq2+fy
    except Exception as ek:
        print("sql查询组合命令错误:")
        print(ek)
        print(traceback.format_exc())
        return ''


'''sql查询组合,时间带时分秒、支持多选[]的函数，name自动模糊查询'''


def sqlc3like(data, name, p, lm, syx):
    try:
        # sql查的基础语句，放入表名name
        sq1 = "select SQL_CALC_FOUND_ROWS * from %s where " % name

        # 加上索引检索或需要放前面的检索
        sq2 = ""
        if syx:
            for s in syx:
                if syx[s]:
                    if sq2:
                        sq2 = sq2 + " and %s='%s'" % (s, syx[s])
                    else:
                        sq2 = "%s='%s'" % (s, syx[s])
        # 组合data里的检索项
        if data:
            for c in data:
                if data[c]:
                    if c in ['start_time']:
                        if sq2:
                            sq2 = sq2 + " and %s >='%s' and %s <='%s'" % (c, data[c][0], c, data[c][1])
                        else:
                            sq2 = "%s >='%s' and %s <='%s'" % (c, data[c][0], c, data[c][1])
                    if c in ['name']:
                        if sq2:
                            sq2 = sq2 + " and %s like '%s'" % (c, '%' + data[c] + '%')
                        else:
                            sq2 = "%s like '%s'" % (c, '%' + data[c] + '%')
                    else:
                        if sq2:
                            sq2 = sq2 + " and %s='%s'" % (c, data[c])
                        else:
                            sq2 = "%s='%s'" % (c, data[c])

        fy = ""  # 处理分页，如有的话
        if p and lm:
            n = int(lm)
            m = (int(p) - 1) * n
            fy = " order by id desc limit %s,%s" % (m, n)
        print('组合后的sql=', sq1+sq2+fy)
        return sq1+sq2+fy
    except Exception as ek:
        print("sql查询组合命令错误:")
        print(ek)
        print(traceback.format_exc())
        return ''


'''sql增组合'''


def sqlz(data, name):
    try:
        # 基础
        sq1 = "insert into %s" % name
        # 批量生成键
        key = tuple(data.keys())
        # 批量生成值
        v = str(tuple(data.values()))
        sql = sq1+"%s values %s" % (str(key).replace("'", ""), v)
        if len(key) == 1:  # 解决在只有一个元素情况下，元组里最后多一个逗号的问题
            sql = sq1+"%s values %s" % ((str(key).rstrip(',)')+')').replace("'", ""), v.rstrip(',)')+')')
        print(sql)
        return sql
    except Exception as ek:
        print("sql插入组合命令错误:")
        print(ek)
        return 0


'''sql增，插入语句组合3双引号'''


def sql3sz(data, name):
    try:
        # 基础
        sq1 = """insert into %s""" % name
        # 批量生成键
        key = tuple(data.keys())
        # 批量生成值
        v = str(tuple(data.values()))
        sql = sq1+"""%s values %s""" % (str(key).replace("'", ""), v)
        if len(key) == 1:  # 解决在只有一个元素情况下，元组里最后多一个逗号的问题
            sql = sq1+"""%s values %s""" % ((str(key).rstrip(',)')+')').replace("'", ""), v.rstrip(',)')+')')
        print(sql)
        return sql
    except Exception as ek:
        print("sql插入组合命令错误:")
        print(ek)
        return 0



'''agent_record智能体记录专用sql增，插入语句组合3双引号'''


def list_to_safe_base64(data_list):
    # json_str = json.dumps(data_list, ensure_ascii=False)
    # return base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
    json_str = json.dumps(data_list, ensure_ascii=False)
    encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
    # print('encoded_data=', encoded_data)
    return encoded_data

def safe_base64_to_list(base64_str):
    # decoded = base64.urlsafe_b64decode(base64_str).decode('utf-8')
    # return json.loads(decoded)
    decoded = base64.b64decode(base64_str)
    return json.loads(decoded.decode('utf-8'))




'''sql改组合'''

def sqlg(data, name, jsx):
    try:
        # 基础
        sq1 = '''update %s set ''' % name
        # 要改的键值
        sq2 = ''''''
        for x in data:
            if sq2:
                sq2 = sq2 + ''',%s="%s"''' % (x, data[x])
            else:
                sq2 = '''%s="%s"''' % (x, data[x])
        # 检索条件
        sq3 = ''''''
        for j in jsx:
            if jsx[j]:
                if sq3:
                    if j in ['id']:  # 如果检索条件中有id，则用in
                        sq3 = sq3 + ''' and %s in (%s)''' % (j, jsx[j])
                    else:
                        sq3 = sq3 + ''' and %s="%s"''' % (j, jsx[j])
                else:
                    if j in ['id']:  # 如果检索条件中有id，则用in
                        sq3 = ''' where %s in (%s)''' % (j, jsx[j])
                    else:
                        sq3 = ''' where %s="%s"''' % (j, jsx[j])

        print(sq1+sq2+sq3)
        return sq1+sq2+sq3
    except Exception as ek:
        print("sql修改组合命令错误:")
        print(ek)
        return 0


'''sql删除'''

def sqls(name, jsx):
    try:
        # 基础
        sq1 = '''delete from %s ''' % name
        # 检索条件
        sq3 = ''''''
        for j in jsx:
            if jsx[j]:
                if sq3:
                    if j in ['id']:  # 如果检索条件中有id，则用in
                        sq3 = sq3 + ''' and %s in (%s)''' % (j, jsx[j])
                    else:
                        sq3 = sq3 + ''' and %s="%s"''' % (j, jsx[j])
                else:
                    if j in ['id']:  # 如果检索条件中有id，则用in
                        sq3 = ''' where %s in (%s)''' % (j, jsx[j])
                    else:
                        sq3 = ''' where %s="%s"''' % (j, jsx[j])

        logger.warning(sq1+sq3)
        return sq1+sq3
    except Exception as ek:
        logger.error("sql修改组合命令错误:")
        logger.error(ek)
        return ''





