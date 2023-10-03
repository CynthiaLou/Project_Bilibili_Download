'''
author: cynthiaL
time: 2021-06-08
last change: 2021-06-08
info: all spider actions
'''
import spider
import db


def spider100VideoInfo():
    """
    爬取热门榜前100个视频的基本信息，并载入数据库
    :return:
    """
    spider.spider100videos()
    db.conn.close()

if __name__ == '__main__':
    spider100VideoInfo()
