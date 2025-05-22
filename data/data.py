# _*_coding:utf-8 _*_

import logging
import secrets  # 用于生成token
import json
import time
import traceback

from db.my import msqlc, msqlzsg
from mod.tool import openfile, writefile  # 文件打开和写入

'''日志'''

logger = logging.getLogger(__name__)


'''appid公司数据'''

appids = {}


'''user用户数据'''

users = {}


'''zydict数据字典'''

zydict = {}

'''ragrag知识库数据'''

ragdata = {}

'''agent智能体数据'''

agentdata = {}


'''cd菜单数据'''

# zyzntcd = []

# 打开 JSON 文件并读取内容
with open('conf/cd.json', 'r', encoding='utf-8') as file:
    zyzntcd = json.load(file)  # 自动转换为字典或列表



'''从数据库加载appid公司数据'''

def loadappid():
    try:
        sqlcmd = "select * from company"
        datac = msqlc(sqlcmd)  # 查询所有公司数据

        appidlist = []
        if datac:
            for a in datac:
                appid = a['appid']
                appidlist.append(appid)
                appids[appid] = a
            logger.warning(f'加载appid成功={appids}')
            # 找到已不存在的appid，记录并删除
            delappid = []
            if appidlist and datac and len(appids) != len(appidlist):
                for p in appids:
                    if p not in appidlist:
                        delappid = delappid + [p]
                # 删除appid
                if delappid:
                    for da in delappid:
                        del appids[da]

            return 200
        else:
            logger.warning('错误，未查到公司帐号数据，reload失败')
            return 0
    except Exception as sqlload:
        logger.error("loadappid错误:")
        logger.error(sqlload)
        logger.error(traceback.format_exc())
        return 0


loadappid()  # 加载appid公司数据


'''从数据库加载用户数据user'''

