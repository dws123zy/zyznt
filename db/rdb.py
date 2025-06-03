# _*_coding:utf-8 _*_

import redis
import json
# import traceback


# redis的ip地址

redisip = "139.196.36.245"


'''创建json键函数，ai的默认使用db=0'''

def rdata(k, v):
    r = redis.Redis(host=redisip, port=6379, password="Dws666888", db=0, decode_responses=True)

    jg = r.execute_command('JSON.SET', k, '.', json.dumps(v))
    print(jg, '结果', type(jg))
    reply = json.loads(r.execute_command('JSON.GET', k, '.'))
    print('数据类型为：', type(reply))
    print('所有数据=', reply)
    r.close()



'''图片验证码，过期时间为5分钟，也就是300秒'''

verify = {"1747017043033kez": 15}


print(verify)

rdata('verify', verify)


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


