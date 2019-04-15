#! /usr/bin/env python
# -*- coding: utf-8 -*-

from aiofile import AIOFile, Writer
import aiohttp
import asyncio
# import uvloop
import re
import time

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:66.0) Gecko/20100101 Firefox/66.0'}
regulars = re.compile(r'src=.+\.jpg|src=.+\.png')
url = 'http://www.nipic.com/'


def get_pic_url(html, url_):
    """
    过滤HTML内容，返回下载链接的列表
    """
    lists_ = []
    list_ = regulars.findall(html)
    _ = re.split(r'://|/', url_)
    domain = '{s1}://{s2}'.format(s1=_[0], s2=_[1])
    for num in range(len(list_)):
        try:
            list_str = list_[num].split('="')[1]
            if re.search(r'http://|https://', list_str):
                lists_.append("{}".format(list_str))
            else:
                lists_.append("{s0}{s1}".format(s0=domain, s1=list_str))
        except BaseException:
            pass
    lists_ = list(dict.fromkeys(lists_).keys())  # 提取图片链接去重，返回一个列表
    return lists_


async def fetch(session, url_, mode='default'):
    async with session.get(url_, headers=headers) as response:
        if mode == 'default':
            return await response.text()
        elif mode == 'pic':
            return await response.read()
        else:
            pass


async def download(url_):
    """
    下载图片
    """
    pic_name = re.split(r'//|/', url_)[-1].split('.')
    async with aiohttp.ClientSession() as session:
        async with AIOFile('{}.{}'.format(pic_name[0], pic_name[1]), 'wb') as afo:
            write_ = Writer(afo)
            result = await fetch(session, url_, mode='pic')
            await write_(result)
            await afo.fsync()


async def get_html(url_):
    """
    获取URL页面内容
    """
    async with aiohttp.ClientSession() as session:
        return await fetch(session, url_)


if __name__ == '__main__':
    startTime = time.time()
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  uvloop用来代替asyncio默认事件循环
    loop = asyncio.get_event_loop()
    download_urls = loop.run_until_complete(get_html(url))
    download_urls = get_pic_url(download_urls, url)
    tasks = [download(url_) for url_ in download_urls]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    print('All Download Finish.')
    endTime = time.time() - startTime
    print(endTime)
    
