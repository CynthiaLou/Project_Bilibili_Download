'''
author: cynthiaL
time: 2021-06-09
last change: 2021-06-14
info:
每个视频爬热门100评论
多线程爬取视频
'''

import db
import threading
import requests
import time
import otherTools

class getOneVideoCommentsThreading(threading.Thread):
    """
    多线程爬取一个视频的十页评论
    """
    def run(self,bv,time_order=False):
        dex=1
        url = getCommentsUrl(bv, time_order)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
            , "Cookie": ""
        }
        for page in range(1,6):
            current_url = url + str(page)
            # print(current_url)
            try:
                html = requests.get(current_url, headers=headers)
                data = html.json()
                if data['data']['replies']:
                    for i in data['data']['replies']:
                        comment_dex = dex
                        dex = dex + 1
                        comment_content = i['content']['message']
                        username = i['member']['uname']
                        # print(username)
                        likes = str(i['like'])
                        print('one comment info inserting...')
                        sql = f"insert into comments values('{bv}',{comment_dex},'{comment_content}','{username}',{likes})"
                        print(sql)
                        #####
                        db.runSingleSql(sql)
                # time.sleep(1)
            except:
                print(current_url)


def getAvidFromBv(bv:str):
    """
    根据bv号获取视频的avid号
    :param bv: 视频bv号
    :return: avid号 str格式
    """
    otherTools.log(f'getting avid from {bv}')
    cursor=db.conn.cursor()
    bv="'"+bv+"'"
    sql='select information.avid from information where information.video_id='+bv
    # print(sql)
    cursor.execute(sql)
    result=cursor.fetchall()
    # print(result[0][0])
    otherTools.log_successFlag()
    return result[0][0]


def getCommentsUrl(bv:str,sort=False):
    """
    根据bv号获取该视频的评论url
    :param bv: 视频号
    :param sort: true按照时间排序，false按照热度排序
    :return: 评论URL str格式
    """
    otherTools.log(f'getting comments url from {bv} ...')
    avid=getAvidFromBv(bv)
    if sort==True:
        sort=str(1)
    if sort==False:
        sort=str(2)
    url=f"https://api.bilibili.com/x/v2/reply?jsonp=jsonp&type=1&oid={avid}&sort={sort}&pn="
    otherTools.log_successFlag()
    return url


class getAllCommentsThreading(threading.Thread):
    """
    多线程爬取一百个热门视频的所有评论
    """
    def run(self):
        """
            获取实时热门榜的所有视频的所有评论信息
            :param:
            :return:
            """
        # 清除所有评论信息数据库
        otherTools.log('clearing comments table ...')
        print('clearing comments table...')
        clearTableSql = 'truncate table comments'
        db.runSingleSql(clearTableSql)
        print('table comments cleared\n')
        otherTools.log_successFlag()

        # 获取实时热门榜的所有bv
        otherTools.log('getting all hot bvs ...')
        sql = 'select information.video_id from information'
        cursor = db.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        bv_list = result
        # print(bv_list)
        otherTools.log_successFlag()

        # 获取所有的评论信息并载入到数据库中
        otherTools.log('getting top 100 contents from hot bvs ...')
        print('inserting all comments from videos in top 100 hot rank...')
        for bv in bv_list:
            # print(bv[0])
            # getCommentsInfoInOneVideo(bv[0])
            otherTools.log(f'getting top 100 contents from {bv[0]} ...')
            getOneVideoCommentsThreading.run(getOneVideoCommentsThreading, bv[0])
            otherTools.log_successFlag()
            time.sleep(1)
        print('comments get successfully')
        otherTools.log_successFlag()



if __name__ == '__main__':
    # print(avid)
    # getCommentsInfoInOneVideo('BV18h411e7f2')
    # getAllComments()
    # getOneVideoCommentsThreading.run(getOneVideoCommentsThreading,'BV14g411G73h')
    getAllCommentsThreading.run(getAllCommentsThreading)

