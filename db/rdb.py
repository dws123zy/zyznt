# _*_coding:utf-8 _*_

import redis
import json
from mod.tool import openfile  # 文件打开


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


'''创建json键函数，ai的默认使用db=0'''

def rdata(k, v):
    try:
        print(f'host={r_host}, port={r_port}, password={r_password}')
        r = redis.Redis(host=r_host, port=r_port, password=r_password, db=0, decode_responses=True, socket_connect_timeout=20)
        # 判断键是否存在
        if r.exists(k):
            print(f'{k}键已存在,无需新建')
        else:
            jg = r.execute_command('JSON.SET', k, '.', json.dumps(v))
            print(jg, '结果', type(jg))
            reply = json.loads(r.execute_command('JSON.GET', k, '.'))
            print('数据类型为：', type(reply))
            print('所有数据=', reply)
        r.close()
    except Exception as ekr:
        print("rdata执行命令错误:")
        print(ekr)



'''图片验证码，过期时间为5分钟，也就是300秒'''
#
# verify = {"1747017043033kez": 15}
#
#
# print(verify)
#
# rdata('verify', verify)

def redis_init():
    try:
        '''reloadtime'''

        reloaddata = {
            "appid": 1686897642.9402745,
            "agent": 1686875844.9163587,
            "rag": 1686842909.5221703,
            "zydict": 1686583460.4805636,
            "user": 1683193283.4748127,
        }

        rdata('reloaddata', reloaddata)


        '''智能体对话记录'''

        agent_record = {"session": {"session": "session", "appid": "zy001", "user": "dws@zy", "agentid": "agent004",
                                    "type": "agent", "start_time": "", "end_time": "", "tokens": "", "data": []}}

        rdata('agent_record', agent_record)
    except Exception as e:
        print("redis_init执行命令错误:")
        print(e)


