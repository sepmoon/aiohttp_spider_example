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
url = 'http://admin.com'         


def getPicUrl(html, url):
    """
    过滤HTML内容，返回下载链接的列表
    """
    reLists = []
    reList = regulars.findall(html)
    _ = re.split(r'://|/', url)
    domain = '{s1}://{s2}'.format(s1=_[0], s2=_[1])
    for num in range(len(reList)):
        try:
            list_str = reList[num].split('="')[1]
            if re.search(r'http://|https://', list_str):
                reLists.append("{}".format(list_str))
            else:
                reLists.append("{s0}{s1}".format(s0=domain, s1=list_str))
        except BaseException:
            pass
    reLists = list(dict.fromkeys(reLists).keys())  # 提取图片链接去重，返回一个列表
    return reLists


async def fetch(session, url, mode='default'):
    async with session.get(url, headers=headers) as response:
        if mode == 'default':
            return await response.text()
        elif mode == 'pic':
            return await response.read()
        else:
            pass


async def downLoad(url):
    """
    下载图片
    """
    picName = re.split(r'//|/', url)[-1].split('.')
    async with aiohttp.ClientSession() as session:
        async with AIOFile('{}.{}'.format(picName[0], picName[1]), 'wb') as afo:
            write_ = Writer(afo)
            result = await fetch(session, url, mode='pic')
            await write_(result)
            await afo.fsync()


async def getHtml(url):
    """
    获取URL页面内容
    """
    async with aiohttp.ClientSession() as session:
        return await fetch(session, url)


if __name__ == '__main__':
    startTime = time.time()
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  #uvloop用来代替asyncio默认事件循环
    loop = asyncio.get_event_loop()
    download_urls = loop.run_until_complete(getHtml(url))
    download_urls = getPicUrl(download_urls, url)
    tasks = [downLoad(url_) for url_ in download_urls]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    print('All Download Finish.')
    endTime = time.time() - startTime
    print(endTime)