def loadusers():
    try:
        # 执行SQL语句，查询所有用户数据
        sqla = "select * from user"
        datac = msqlc(sqla)
        if datac:
            for u in datac:
                if u.get('user'):
                    users[u.get('user', '')] = u
        logger.warning(f'加载user成功={users}')
    except Exception as e:
        logger.error({"loadusers错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())


loadusers()  # 加载用户数据user


'''从数据库加载zydict数据'''

def loadzydict():
    try:
        # 执行SQL语句
        sqla = "select * from zydict"
        dataczydict = msqlc(sqla)
        if dataczydict:
            for i in dataczydict:
                edata = eval(i['data'])
                zydict[i['dictid']] = i
                zydict[i['dictid']]['data'] = edata
            logger.warning(f'reloaddict成功={zydict}')
            return 200
        else:
            logger.warning('错误，未查到数据字典数据，reload失败')
            return 0
    except Exception as sqlload:
        logger.error("loaddict错误:")
        logger.error(sqlload)
        logger.error(traceback.format_exc())
        return 0


loadzydict()  # 加载zydict数据


'''从数据库加载rag知识库'''

def loadrag():
    try:
        # 执行SQL语句
        sqla = "select * from rag"
        datacrag = msqlc(sqla)
        if datacrag:
            for i in datacrag:
                ragdata[i['ragid']] = i
                if i['search']:
                    searchdata = eval(i['search'])
                    ragdata[i['ragid']]['search'] = searchdata
                else:
                    ragdata[i['ragid']]['search'] = {}
                if i['split']:
                    splitdata = eval(i['split'])
                    ragdata[i['ragid']]['split'] = splitdata
                else:
                    ragdata[i['ragid']]['split'] = {}
            logger.warning(f'reload_rag成功={ragdata}')
            return 200
        else:
            logger.warning('错误，未查到rag数据，reload_rag失败')
            return 0
    except Exception as sqlload:
        logger.error("reload_rag错误:")
        logger.error(sqlload)
        logger.error(traceback.format_exc())
        return 0

loadrag()  # 加载rag数据


'''从数据库加载agent智能体数据'''

def loadagent():
    try:
        # 执行SQL语句
        sqla = "select * from agent"
        datacagent = msqlc(sqla)
        if datacagent:
            for i in datacagent:
                edata = eval(i['data'])
                agentdata[i['agentid']] = i
                agentdata[i['agentid']]['data'] = edata
            logger.warning(f'reload agent成功={agentdata}')
            return 200
        else:
            logger.warning('错误，未查到agent智能体数据，reload失败')
            return 0
    except Exception as sqlload:
        logger.error("load agent错误:")
        logger.error(sqlload)
        logger.error(traceback.format_exc())
        return 0


loadagent()  # 加载agent数据


'''验证码图片校验'''

def img_verify(imgid, verify):
    try:
        if openfile(f'../file/img/{imgid}.txt') == verify:
            return True
        else:
            return False
    except Exception as e:
        logger.error({"img_verify错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return False



'''登录验证'''

def logonac(data):
    try:
        if data.get('user') in users:
            # 验证密码
            if users[data.get('user')]['password'] == data.get('password'):
                # 拿到用户的appid
                appid = users[data.get('user')]['appid']
                # 判断appid公司是否开启了动态验证，如果t,则判断验证码是否正确,否则不判断验证码
                if appids[appid].get('verify', '') in ['t']:
                    if not img_verify(data.get('imgid'), data.get('verify')):
                        return {'code': '403', 'msg': '验证码错误'}
                # 生成token，设置有效期
                token = secrets.token_hex(16)  # 生成32位安全随机字符串
                expire = int(time.time()) + 3600 * 24 * 3
                # 存入字典和mysql
                users[data.get('user')]['token'] = token
                users[data.get('user')]['expire'] = expire
                sqlcmd = f"update user set token='{token}',expire={expire} where user='{data.get('user')}'"
                msqlzsg(sqlcmd)
                # 返回token
                return {'code': '200', 'msg': '登录成功', 'data': {'token': token, 'cd': zyzntcd, 'appid': appid}}
            else:
                return {'code': '403', 'msg': '密码错误'}
        else:
            return {'code': '406', 'msg': '用户名错误或已暂停'}
    except Exception as e:
        logger.error({"logonac错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'code': '501', 'msg': '数据错误'}


'''验证token'''

def tokenac(token, user):
    try:
        if user in users:
            if users[user]['token'] == token:
                if int(time.time()) < int(users[user]['expire']):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        logger.error({"tokenac错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return False



'''验证apikey'''

def apikeyac(apikey, appid):
    try:
        logger.warning(f'apikey={apikey}, appid={appid}')
        if appid in appids:
            print('appid合法')
            if apikey in zydict:
                print('apikey合法')
                if zydict[apikey]['appid'] in [appid]:
                    data = zydict[apikey]['data']
                    print(data)
                    if data.get('expire', 0) in ['000'] or int(time.time()) < int(data.get('expire', 0)):
                        print('apikey有效')
                        return True
        return False
    except Exception as e:
        logger.error({"apikeyac错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return False



'''根据user、cmd获取检索项'''

def get_filter(cmd, user=''):
    try:
        if cmd and user:  # 根据用户角色、cmd获取对应的检索项
            role = users.get(user).get('role', '')
            jsxid = zydict.get(role, {}).get('data', {}).get('filter', {}).get(cmd, '')
            if jsxid and jsxid in zydict:
                return zydict.get(jsxid, {}).get('data', {})
        elif cmd:  # 只根据cmd获取检索项
            if cmd in zydict:
                return zydict.get(cmd, {}).get('data', {})
        return {}  # 没找到数据，返回空字典
    except Exception as e:
        logger.error({"获取检索项错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {}


'''根据type(数据类型比如tb表头、form表单)、user、cmd获取检索项'''

def get_zydict(datatype, cmd, user=''):
    try:
        if datatype:  #  in ['tb', 'form', 'db']:
            if cmd and user:  # 根据用户角色、cmd获取对应的检索项
                role = users.get(user).get('role', '')
                jsxid = zydict.get(role, {}).get('data', {}).get(datatype, {}).get(cmd, '')
                if jsxid and jsxid in zydict:
                    return zydict.get(jsxid, {}).get('data', {})
            elif datatype in ['tool', 'mcp'] and cmd in zydict:  # 此类型的数据返回所有
                return zydict.get(cmd, {})

            elif cmd:  # 只根据cmd获取检索项
                if cmd in zydict:
                    return zydict.get(cmd, {}).get('data', {})
        return {}  # 没找到数据，返回空字典
    except Exception as e:
        logger.error({"获取检索项错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {}


'''根据ragid获取rag配置数据'''

def get_rag(ragid):
    try:
        if ragid and ragid in ragdata:
            return ragdata.get(ragid, {})
        return {}  # 没找到数据，返回空字典
    except Exception as e:
        logger.error({"获取ragdata错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {}


'''根据agentid获取agent配置数据'''

def get_agent(agentid):
    try:
        if agentid and agentid in agentdata:
            return agentdata.get(agentid, {})
        return {}  # 没找到数据，返回空字典
    except Exception as e:
        logger.error({"获取agentdata错误:": e})
        logger.error(e)
        logger.error(traceback.format_exc())
        return {}











