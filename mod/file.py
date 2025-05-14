# _*_coding:utf-8 _*_

import traceback
import time
import logging
import threading
import importlib
import os
import httpx
from concurrent.futures import ThreadPoolExecutor  # 线程池

# 本地模块
from mod import textsplit
from db.mv import insert_data
from db import my
from data.data import get_zydict


'''文件解析模块'''


'''日志'''

logger = logging.getLogger(__name__)


'''初始化线程池'''

filefpool = ThreadPoolExecutor(max_workers=9)


'''获取文件读取模块配置'''

# filemod = [{'fun_name': 'read_file', 'dir': 'mod.file2text.file2text'},
#            {'fun_name': 'read_pdf', 'dir': 'mod.file2text.file2text'},
#            {'fun_name': 'read_docx', 'dir': 'mod.file2text.file2text'},
#             {'fun_name': 'read_excel', 'dir': 'mod.file2text.file2text'},
#             {'fun_name': 'read_ppt', 'dir': 'mod.file2text.file2text'},
#             {'fun_name': 'read_csv', 'dir': 'mod.file2text.file2text'},
#            ]   # 所有文件模块
filemod = get_zydict('file', 'filemod')

# fileformat = {'docx': 'read_docx', 'pdf': 'read_pdf', 'xlsx': 'read_excel', 'pptx': 'read_ppt', 'csv': 'read_csv',
#               'txt': 'read_file', 'py': 'read_file', }
fileformat = get_zydict('file', 'fileformat')


'''动态加载文件读取模块'''

modlist = {}


for m in filemod:
    try:
        # 动态导入 mod/a.py
        module = importlib.import_module(m.get('dir'))
        # 获取函数
        func = getattr(module, m.get('fun_name'))
        modlist[m.get('fun_name')] = func
        print('模块导入成功=', func)
    except ImportError as e:
        print(f"导入失败: {e}")

logger.warning(f'模块导入成功={modlist}')


'''embd模型'''

def zyembd(text, embddata):
    try:
        logger.warning('开始调用embd模型')
        if embddata.get('embdname') in ['zyembd'] and embddata.get('mod_name') in ['bge-large-zh-v1.5']:
            logger.warning(f'开始调用本地embd模型={embddata.get("mod_name")}')
            url = embddata.get('url')
            payload = {'apikey': embddata.get('apikey'), 'text': [text]}
            # 设置请求头（根据接口需求调整)
            headers = {"Content-Type": "application/json"}
            # 发送同步 POST 请求
            # response = httpx.post(url=url, json=payload, headers=headers, timeout=60.0)
            with httpx.Client() as client:  # 使用上下文管理器确保资源正确释放
                response = client.post(url, json=payload, headers=headers, timeout=60.0)
                # 检查响应状态码
                if response.status_code == 200:
                    print("请求成功!")
                    rdata = response.json()
                    # print("响应内容:", rdata)  # 将响应内容解析为JSON
                    return rdata.get('data', '')[0]
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    logger.warning(f"错误信息:{response.json()}")
                    return ''
        elif embddata.get('embdname') in ['ollama']:
            logger.warning(f'开始调用ollama中的embd模型={embddata.get("mod_name")}')
            return ''
        else:
            logger.warning(f'不支持的embd模型={embddata.get("embdname")}')
            return ''
    except Exception as e:
        logger.error(f"调用embd模型错误: {e}")
        logger.error(traceback.format_exc())
        return ''



'''校验文件状态和变更状态，启动解析时，文件状态要为未解析，然后改为解析中，解析完成后改为已解析'''

def  file_status(fileid, cmd):
    try:
        if cmd in ['work']:  # 要解析文件，先校验状态为非work,然后把状态改为work
            sql = my.sqlc3({'fileid': fileid}, 'file', 1, 10, '')
            jg = my.msqlc(sql)
            if jg and jg[0].get('analysis') not in ['work']:
                logger.warning(f'此文件可以解析，现在改状态为解析中work')
                sql = my.sqlg({'analysis': 'work'}, 'file', {'fileid': fileid})
                jg2 = my.msqlzsg(sql)
                return 1
            else:
                logger.warning(f'文件状态为解析中work，禁止再次解析，文件id={fileid}')
                return 0
        elif cmd in ['ok']:  # 此时文件解析已完成，把状态改为ok
            logger.warning(f'文件解析完成，现在改状态为解析成功ok')
            sql = my.sqlg({'analysis': 'ok'}, 'file', {'fileid': fileid})
            jg2 = my.msqlzsg(sql)
            return 1
        elif cmd in ['error']:  # 文件解析失败，把状态改为error
            logger.warning(f'文件解析失败，现在改状态为解析失败error')
            sql = my.sqlg({'analysis': 'error'}, 'file', {'fileid': fileid})
            jg3 = my.msqlzsg(sql)
            return 1
        else:
            logger.warning(f'不支持的cmd={cmd}')
            return 0
    except Exception as e:
        logger.error(f"文件状态修改错误: {e}")
        return ''



