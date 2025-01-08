# -*- coding: utf-8 -*-
# 下载抖音无水印视频
from bs4 import BeautifulSoup
import requests
import re
import os
import time


def main():
    print("抖音短视频，无水印素材下载")
    url = input("请输入链接地址：")
    article = get_code(url)
    pattern = re.compile('s_vid=([a-z0-9]+)&line=0')
    script = article.find("script", text=pattern)
    print(777,script)
    s_vid = pattern.search(script.text).group(1)
    # 拼合链接
    video_url = 'https://aweme.snssdk.com/aweme/v1/play/?s_vid=%s&line=0' % s_vid
    res_url = get_redirect_url(video_url)
    # 视频名称
    video_name_data = get_true_name(url)
    # 进行下载
    print("正在下载中~~~~")
    do_load_media(res_url, './video/%s.mp4' % video_name_data)
    print("运行完成")


# 获取源代码
def get_code(url):
    if not url:
        url = input("请输入链接地址：")
    # 获取响应码
    res = requests.get(url)
    code = res.status_code
    if code != 200:
        print('无法响应')
    # 获取页面代码
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        "Cookie": "anonymid=j3jxk555-nrn0wh; _r01_=1; _ga=GA1.2.1274811859.1497951251; _de=BF09EE3A28DED52E6B65F6A4705D973F1383380866D39FF5; ln_uact=mr_mao_hacker@163.com; depovince=BJ; jebecookies=54f5d0fd-9299-4bb4-801c-eefa4fd3012b|||||; JSESSIONID=abcI6TfWH4N4t_aWJnvdw; ick_login=4be198ce-1f9c-4eab-971d-48abfda70a50; p=0cbee3304bce1ede82a56e901916d0949; first_login_flag=1; ln_hurl=http://hdn.xnimg.cn/photos/hdn421/20171230/1635/main_JQzq_ae7b0000a8791986.jpg; t=79bdd322e760beae79c0b511b8c92a6b9; societyguester=79bdd322e760beae79c0b511b8c92a6b9; id=327550029; xnsid=2ac9a5d8; loginfrom=syshome; ch_id=10016; wp_fold=0"
    }
    content = requests.get(url, headers=headers, timeout=3000)
    # 设置编码格式
    content.coding = 'UTF-8'
    # 以文本形式获取源码
    content_text = content.text
    # 利用解析器进行解析操作
    article = BeautifulSoup(content_text, "html.parser")
    return article


# 下载视频
def do_load_media(url, save_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'}
        pre_content_length = 0
        # 循环接收视频数据
        while True:
            # 若文件已经存在，则断点续传，设置接收来需接收数据的位置
            if os.path.exists(save_path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(save_path)
            res = requests.get(url, stream=True, headers=headers)

            content_length = int(res.headers['content-length'])
            # 若当前报文长度小于前次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
            if content_length < pre_content_length or (
                    os.path.exists(save_path) and os.path.getsize(save_path) == content_length) or content_length == 0:
                break
            pre_content_length = content_length

            # 写入收到的视频数据
            with open(save_path, 'ab') as file:
                file.write(res.content)
                file.flush()
                print('下载成功：文件大小 : %s  总下载大小:%s' % (StrOfSize(os.path.getsize(save_path)), StrOfSize(content_length)))
    except Exception as e:
        print(e)


# 文件大小转化
def StrOfSize(size):
    '''
    auth: wangshengke@kedacom.com ；科达柯大侠
    递归实现，精确为最大单位值 + 小数点后三位
    '''

    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level + 1 > len(units):
        level = -1
    return ('{}.{:>03d} {}'.format(integer, remainder, units[level]))


# 重定向的链接，模拟安卓请求地址
def get_redirect_url(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Upgrade-Insecure-Requests': '1',
    }
    data = requests.get(headers=header, url=url, timeout=5)
    return data.url


# 获取名称
def get_true_name(url):
    true_url = get_redirect_url(url)
    article = get_code(true_url)
    name = article.find(class_="desc")
    if name:
        return name.string
    else:
        return time.time()


if __name__ == '__main__':
    main()
