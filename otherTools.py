'''
author: cynthiaL
time: 2021-06-13
last change:
info: 一些其他功能
'''
import datetime

def getTime():
    """
    获取系统时间[yyyy-mm-dd hh-mm-ss]
    :return: 获取的时间字符串
    """
    time=datetime.datetime.now().strftime('[%F %T]')
    return time

def getTimeWithoutSpace():
    time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return time

def log(content):
    """
    写入指定日志内容到文件中
    :param content: 日志内容
    :return:
    """
    time=getTime()
    text=time+' '+content
    f=open("back-end_log.txt",'a')
    f.write(text+'\n')
    f.close()

def log_getResponseFromUrl(url:str):
    log(f'getting response from {url} ...')

def log_successFlag():
    log('--succeed')

def log_fileSaving(content,filename):
    log(f'saving [{content}] as file named {filename} ...')