'''存入向量数据库和改mysql中的解析状态'''

def vdb_mdb(ragdata, vdata, fileid):
    try:
        # 存入向量数据库
        if vdata:
            logger.warning(f'转向量并组合数据成功，现在存入向量数据库')
            ragid = ragdata.get('ragid')
            if ragid:
                vjg = insert_data(vdata, ragid)
                if vjg:
                    logger.warning(f'向量数据库数据存入成功')
                    # 存入mysql数据库
                    # sql = my.sqlg({'analysis': 'ok'}, 'file', {'fileid': fileid})
                    # jg = my.msqlzsg(sql)
                    # if jg:
                    #     logger.warning(f'数据存入mysql数据库成功')
                    #     # 返回结果
                    #     return 1
                    # else:
                    #     logger.warning(f'数据存入mysql数据库失败')
                    #     return ''
                    return 1
                else:
                    logger.warning(f'数据存入向量数据库失败')
                    return ''
        return ''
    except Exception as e:
        logger.error(f"数据存入向量数据库错误: {e}")
        logger.error(traceback.format_exc())
        return ''



'''解析流程控制总函数'''

def filejx(filedata, ragdata):
    try:
        logger.warning(f'开始解析文件，文件数据={filedata}')
        # 获取文件路径
        file_path = f"../file/{ragdata.get('appid', '')}/{ragdata.get('ragid', '')}/{filedata.get('name', '')}"
        logger.warning(f'文件路径={file_path}')
        # 获取文件扩展名
        file_extension = os.path.splitext(file_path)[1].replace('.', '')
        logger.warning(f'文件格式={file_extension}')
        if file_extension in fileformat:
            file_fun = fileformat.get(file_extension, 'read_file')
            logger.warning(f'file_fun={file_fun}')
        else:
            logger.warning(f'不支持的文件格式{file_extension}，文件数据={filedata}')
            return 0
        # 获取文件大小，超过100M的另外处理
        file_size = os.path.getsize(file_path)/(1024*1024)   # 转为M

        # 读取文件内容
        datac = []
        if file_size > 100:
            logger.warning(f'文件大小超过100M暂不处理，文件数据={file_size}')
            return ''
        else:
            if '/' in file_fun:
                file_fun2 = file_fun.split('/')
                file_fun = file_fun2[0]
                encoding = file_fun2[1]
                datac = modlist[file_fun](file_path, encoding)
            else:
                datac = modlist[file_fun](file_path)

        # 处理内容
        if datac:
            logger.warning(f'文件内容读取成功，现在做图片提取、文本分段、并向量化处理{datac}')
            # 图片提取

            # 文本分段
            textlist = []
            split_data = filedata.get('split', {})
            split_fun = split_data.get('split_fun', 'general')
            if split_fun in ['general']:  # 通用分段
                logger.warning(f'通用文本分段开始')
                separator = split_data.get('data', {}).get('separator', '\n\n\n|\n\n|\n|。')
                maxsize = int(split_data.get('data', {}).get('maxsize', 500))
                o_size = int(split_data.get('data', {}).get('o_size', 50))
                textlist = textsplit.general(datac, separator=separator, maxsize=maxsize, o_size=o_size)
                # 处理llm泛华问题配置
                if split_data.get('llm_q'):
                    pass
            elif split_fun in ['separator']:
                logger.warning(f'指定分隔符文本分段开始')
                textlist = textsplit.separator(datac, split_data.get('data', {}).get('separator', '\n\n\n|\n\n|\n|。'))
                # 处理llm泛华问题配置
                if split_data.get('llm_q'):
                    pass
            elif split_fun in ['llm', 'LLM']:
                logger.warning(f'LLM文本分段开始')
                # 处理llm泛华问题配置
                if split_data.get('llm_q'):
                    pass
            elif split_fun in ['qa']:
                logger.warning(f'QA问答文本分段开始')
                # 处理llm泛华问题配置
                if split_data.get('llm_q'):
                    pass

            # 转向量并存入向量数据库
            vdata = []  # 存储向量数据，单次不能超过1000M
            fileid = filedata.get('fileid', '')
            if textlist:
                logger.warning(f'分段已成功，现在转向量并组合数据')

                # 获取检索向量方式
                search = ragdata.get('search', {}).get('search_fun', 'vector')  # 拿到检索向量方式
                # 获取embedding数据
                embdid = ragdata.get('embedding').split('/')[1] if ragdata.get('embedding') else 'bge-large-zh-v1.5'
                embddata = get_zydict('embd', embdid)
                # 遍历文本列表，向量化文本，组合数据，入库向量数据库
                for t in textlist:
                    '''
                    id vector sparse text fileid  state   metadata  q_text  s_text  keyword    

                    id  向量 稀疏      文本  文件名或id  块状态   元数据        问   稀疏文本    关键词、标签    
                    '''
                    vd = {'fileid': fileid, 'state': 't', 'metadata': {'filename': filedata.get('name', '')}}

                    if search in ['vector']:  # 向量化检索
                        logger.warning(f'向量化检索数据处理开始')
                        # 判断是否为问答或llm泛化问答
                        if split_fun in ['qa'] or split_data.get('llm_q'):  # 问答时t的数据格式为{q: ,a: }
                            vd['q_text'] = t.get('q', '')
                            vd['text'] = t.get('a', '')
                            vd['vector'] = zyembd(t.get('q', ''), embddata)
                        else:  # 非问答时，t就是文本内容
                            vd['text'] = t
                            vd['vector'] = zyembd(t, embddata)
                    # elif search in ['sparse']:  # 稀疏向量化检索 当只使用全文检索时，且表中没有向量字段时走这个逻辑
                    #     logger.warning(f'稀疏向量化检索数据处理开始')
                    #     # 判断是否为问答或llm泛化问答
                    #     if split_fun in ['qa'] or split_data.get('llm_q'):  # 问答时t的数据格式为{q: ,a: }
                    #         vd['q_text'] = t.get('q', '')
                    #         vd['text'] = t.get('a', '')
                    #         vd['s_text'] = t.get('q', '')
                    #     else:  # 非问答时，t就是文本内容
                    #         vd['text'] = t
                    #         vd['s_text'] = t
                    elif search in ['sparse', 'vs']:  # 全文检索  向量+稀疏向量检索
                        logger.warning(f'向量+稀疏向量检索数据处理开始')
                        # 判断是否为问答或llm泛化问答
                        if split_fun in ['qa'] or split_data.get('llm_q'):  # 问答时t的数据格式为{q: ,a: }
                            vd['q_text'] = t.get('q', '')
                            vd['text'] = t.get('a', '')
                            vd['s_text'] = t.get('q', '')
                            vd['vector'] = zyembd(t.get('q', ''), embddata)
                        else:  # 非问答时，t就是文本内容
                            vd['text'] = t
                            vd['s_text'] = t
                            vd['vector'] = zyembd(t, embddata)
                    else:
                        logger.error(f'检索方式{search}不存在，请检查')
                        # 跳过此次循环
                        continue
                    # 把本条数据加到vdata中
                    vdata.append(vd)
                    # 检查vdata是否超过了1000条，如果是，就入库一次，以免占用内存
                    if len(vdata) > 1000:
                        logger.warning(f'vdata数据超过1000条，入库中')
                        jg = vdb_mdb(ragdata,vdata, fileid)  # 把vdata中现有的数据先入库
                        if jg:
                            vdata = []  # 清空vdata

            # 检查vdata中是否还有数据
            if vdata:
                logger.warning(f'vdata数据不足1000条，入库中')
                jg2 = vdb_mdb(ragdata, vdata, fileid)
                if jg2:
                    logger.warning(f'向量入库成功={filedata}')
                else:
                    logger.error(f'向量入库失败={filedata}')
        # 文件解析全部成功
        logger.warning(f'文件解析全部成功，文件数据={filedata}')
        # 解析成功，现在修改文件状态为ok
        jg = file_status(fileid, 'ok')
        # 返回结果
        return 1

    except Exception as e:
        logger.error(f'校验文件状态和变更状态失败，文件数据={filedata}')
        logger.error(e)
        logger.error(traceback.format_exc())
        # 解析失败，修改文件状态为error
        jg = file_status(fileid, 'error')
        return ''


