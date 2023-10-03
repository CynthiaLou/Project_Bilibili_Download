'''
author: cynthiaL
time: 2021-06-08
last change: 2021-06-13
info: create cloud pic for danmaku in specific video, download it to local foder named 'currentCloud.jpg'
'''
import otherTools
import re
import requests
import csv
import jieba
from wordcloud import WordCloud

import db

url='https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid=350063750&date=2021-06-07'
url1='https://api.bilibili.com/x/v1/dm/list.so?oid=1&oid={cid}'
headers={
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    ,'cookie':"_uuid=1F523E00-B3AF-2578-B9B7-A8ECF10B0DE832999infoc; buvid3=34C6D085-620E-4BCF-96A7-5DB821D6A9EF34762infoc; fingerprint=d1bc619569d8d25190f54171d4488b63; buvid_fp=34C6D085-620E-4BCF-96A7-5DB821D6A9EF34762infoc; buvid_fp_plain=34C6D085-620E-4BCF-96A7-5DB821D6A9EF34762infoc; SESSDATA=73c50a8b%2C1638613562%2C5bd37%2A61; bili_jct=2820b58fde3531796956415ccb2429c6; DedeUserID=23372980; DedeUserID__ckMd5=e6b1afbe5aa78895; sid=5zr2zo6f; bsource=search_bing; CURRENT_FNVAL=80; blackside_state=1; rpdid=|(u)YRm|~R|J0J'uYkJ|YRJml; LIVE_BUVID=AUTO6716231395912479; PVID=2; bfe_id=5db70a86bd1cbe8a88817507134f7bb5"
}
current_filename=''
current_bv=''

def download_page(url):
    """
    获取url对应的响应报文对象
    :param url:
    :return:
    """
    otherTools.log_getResponseFromUrl(url)
    res=requests.get(url,headers=headers)
    otherTools.log_successFlag()
    return res

def getcid(bv):
    """
    通过bv号获取cid号
    :param bv:
    :return:cid
    """
    otherTools.log(f'getting cid from {bv} ...')
    current_filename=bv+'.txt'
    current_bv=bv
    cursor=db.conn.cursor()
    # print(bv)
    sql='select cid from information where information.video_id='+"'"+bv+"'"
    print(sql)
    result=cursor.execute(sql)
    datas=cursor.fetchall()
    # print(result)
    print(datas)
    otherTools.log_successFlag()
    return datas[0][0]

def getDanmaku(cid):
    """
    通过cid获取弹幕列表
    :param cid:
    :return: 弹幕列表
    """
    otherTools.log(f'getting danmaku with cid [{cid}] ...')
    url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={cid}'
    res=download_page(url)
    otherTools.log_successFlag()
    ####untested
    otherTools.log_fileSaving('response seq text of danamaku',f'seq/danmakuSeq/{cid}.txt')
    db.saveAsFile(f'seq/danmakuSeq/{cid}.txt',res.text)
    otherTools.log_successFlag()
    ####
    res_xml=res.content.decode('utf-8')
    pattern=re.compile('<d.*?>(.*?)</d>')
    damakuList=pattern.findall(res_xml)
    return damakuList

def saveDanmakuList(danmakuList,filename):
    """
    保存弹幕文件
    :param danmakuList: 弹幕列表
    :return:
    """
    otherTools.log_fileSaving('danmakuList',"seq/danmakuList/"+filename)
    with open("seq/danmakuList/"+filename,mode='w',encoding='utf-8') as f:
        for oneDanmaku in danmakuList:
            f.write(oneDanmaku)
            f.write('\n')
    otherTools.log_successFlag()

def getVideoDanmaku(bv):
    """
    获取指定bv号视频对象的弹幕列表，并保存到文件
    :param bv:
    :return:
    """
    cid=getcid(bv)
    danmakuList=getDanmaku(cid)
    saveDanmakuList(danmakuList,f'{bv}.txt')

def read_file(filename):
    """
    读取弹幕文件
    :param filename: 文件名路径
    :return:
    """
    with open(filename, mode='r', encoding='utf-8') as f:
        danmu = f.read()
        print('file successfully readed')
        return danmu

def jieba_cut(str):
    """
    利用jieba库切割字符串
    :param str:
    :return:
    """
    otherTools.log('cutting text...')
    jieba.suggest_freq('前方高能', tune=True)# 指定不切割词组
    jieba.suggest_freq('正道的光', tune=True)
    jieba.suggest_freq('下次一定', tune=True)
    cut_list = jieba.lcut(str)
    print('danmaku words successfully cut')
    otherTools.log_successFlag()
    return cut_list

def gen_word_cloud(cut_list,bv):
    """
    生成词云图，并保存到本地
    :param cut_list: 切割后的词组列表
    :return:
    """
    otherTools.log('generating danmaku cloud ...')
    word_str=' '.join(cut_list)
    wc_settings={
        'font_path': 'resources/simhei.ttf',  # 字体
        'width': 800,  # 图片宽度
        'height': 600,  # 图片高度
        'max_words': 200,  # 最大词数
        'background_color': 'white'  # 背景颜色
    }
    wc=WordCloud(**wc_settings).generate(word_str)
    print('cloud object generated successfully')
    wc.to_file(f'cloud#{bv}.jpg')#前面加上static的路径
    print('cloud generated successfully')
    otherTools.log_successFlag()

def getDanmakuCloud(bv):
    """
    生成指定bv号对应的弹幕词云图
    :param bv: 指定bv号
    :return: 将词云图保存到本地currentCloud.jpg文件
    """
    getVideoDanmaku(bv)
    str=read_file(f'seq/danmakuList/{bv}.txt')
    cut_list=jieba_cut(str)
    ###
    gen_word_cloud(cut_list,bv)

if __name__ == '__main__':
    getDanmakuCloud("BV1MV41147aJ")
    # cid='350235654'
    # getDanmaku(cid)