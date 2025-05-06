# _*_coding:utf-8 _*_

import traceback
import logging


'''文件解析模块(格式txt py .c, .cpp, .h .sh 等可以用txt打开的所有文件)'''


'''日志'''

logger = logging.getLogger(__name__)


'''文件打开函数'''

def read_file(filedir, encoding='utf-8', line=''):  # encoding 打开文件时所用的编码格式，默认utf-8
    try:
        # 获取文件line行标，有值则是按行读取，无则一次读取，一般100M以内直接读取，以上按行读取
        if line:
            logger.warning(f'按行读取文件，行数={line}')  # '开放中'
            return ''
        else:
            logger.warning(f'读取文件，文件路径={filedir}')
            with open(filedir, 'r', encoding=encoding) as data:
                return data.read()
    except Exception as ek:
        logger.error("打开文件错误:")
        logger.error(ek)
        logger.error(traceback.format_exc())
        return ''


'''pdf文件解析打开函数'''


import pdfplumber

# 常规打开方式（适合小文件，大于100M的使用分页方式读取）

def read_pdf(filedir, page2=''):
    try:
        # page2，有值则是按页读取，无则一次读取，一般100M以内直接读取，以上按页读取
        if page2:
            logger.warning(f'按页读取文件，行数={page2}')  # '开放中'
            return ''
        else:
            logger.warning(f'读取文件，文件路径={filedir}')
            pdflist = []
            with pdfplumber.open(filedir) as pdf:
                for page in pdf.pages:
                    pdflist.append(page.extract_text())

            # 返回数据，每个页面为一个元素
            return pdflist
    except Exception as ek:
        logger.error("打开文件错误:")
        logger.error(ek)
        logger.error(traceback.format_exc())
        return ''




'''docx文件打开python-docx'''


from docx import Document


def read_docx(file_path, page2=''):
    try:
        # page2，有值则是按页读取，无则一次读取，一般100M以内直接读取，以上按页读取
        if page2:
            logger.warning(f'按页读取文件，行数={page2}')  # '开放中'
            return ''
        else:
            logger.warning(f'读取文件，文件路径={file_path}')
            with open(file_path, 'rb') as file:
                doc = Document(file)
                full_text = []
                for paragraph in doc.paragraphs:
                    full_text.append(paragraph.text)

                # 返回文本列表
                return full_text
    except Exception as e:
        logger.error("打开docx文件错误:")
        logger.error(e)
        logger.error(traceback.format_exc())
        return ''



'''读取xlsx/xlsm/xltx/xltm文件'''


from openpyxl import load_workbook


def read_excel(file_path):
    try:
        # 加载工作簿
        workbook = load_workbook(filename=file_path)
        try:
            # 获取所有工作表
            sheets = workbook.sheetnames
            logger.warning(f"文件包含的工作表: {sheets}")

            data = {}
            # 读取每个工作表的内容
            for sheet_name in sheets:
                sheet = workbook[sheet_name]
                logger.warning(f"\n工作表 '{sheet_name}' 内容:")

                # 把sheet加到数据中
                if sheet_name not in data:
                    data[sheet_name] = []
                # 读取所有数据
                for row in sheet.iter_rows(values_only=True):
                    data[sheet_name].append(row)

            # 返回数据
            return data
        except Exception as e2:
            logger.error(f"读取工作表 '{file_path}' 时出错: {e2}")
            logger.error(traceback.format_exc())
            return ''
        finally:
            workbook.close()
    except Exception as e:
        logger.error(f"读取文件 '{file_path}' 时出错: {e}")
        logger.error(traceback.format_exc())
        return ''



'''读取ppt  python-pptx'''

from pptx import Presentation

def read_ppt(ppt_file_path):
    """读取PPT文件内容并返回文本"""
    try:
        logger.warning(f'ppt读取文件，文件路径={ppt_file_path}')
        with open(ppt_file_path, 'rb') as f:
            prs = Presentation(f)

            content = []
            for slide in prs.slides:
                slide_content = []
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        slide_content.append(shape.text)
                content.append("\n".join(slide_content))

            logger.warning(f"PPT文件读取成功，现在返回内容")
            return content
    except Exception as e:
        logger.error(f"读取PPT文件时出错: {e}")
        logger.error(traceback.format_exc())
        return ''


'''读取csv文件'''

import csv

def read_csv(file_path):
    try:
        logger.warning(f'csv读取文件，文件路径={file_path}')
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # 创建csv阅读器
            csv_reader = csv.reader(csvfile)
            data = []
            for row in csv_reader:
                data.append(row)  # 每行是一个列表

            logger.warning(f"CSV文件读取成功，现在返回内容")
            return data
    except Exception as e:
        logger.error(f"读取CSV文件时出错: {e}")
        logger.error(traceback.format_exc())
        return ''



















