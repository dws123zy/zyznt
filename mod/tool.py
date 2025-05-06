# _*_coding:utf-8 _*_
import logging


'''日志'''

logger = logging.getLogger(__name__)


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