'''解析对外交互函数，接受任务发起、拉起多线程执行解析总函数'''

def fileanalysis(filedata, ragdata):
    try:
        logger.warning(f'开始处理解析文件请求')
        # 调用线程池发起解析请求
        filelist = []
        for f in filedata:
            try:
                jg = file_status(f.get('fileid', ''), 'work')
                if jg:
                    filework = filefpool.submit(filejx, f, ragdata)
                    logger.warning(f'发起解析文件请求成功，文件数据={f}')
                    filelist.append({'fileid': f.get('fileid', ''), 'status': 'work'})
                else:
                    logger.error(f'文件状态为work，文件数据={f}')
                    filelist.append({'fileid': f.get('fileid', ''), 'status': 'error'})
            except Exception as e:
                logger.error(f'发起解析文件请求失败，文件数据={f}')
                logger.error(e)
                logger.error(traceback.format_exc())
                filelist.append({'fileid': f.get('fileid', ''), 'status': 'error'})
        return filelist
    except Exception as e:
        logger.error(f'解析文件失败，文件数据={filedata}')
        logger.error(e)
        logger.error(traceback.format_exc())
        return 0



'''单条文本块转向量入库'''

def partjx(filedata, ragdata):
    try:
        logger.warning(f'开始解析单条文本段，文件数据={filedata}')
        # 处理内容
        text = filedata.get('text', '')
        split_fun = filedata.get('q_text', '')  # 有值时为问答，否则为非问答
        fileid = filedata.get('fileid', '')
        # 获取检索向量方式
        search = ragdata.get('search', {}).get('search_fun', 'vector')  # 拿到检索向量方式
        # 获取embedding数据
        embdid = ragdata.get('embedding').split('/')[1] if ragdata.get('embedding') else 'bge-large-zh-v1.5'
        embddata = get_zydict('embd', embdid)
        # 遍历文本列表，向量化文本，组合数据，入库向量数据库
        if text:
            '''
            id vector sparse text fileid  state   metadata  q_text  s_text  keyword    

            id  向量 稀疏      文本  文件名或id  块状态   元数据        问   稀疏文本    关键词、标签    
            '''
            vd = {'fileid': fileid, 'state': 't', 'metadata': {'filename': filedata.get('name', '')}}

            if search in ['vector']:  # 向量化检索
                logger.warning(f'向量化检索数据处理开始')
                # 判断是否为问答或llm泛化问答
                if split_fun:  # 问答时t的数据格式为{q: ,a: }
                    vd['q_text'] = split_fun
                    vd['text'] = text
                    vd['vector'] = zyembd(split_fun, embddata)
                else:  # 非问答时，t就是文本内容
                    vd['text'] = text
                    vd['vector'] = zyembd(text, embddata)
            # elif search in ['sparse']:  # 稀疏向量化检索 当只使用全文检索时，且表中没有向量字段时走这个逻辑
            #     logger.warning(f'稀疏向量化检索数据处理开始')
            #     # 判断是否为问答或llm泛化问答
            #     if split_fun in ['qa'] or split_data.get('llm_q'):  # 问答时t的数据格式为{q: ,a: }
            #         vd['q_text'] = t.get('q', '')
            #         vd['text'] = t.get('a', '')
            #         vd['s_text'] = t.get('q', '')
            #     else:  # 非问答时，t就是文本内容
            #         vd['text'] = t
            #         vd['s_text'] = t
            elif search in ['sparse', 'vs']:  # 全文检索  向量+稀疏向量检索
                logger.warning(f'向量+稀疏向量检索数据处理开始')
                # 判断是否为问答或llm泛化问答
                if split_fun:  # 问答时t的数据格式为{q: ,a: }
                    vd['q_text'] = split_fun
                    vd['text'] = text
                    vd['s_text'] = split_fun
                    vd['vector'] = zyembd(split_fun, embddata)
                else:  # 非问答时，t就是文本内容
                    vd['text'] = text
                    vd['s_text'] = text
                    vd['vector'] = zyembd(text, embddata)
            else:
                logger.error(f'检索方式{search}不存在，请检查')
            # 把本条数据加到vdata中
            logger.warning(f'vdata数据入库中')
            ragid = ragdata.get('ragid')
            if ragid:
                vjg = insert_data([vd], ragid)
        # 解析成功
        logger.warning(f'文本段解析成功，文件数据={filedata}')
        # 返回结果
        return 1

    except Exception as e:
        logger.error(f'单条文本块转向量入库错误，文件数据={filedata}')
        logger.error(e)
        logger.error(traceback.format_exc())
        return ''







'''工具集'''


'''文件打开函数'''

def openfile(name):
    try:
        with open(name, 'r', encoding='utf-8') as data:
            return data.read()
    except Exception as ek:
        logger.error("打开文件错误:")
        logger.error(ek)
        logger.error(traceback.format_exc())
        return 0


'''文件写入函数'''

def writefile(name, data):
    try:
        with open(name, 'w+', encoding='utf-8') as dataw:
            dataw.write(str(data))
        return 1
    except Exception as ek:
        logger.error("写入文件错误:")
        logger.error(ek)
        logger.error(traceback.format_exc())
        return 0














