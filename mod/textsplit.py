# _*_coding:utf-8 _*_

import traceback
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter



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
        # 判断text是否为列表，如果是转为字符
        if type(text) in [list]:
            text = ''.join(text)

        # 获取分隔符列表
        slist = separator.split('|')

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
        return chunks

    except Exception as e:
        logger.error(f'通用文本分段失败，文本={e}')
        logger.error(traceback.format_exc())
        return ''


'''使用一个分隔符简单分段'''


def separator(text, separator='\n\n'):
    try:
        """
        不同格式的文件要做不同的处理,txt不用处理
        """

        return text.split(separator)

    except Exception as e:
        logger.error(f'通用文本分段失败，文本={e}')
        logger.error(traceback.format_exc())
        return ''


'''
问答分段，仅支持表格，第一列问，第二列答
问答格式：[{q: '' a: ''}]

'''












