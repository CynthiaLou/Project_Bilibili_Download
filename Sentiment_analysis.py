from snownlp import SnowNLP
from snownlp import sentiment
import pymysql
import matplotlib.pyplot as plt
import numpy as np
import db


'''
s1 = SnowNLP(u"朱厘米老师！双厨狂喜[打call]")
print(" ".join(s1.words))
print(s1.sentiments)
'''
# db = pymysql.connect("localhost", "root", "wanddy", "slab")
cursor = db.conn.cursor()



def traindata():
    print('training sentiment...')
    sentiment.train('train/neg.txt', 'train/pos.txt')
    sentiment.save('train/forbilibili')
    print('program trained')


def savefile():

    cursor.execute('select video_id, comment_content from comments')
    comments = cursor.fetchall()
    print(comments[0][1])
    bv = ''
    for onecomment in comments:
        print(onecomment)
        if onecomment[0] != bv or bv == '':
            print("change")
            bv = onecomment[0]
            file = open(r'senti/comments/%s.txt' % bv, 'w', encoding='utf-8')
        comment = onecomment[1]
        # print(comment)
        # print(type(comment))
        file.write('%s\n\n'%comment)
    file.close()


def analyse():
    ###清空senti表
    print('clearing table senti ...')
    cursor.execute('truncate table senti')
    print('table cleared')

    cursor.execute('select distinct video_id from comments')
    video_id_list = cursor.fetchall()
    print(video_id_list)
    for video_id in video_id_list:
        #读取每一个视频
        this_comments = open("senti/comments/%s.txt"%video_id, "r", encoding='utf-8')
        line = this_comments.readlines()
        sentiments = []
        sentimentslist = []

        num = 0
        for i in line:
            #读取每一行评论内容
            if i == '\n':
                the_end = 0
                #print(num)
                #print(sentiments)
                for sentiment in sentiments:
                    #print(sentiment)
                    the_end = the_end + sentiment
                    #print(the_end)
                the_end = the_end / num
                the_end = round(the_end, 4)
                print(the_end)
                sentimentslist.append(the_end)
                sentiments = []
                num = 0
                continue


            s = SnowNLP(i)

            #print("++++++++++++++++++++++++++++++++++++")
            num = num + 1
            print(i)
            #print(num)


            #print(round(s.sentiments, 4))
            #print("***************************************")
            sentiments.append(round(s.sentiments, 4))

        print(sentimentslist)
        ###统计当前视频的热评情感平均值
        sumSenti=0
        for i in sentimentslist:
            sumSenti=sumSenti+i
        dime = len(sentimentslist)
        result=sumSenti/dime
        ###写入senti表
        # cursor=db.conn.cursor()
        video_id=video_id[0]
        sql=f'insert into senti values("{video_id}",{result})'
        print(sql)
        cursor.execute(sql)
        plt.figure(figsize=(25,10))
        plt.plot(np.arange(0, dime, 1), sentimentslist, 'k-')
        plt.xlabel('Number')
        plt.ylabel('Sentiment')
        plt.title('Analysis of Sentiments')
        plt.savefig('./senti/pic/%s.jpg'%video_id)


def savefile_one(video_id):

    cursor.execute('select comment_content from comments where video_id=%s', video_id)
    comments = cursor.fetchall()
    # print(comments)
    file = open(r'%s.txt' % video_id, 'w', encoding='utf-8')
    for onecomment in comments:
        # print(onecomment)

        comment = onecomment[0]
        # print(comment)
        # print(type(comment))
        file.write('%s\n\n'%comment)
    file.close()


def analyse_one(video_id):
    this_comments = open("%s.txt"%video_id, "r", encoding='utf-8')
    line = this_comments.readlines()
    sentiments = []
    sentimentslist = []
    num = 0
    for i in line:
        if i == '\n':
            #print("===============================")
            the_end = 0
            #print(num)
            #print(sentiments)
            for sentiment in sentiments:
                #print(sentiment)
                the_end = the_end + sentiment
                #print(the_end)
            the_end = the_end / num
            the_end = round(the_end, 4)
            print(the_end)
            sentimentslist.append(the_end)
            sentiments = []
            num = 0
            continue


        s = SnowNLP(i)

        #print("++++++++++++++++++++++++++++++++++++")
        num = num + 1
        print(i)
        #print(num)


        #print(round(s.sentiments, 4))
        #print("***************************************")
        sentiments.append(round(s.sentiments, 4))

    print(sentimentslist)
    dime = len(sentimentslist)
    sumSenti = 0
    for i in sentimentslist:
        sumSenti = sumSenti + i
    result=sumSenti/dime
    print(result)
    ###写入senti表
    sql = f'insert into senti values("{video_id}",{result})'
    cursor.execute(sql)
    print('insert successfully')
    # print(dime)
    plt.figure(figsize=(25,10))
    plt.plot(np.arange(0, dime, 1), sentimentslist, 'k-')
    plt.xlabel('Number')
    plt.ylabel('Sentiment')
    plt.title('Analysis of Sentiments')
    plt.savefig('pictures/%s.jpg'%video_id)

def getDeniedBvList(n:int):
    """
    获取最消极的n个视频
    :return:不允许下载的视频bv列表
    """
    n=str(n)
    cursor.execute(f'select t1.video_id from (select senti.video_id from senti order by senti asc) t1 limit {n}')
    result=cursor.fetchall()
    bv_list=[]
    for i in result:
        bv_list.append(i[0])
    print(bv_list)
    return bv_list

def setVideoDenied(bv_list):
    """
    将bv_list中的视频设为denied=1的视频
    :param bv_list:
    :return:
    """
    print('setting denied videos ...')
    for i in bv_list:
        cursor.execute(f"update information set information.downloadDenied=1 "
                       f"where information.video_id='{i}'")
    print('done')


# traindata()
# savefile()
# analyse()
if __name__ == '__main__':
    savefile()
    analyse()
    list=getDeniedBvList(10)
    setVideoDenied(list)