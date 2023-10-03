'''
author: cynthiaL
time: 2021-06-08
last change: 2021-06-13
info: spider for media, fill up table information in db
'''
import requests
import json
import db
import otherTools


# 爬取b站实时热门视频
url = 'https://api.bilibili.com/x/web-interface/popular?ps=20&pn='
# 解决反爬虫——模仿浏览器  建立字典key：value
ua = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}

def spiderVideoInfo(url):
    """
    爬取视频基本信息
    :return: no returns
    """

    #请求各视频概览信息和播放地址
    otherTools.log_getResponseFromUrl(url)
    text = requests.get(url, headers=ua).text
    headerSeq=requests.get(url, headers=ua).headers
    db.saveAsFile("seq/infoseq/hotVideos.txt",text)
    db.saveAsFile("seq/infoseq/hotVideosHeaders.txt",str(headerSeq))
    otherTools.log_successFlag()

    #筛选
    res=json.loads(text)['data']['list']

    otherTools.log('saving to database...')
    for i in range(len(res)):
        video_info=res[i]
        # print(str(video_info))
        aid=video_info['aid'] #aid
        bvid=video_info['bvid'] #bvid
        cid=video_info['cid'] #cid
        desc=video_info['desc'] #description
        title=video_info['title'] #title
        pic_url=video_info['pic'] #cover_url
        owner=video_info['owner']['name'] #owner
        zone=video_info['tname']
        detail_url=video_info['short_link']

        stat=video_info['stat']
        clicks_num=stat['view']
        comments_num=stat['reply']
        likes_num=stat['like']

        print('inserting '+bvid+'...')
        data={
            'video_id':bvid,
            'avid':str(aid),
            'cid':str(cid),
            'titile':title,
            'desc':desc,
            'owner':owner,
            'zone':zone,
            'clicksNum':str(clicks_num),
            'commentsNum':str(comments_num),
            'likesNum':str(likes_num),
            'coverURL':pic_url,
            'detailUrl':detail_url,
            'deleted': 0,
            'downloadDenied': 0
        }

        table='information'
        keys=','.join(data.keys())
        values=','.join(['%s']*len(data))
        sql='insert into {table} values{values}'.format(table=table,keys=keys,values=tuple(data.values()))
        # print(sql)
        # print(tuple(data.values()))
        db.runSingleSql(sql)

        otherTools.log_successFlag()

def spider100videos():
    """
    爬取实时热门榜前5page视频信息
    :return:
    """
    # clear data in table infomation
    otherTools.log('clearing table information ...')
    clearTableSql = 'truncate table information'
    db.runSingleSql(clearTableSql)
    print('table information cleared\n')
    otherTools.log_successFlag()

    for i in range(5):
        this_url=url+str(i+1)
        spiderVideoInfo(this_url)

    print('selected information done')
