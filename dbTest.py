'''
author: cynthiaL
time: 2021-06-07
last change: 2021-06-07
info: for db connection
'''
import pymysql

conn=pymysql.connect(
    host='localhost',
    user='root',
    passwd='19991230',
    port=3306,
    db='infoSec',charset='utf8',autocommit=True
)
# cur=conn.cursor()

def runSingleSql(sql):
    cur=conn.cursor()
    try:
        cur.execute(sql)
        print('successfully')
    except:
        print("❗️failed")
        conn.rollback()
    finally:
        cur.close()

def runSql(sql,tuple):
    cur=conn.cursor()
    try:
        cur.execute(sql,tuple)
        print('successfully')
    except:
        print("\033[31m%s"%"failed")
        conn.rollback()
    finally:
        cur.close()

def showSelectResult(sql):
    cur=conn.cursor()
    try:
        result=cur.execute(sql)
        a=cur.fetchall()
        content=a[0][0]
    except:
        content='selection failed'
    finally:
        cur.close()
        # conn.close()
        print(content)
    return content

def saveAsFile(filename:str,stuff):
    with open(filename,mode='w',encoding='utf-8') as f:
            f.write(stuff)
            f.write('\n')




