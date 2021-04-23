# -*- coding: utf-8 -*-
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_path = os.path.dirname(current_dir)
sys.path.append(parent_path)

import json
import time
from random import random
from urllib.parse import urlparse

from you_get.common import *


class SoHu(object):
    def __init__(self):
        pass

    def sohu_download(self, url):
        if re.match(r'http://share.vrs.sohu.com', url):
            vid = r1('id=(\d+)', url)
        else:
            html = get_html(url)
            vid = r1(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?', html) or r1(r'bid:\'(\d+)\',', html) or r1(r'bid=(\d+)', html)
        assert vid
        print(vid)

        info = json.loads(get_decoded_html('http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % vid))
        # print(info)
        if info and info.get("data", ""):
            for qtyp in ["oriVid", "superVid", "highVid", "norVid", "relativeId"]:
                if 'data' in info:
                    hqvid = info['data'][qtyp]
                else:
                    hqvid = info[qtyp]
                if hqvid != 0 and hqvid != vid:
                    info = json.loads(get_decoded_html('http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % hqvid))
                    if not 'allot' in info:
                        continue
                    break
            host = info['allot']
            prot = info['prot']
            tvid = info['tvid']
            urls = []
            data = info['data']
            title = data['tvName']
            size = sum(data['clipsBytes'])
            assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
            for fileName, key in zip(data['su'], data['ck']):
                urls.append(self.real_url(fileName, key, data['ch']))
        
        else:
            info = json.loads(get_decoded_html('http://my.tv.sohu.com/play/videonew.do?vid=%s&referer=http://my.tv.sohu.com' % vid))
            host = info['allot']
            prot = info['prot']
            tvid = info['tvid']
            urls = []
            data = info['data']
            title = data['tvName']
            size = sum(map(int, data['clipsBytes']))
            assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
            for fileName, key in zip(data['su'], data['ck']):
                urls.append(self.real_url(fileName, key, data['ch']))
        
        print(urls)

    def real_url(self, fileName, key, ch):
        url = "https://data.vod.itc.cn/ip?new=" + fileName + "&num=1&key=" + key + "&ch=" + ch + "&pt=1&pg=2&prod=h5n"
        return json.loads(get_html(url))['servers'][0]['url']

if __name__ == "__main__":
    site = "sohu"
    url = "https://tv.sohu.com/v/dXMvMzM2MTQwMTA5LzI1MTEzNTAzOC5zaHRtbA==.html"
    sohu = SoHu()
    sohu.sohu_download(url)
