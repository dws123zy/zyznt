# _*_coding:utf-8 _*_

import redis
import json
import traceback
import time
import logging
from mod.tool import openfile  # 文件打开



'''redis内存数据库模块'''


'''日志'''

logger = logging.getLogger(__name__)



'''项目配置文件'''

conf_data = {}
try:
    if '{' in str(openfile('../file/conf.txt')):
        conf_data = eval(openfile('../file/conf.txt'))
except:
    conf_data = {}

'''redis配置全局变量'''

r_host = '127.0.0.1'
if conf_data.get('r_host'):
    r_host = conf_data.get('r_host', '127.0.0.1')

r_port = 6379
if conf_data.get('r_port'):
    r_port = conf_data.get('r_port', 6379)

r_password = 'zyznt'
if conf_data.get('r_password'):
    r_password = conf_data.get('r_password', 'zyznt')


# 连接
# r = redis.Redis(host="192.168.31.125", port=6379, password="Dws666888", db=11, decode_responses=True)

# , retry_on_timeout=True,
#                                   max_idle_time=60
# redis连接池
redis_pool = redis.ConnectionPool(host=r_host, port=r_port, password=r_password, db=0, max_connections=160,
                                  decode_responses=True, socket_connect_timeout=15, retry_on_timeout=True)
# print('刚启动时的现在的连接状态=', redis_pool.max_connections)

'''写入redis.json.set'''

def rjset(cmd):
    try:
        jg = ''
        if cmd and len(cmd) >= 3:
            r = redis.Redis(connection_pool=redis_pool)
            # r = redis.Redis(host="192.168.31.125", port=6379, password="Dws666888", db=11, decode_responses=True)
            try:
                jg = r.execute_command('JSON.SET', cmd[0], cmd[1], json.dumps(cmd[2]))
            except Exception as ekr:
                logger.error(f"rjset错误:{ekr}")
                logger.error('rjset执行命令错误' + str(traceback.format_exc()))
            r.close()
            return jg
        elif cmd and len(cmd) == 2:
            r = redis.Redis(connection_pool=redis_pool)
            # r = redis.Redis(host="192.168.31.125", port=6379, password="Dws666888", db=11, decode_responses=True)
            try:
                jg = r.execute_command('JSON.SET', cmd[0], '.', json.dumps(cmd[1]))
            except Exception as ekr:
                logger.error(f"rjset错误:{ekr}")
                logger.error('rjset执行命令错误' + str(traceback.format_exc()))
            r.close()
            return jg
        return ''
    except Exception as ekr:
        logger.error("rjset错误:")
        logger.error(ekr)
        logger.error(traceback.format_exc())
        logger.error('rjset错误' + str(traceback.format_exc()))
        return ''


'''获取redis.json.get'''

def rjget(cmd):
    try:
        if cmd:
            try:
                jg = ''
                r = redis.Redis(connection_pool=redis_pool)
                # r = redis.Redis(host="192.168.31.125", port=6379, password="Dws666888", db=11, decode_responses=True)
                try:
                    if len(cmd) == 1:
                        jg = json.loads(r.execute_command('JSON.GET', cmd[0]))
                    else:
                        jg = json.loads(r.execute_command('JSON.GET', cmd[0], cmd[1]))
                except Exception as ekr:
                    logger.error("rjget执行命令错误:")
                    logger.error(ekr)
                    # logger.error('rjget执行命令错误' + str(traceback.format_exc()))
                r.close()
                return jg

            except Exception as ekr:
                logger.error("rjget错误:")
                logger.error(ekr)
                logger.error(traceback.format_exc())
                logger.error('rjget错误' + str(traceback.format_exc()))
                return ''
        else:
            return ''
    except Exception as ekr:
        logger.error("rjget错误:")
        logger.error(ekr)
        logger.error(traceback.format_exc())
        return ''


'''redis.json通用命令'''

def rjcmd(cmd):
    try:
        if cmd:
            try:
                jg = ''
                r = redis.Redis(connection_pool=redis_pool)
                try:
                    if len(cmd) == 2:
                        jg = r.execute_command(cmd[0], cmd[1])
                    elif len(cmd) == 3:
                        jg = r.execute_command(cmd[0], cmd[1], cmd[2])
                    else:
                        jg = r.execute_command(cmd[0], cmd[1], cmd[2], cmd[3])
                except Exception as ekr:
                    logger.error("rjcmd错误:")
                    logger.error('rjcmd执行命令错误' + str(traceback.format_exc()))
                r.close()
                return jg
            except Exception as ekr:
                logger.error(f"rjcmd错误:{ekr}")
                logger.error(traceback.format_exc())
                logger.error('rjcmd错误' + str(traceback.format_exc()))
                return ''
        else:
            return ''
    except Exception as ekr:
        logger.error(f"rjcmd错误:{ekr}")
        logger.error(traceback.format_exc())
        return ''


'''redis字符串键值对命令'''


def rstr(cmd):
    if cmd:
        try:
            jg = ''
            if cmd[0] == 'set' and len(cmd) > 2:
                r = redis.Redis(connection_pool=redis_pool)
                try:
                    jg = r.set(cmd[1], cmd[2])
                except Exception as ekr:
                    logger.error(f"rstr错误:{ekr}")
                    logger.error('rstr执行命令错误' + str(traceback.format_exc()))
                r.close()
                return jg
            elif cmd[0] == 'get' and len(cmd) > 1:
                r = redis.Redis(connection_pool=redis_pool)
                try:
                    jg = r.get(cmd[1])
                except Exception as ekr:
                    logger.error(f"rstr错误:{ekr}")
                    logger.error('rstr执行命令错误' + str(traceback.format_exc()))
                r.close()
                return jg
            elif cmd[0] == 'exists' and len(cmd) > 1:
                r = redis.Redis(connection_pool=redis_pool)
                try:
                    jg = r.exists(cmd[1])
                except Exception as ekr:
                    logger.error(f"rstr错误:{ekr}")
                    logger.error('rstr执行命令错误' + str(traceback.format_exc()))
                r.close()
                return jg
            else:
                return ''
        except Exception as ekr:
            logger.error(f"rstr错误:{ekr}")
            logger.error(traceback.format_exc())
            logger.error('rstr错误' + str(traceback.format_exc()))
            return ''
    else:
        return ''


'''set 并设置过期时间'''

def r_set_exp(cmd):
    try:
        jg = ''
        r = redis.Redis(connection_pool=redis_pool)
        try:
            # 设置键、值，并设置过期时间为180秒
            jg = r.set(cmd[0], cmd[1], ex=180)
        except Exception as ekr:
            logger.error(f"r_set_exp错误:{ekr}")
            logger.error('r_set_exp执行命令错误' + str(traceback.format_exc()))
        r.close()
        return jg
    except Exception as ekr:
        logger.error(f"r_set_exp错误:{ekr}")
        logger.error(traceback.format_exc())
        return ''
