# encoding: utf-8

'''
author: cynthiaL
time: 2021-06-10
last change:2021-06-13
info: 单个视频的下载
'''

import requests  
import json
import re
import os
import otherTools
import db

#获取保存路径,从界面输入获取，然后执行demo
filepath='/Users/cynthia/Desktop/test'

class BilibiliVideoSpider(object):
    def __init__(self, url, output_root=''):
        self.url = url
        if not os.path.isdir(output_root):
            output_root =  os.path.abspath(os.path.dirname(__file__))
        self.output_root = output_root
        self.headers = {
            # 'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }   # 定义请求头


    def _match(self, text, pattern):
        """
        正则表达式匹配
        :param text: 匹配文本
        :param pattern: 表达式
        :return:
        """
        match = re.search(pattern, text)
        if match is None:
            print('this pattern was not matched !')
        return json.loads(match.group(1))

    def getHtml(self):
        """
        获取html响应
        :return: 响应的get对象
        """
        try:
            response = requests.get(url=self.url, headers=self.headers)  # 发请求，获取数据 （获取响应对象）
            print(f'status_code: {response.status_code}')
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException:
            print('html request error !')

    def parseHtml(self, response):
        """
        分割报文，获取所需部分，并将完整报文写入指定文件保存
        :param response: 响应的报文
        :return: 视频下载url，音频下载url，视频名称
        """
        playinfo = self._match(response.text, '__playinfo__=(.*?)</script><script>')          # 视频详情json
        initial_state = self._match(response.text, r'__INITIAL_STATE__=(.*?);\(function\(\)') # 视频内容json

        video_url = playinfo['data']['dash']['video'][0]['baseUrl']                        # 视频分多种格式，直接取分辨率最高的视频 1080p
        audio_url = playinfo['data']['dash']['audio'][0]['baseUrl']                        # 取音频地址
        video_name = initial_state['videoData']['title']                                   # 取视频名字
        #保存视频报文内容
        with open(f"seq/videoMediaSeq/{video_name}.txt", mode='w', encoding='utf-8') as f:
            f.write(response.text)
            f.write('\n')
        return video_url, audio_url, video_name

    def video_audio_merge(self, video_src, audio_src, video_dst):
        """
        将视频和音频合并——ffmpeg
        :param video_src: 视频源
        :param audio_src: 音频源
        :param video_dst: 目标合并视频地址
        :return:
        """
        import subprocess
        # print(video_dst)
        command = "ffmpeg -i %s_video.mp4 -i %s_audio.mp4 -c copy %s.mp4 -y -loglevel quiet" % (
            video_src, audio_src, video_dst)
        subprocess.Popen(command, shell=True)
        # print(video_dst)

    def downloadVideo(self, video_url, audio_url, video_name,legalDownload=True):
        """
        下载视频
        :param video_url: 视频url
        :param audio_url: 音频url
        :param video_name: 视频名
        :return:
        """
        if(legalDownload):
            self.headers.update({"Referer": self.url})
            # print(str(self.headers))
            print(f'{video_name} downloading...')
        else:
            self.headers.update({'Referer':"https://www.bilibili.com/video/BV1mN411Q7iT?from=search&seid=18390425215544645491"})
            print('illegal video downloading...')
        # print(video_url)
        video_content = requests.get(video_url, headers=self.headers)
        # print(video_content.headers)
        audio_content = requests.get(audio_url, headers=self.headers)
        print('视频大小：',video_content.headers['content-length'])
        print('音频大小：', audio_content.headers['content-length'])

        # 下载视频
        received_video = 0
        video = f'{self.output_root}/video.mp4'
        with open(video, 'ab') as output:
            while int(video_content.headers['content-length']) > received_video:
                #将所有视频分片进行合并
                self.headers['Range'] = 'bytes=' + str(received_video) + '-'
                response = requests.get(video_url, headers=self.headers)
                output.write(response.content)
                received_video += len(response.content)

        # 下载音频开始
        audio_content = requests.get(audio_url, headers=self.headers)
        received_audio = 0
        audio = f'{self.output_root}/audio.mp4'
        with open(audio, 'ab') as output:
            while int(audio_content.headers['content-length']) > received_audio:
                #将所有音频分片进行合并
                self.headers['Range'] = 'bytes=' + str(received_audio) + '-'
                response = requests.get(audio_url, headers=self.headers)
                output.write(response.content)
                received_audio += len(response.content)
        print('❤️音视频下载完成')
        print('merging video and audio...')

        cursor=db.conn.cursor()
        sql=f'select information.video_id from information where information.title="{video_name}"'
        result=cursor.execute(sql)
        # bv=cursor.fetchall()[0][0]
        # print(bv)
        # ###
        # video_dst =  f"{filepath}/{bv}.mp4"
        video_dst=f"{filepath}/novideo.mp4"


        self.video_audio_merge(video, audio, video_dst)
        print(f'下载的视频: {video_dst}')

        os.remove(video)
        os.remove(audio)


    def video_audio_merge(self, video_src, audio_src, video_dst):
        '''使用ffmpeg单个视频音频合并'''
        import subprocess
        cmd = f"ffmpeg -y -i {audio_src} -i {video_src} -vcodec copy -acodec aac -strict -2 -q:v 1 {video_dst}"
        print('execute cmd:', cmd)
        os.system(cmd)
        # print(video_dst)
        # subprocess.Popen(cmd, shell=True)

    def run(self):
        """
        合法视频的下载处理
        :return:
        """
        response = self.getHtml()
        video_url, audio_url, video_name = self.parseHtml(response)
        self.downloadVideo(video_url, audio_url, video_name)

    def alter(self,file, old_str, new_str):
        """
        替换文件中的字符串
        :param file:文件名
        :param old_str:旧字符串
        :param new_str:新字符串
        :return:
        """
        file_data = ""
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                file_data += line
        with open(file, "w", encoding="utf-8") as f:
            f.write(file_data)

    def illegalRun(self):
        """
        非法视频的下载处理
        :return:
        """
        response = self.getHtml()
        video_url1, audio_url1, video_name = self.parseHtml(response)

        f = open('seq/videoMediaSeq/NoVideo.txt', 'r', encoding='utf-8')
        new_seq = f.read()
        # print(new_seq)
        f.close()
        playinfo1 = self._match(new_seq, '__playinfo__=(.*?)</script><script>')  # 视频详情json
        # print(playinfo1)
        #进行包污染，使其特定部分变成指定视频包内容的传送
        initial_state1 = self._match(new_seq, r'__INITIAL_STATE__=(.*?);\(function\(\)')  # 视频内容json
        video_url = playinfo1['data']['dash']['video'][0]['baseUrl']  # 视频分多种格式，直接取分辨率最高的视频 1080p
        self.alter(f"seq/videoMediaSeq/{video_name}.txt",video_url1,video_url)#同时将seq污染，避免他人获取
        audio_url = playinfo1['data']['dash']['audio'][0]['baseUrl']  # 取音频地址
        self.alter(f"seq/videoMediaSeq/{video_name}.txt",audio_url1,audio_url)
        print("illegal seq dealed")

        self.downloadVideo(video_url, audio_url, video_name,False)
        print("❗️本视频非法，不符合协议要求，将导致无法下载到本地")
        #重置url，以便之后的下载
        self.headers.update({"Referer": self.url})


def get_seid():
    """
    从报文中获取合法ip的seid随机生成码，用于申请视频的响应报文
    :return:
    """
    url='https://api.bilibili.com/x/web-interface/search/default'
    headers={
        'user-agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"

    }
    respond=requests.get(url,headers=headers)
    res=respond.json()
    return res['data']['seid']

def demo(bv,canRun=True):
    """
    用于下载视频的函数
    :param bv: 视频bv号
    :param canRun: 视频是否能被播放
    :return:
    """
    otherTools.log("getting user's seid ...")
    seid=get_seid()#实时获取随机seid
    otherTools.log_successFlag()

    url = f'https://www.bilibili.com/video/{bv}?from=search&seid={seid}'
    otherTools.log_getResponseFromUrl(url)
    b = BilibiliVideoSpider(url)
    otherTools.log_successFlag()

    if canRun:
        otherTools.log(f'downloading video {bv} ...')
        b.run()
        otherTools.log_successFlag()
    else:
        otherTools.log('downloading illegal videos and dealing ...')
        b.illegalRun()
        otherTools.log_successFlag()


if __name__ == '__main__':
    # demo('BV1o64y167qq',False)
    # print(get_seid())
    demo('BV1mN411Q7iT')