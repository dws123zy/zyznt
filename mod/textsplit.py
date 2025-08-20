# _*_coding:utf-8 _*_
import json
import traceback
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mod.llm import openai_llm, openai_llm_json
from data.data import get_zydict



'''日志'''

logger = logging.getLogger(__name__)


'''通用文本分段模块'''

def general(text, separator='\n\n\n|\n\n|\n|。', maxsize=500, o_size=50):
    try:
        """
        text 要分段的文本
        separator 分段字符，多个以|分隔
        maxsize 文本块最大大小
        o_size 可重叠大小
        """
        logger.warning(f'通用文本分段开始separator={separator} maxsize={maxsize} o_size={o_size}')
        # 判断text是否为列表，如果是转为字符，如果是字典，转为字符，如果是集合，转为字符，如果是元组，转为字符
        if type(text) in [list]:
            # text = ''.join(text)
            text = ''.join(str(item) for item in text)
        elif type(text) in [dict, set, tuple]:
            text = str(text)

        # 获取分隔符列表
        slist = separator.split('|')
        logger.warning(f'通用文本分段分隔符={slist}')

        # 初始化递归分割器
        text_splitter = RecursiveCharacterTextSplitter(
            separators=slist,  # 分隔符
            chunk_size=maxsize,  # 最大字符数限制
            chunk_overlap=o_size,  # 段落间重叠字符
            length_function=len,
            is_separator_regex=False,
            keep_separator=True  # 保留分隔符标记
        )

        chunks = text_splitter.split_text(text)
        return {"code": 200, "data": chunks}

    except Exception as e:
        logger.error(f'通用文本分段失败，文本={e}')
        logger.error(traceback.format_exc())
        return {"code": 501, "data": f'通用文本分段失败，原因={e}'}


'''使用一个分隔符简单分段'''


def separator_split(text, separator='\n\n', maxsize=5000):
    try:
        """
        不同格式的文件要做不同的处理,txt不用处理
        """
        textlist = str(text).split(separator)
        for t in textlist:
            if len(t) > int(maxsize):
                logger.warning(f'通用文本分段失败，超过了最大长度，文本={t}')
                return {"code": 501, "data": f'通用文本分段失败，原因=段落超过了最大长度'}

        return {"code": 200, "data": textlist}

    except Exception as e:
        logger.error(f'使用一个分隔符分段失败，原因={e}')
        logger.error(traceback.format_exc())
        return {"code": 501, "data": f'使用一个分隔符分段失败，原因={e}'}


'''
问答分段，仅支持表格，第一列问，第二列答
问答格式：[{q: '' a: ''}]

'''

def qa_split(text, maxsize=5000):
    try:
        """
        问答分段，只处理表格数据，第一列是问，第二列答
        """
        text_list = []
        # 判断text格式是否为要求的，如果是表格，则处理
        if type(text) in [dict]:
            # 遍历所有表格
            for sheet in text:
                logger.warning(f'问答分段，{ sheet}表格数据处理开始')
                if text[sheet]:  # 判断表中是否有数据
                    for x in text[sheet]:
                        if x and type(x) in [tuple, list]:
                            if len(x[0]) < int(maxsize) and len(x[1]) < int(maxsize):
                                text_list.append({'q': x[0], 'a': x[1]})
                            else:
                                logger.warning(f'问答分段，超过最大长度，文本={x}')

                else:
                    logger.warning(f'问答分段，{ sheet}表格没有数据')

        return {"code": 200, "data": text_list}

    except Exception as e:
        logger.error(f'文本问答分段失败={e}')
        logger.error(traceback.format_exc())
        return {"code": 501, "data": f'文本问答分段失败，原因={e}'}


'''LLM智能分段'''

'''LLM文本分段格式化示例llm用'''

sql_example1 = json.dumps(
    ['呼叫中心系统可以录音，并支持导出录音。', '\n 呼叫中心系统有通话记录功能，可以查询呼叫的开始和结束时间，还有通话时长。'],
    ensure_ascii=False
)

text_json_msg = """请根据用户提供的文件内容，按用户要求给文本分段，然后以JSON格式输出，格式例如：["文本段1", "文本段2", "文本段3"]。
        示例：
        Q：请把此文本按语义分成最大500字左右的段落，用于转为向量，做RAG知识增强。文件内容：呼叫中心系统可以录音，并支持导出录音。\n 呼叫中心系统有通话记录功能，可以查询呼叫的开始和结束时间，还有通话时长。
        A：%s\n
        """ % sql_example1


def llm_text(text, sys_text, llm, msg, separator='', maxsize=5000):
    try:
        """
        不同格式的文件要做不同的处理,txt不用处理
        """
        # 先判断是否有分段符，如果有则按分隔符处理
        if separator:
            textlist = str(text).split(separator)
        else:
            textlist = general(text, separator= '\n\n\n\n\n|\n\n\n',maxsize=int(maxsize), o_size=50)
        for t in textlist:
            if len(t) > int(maxsize):
                logger.warning(f'通用文本分段失败，超过了最大长度，文本={t}')
                return {"code": 501, "data": f'通用文本分段失败，原因=段落超过了最大长度'}
        # 使用llm大模型处理分段
        # 获取llm配置数据
        llmdata = get_zydict('llm',llm)
        if not llmdata:
            logger.error(f'LLM模型没有数据，请检查')
            return {"code": 501, "data": f'LLM模型没有数据，请检查'}
        # 遍历源初级分段，使用llm再次处理
        llm_text_list = []
        for l in textlist:
            if l:
                logger.warning(f'LLM文本分段，要处理的内容：{l}')
                # 组合msg
                msg_list = [
                    {'role': 'system', 'content': str(text_json_msg)+str(sys_text)},
                    {'role': 'user', 'content': f'文件内容：{l}'},
                    {'role': 'user', 'content': msg},
                ]
                logger.warning(f'LLM文本分段，msg_list={msg_list}')
                if llmdata.get('sdk') in ['openai']:
                    llm_chunks_list = openai_llm_json(msg_list, llmdata.get('apikey', ''), llmdata.get('url', ''), llmdata.get('module', ''))
                    if llm_chunks_list:
                        llm_text_list = llm_text_list + llm_chunks_list

        # 返回结果
        return {"code": 200, "data": llm_text_list}

    except Exception as e:
        logger.error(f'llm文本分段失败{e}')
        logger.error(traceback.format_exc())
        return {"code": 501, "data": f'llm文本分段失败，原因={e}'}







