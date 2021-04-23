# -*- coding: utf-8 -*-
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_path = os.path.dirname(current_dir)
sys.path.append(parent_path)

import json
import hashlib

from urllib.parse import urlencode
from xml.dom.minidom import parseString
from util.match import match1
from util.html import get_content

APPKEY = '84956560bc028eb7'
SECRETKEY = '94aba54af9065f71de72f5508f1cd42e'
api_url = 'https://bangumi.bilibili.com/player/web_api/v2/playurl'

API_view = 'https://api.bilibili.com/x/web-interface/view?bvid='

fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.1) Gecko/20100101 Firefox/60.1',
    'Referer': 'https://www.bilibili.com/'
}

def sign_api_url(api_url, params_str, skey):
    chksum = hashlib.md5(compact_bytes(params_str + skey, 'utf8')).hexdigest()
    return '{}?{}&sign={}'.format(api_url, params_str, chksum)

def parse_cid_playurl(xml):
    urls = []
    size = 0
    doc = parseString(xml.encode('utf-8'))
    fmt = doc.getElementsByTagName('format')[0].firstChild.nodeValue
    qlt = doc.getElementsByTagName('quality')[0].firstChild.nodeValue
    aqlts = doc.getElementsByTagName('accept_quality')[0].firstChild.nodeValue.split(',')
    for durl in doc.getElementsByTagName('durl'):
        urls.append('https' + durl.getElementsByTagName('url')[0].firstChild.nodeValue[4:])
        size += int(durl.getElementsByTagName('size')[0].firstChild.nodeValue)
    return urls, size, fmt, qlt, aqlts

def compact_bytes(string, encode):
    return string.encode(encode)


class BiliBan(object):
    name = u'哔哩哔哩 番剧 (Bilibili Bangumi)'

    format_2_type_profile = {
        'hdflv2': ('BD', u'高清 1080P+'), #112
        'flv':    ('BD', u'高清 1080P'),  #80
        'flv720': ('TD', u'高清 720P'),   #64
        'hdmp4':  ('TD', u'高清 720P'),   #48
        'flv480': ('HD', u'清晰 480P'),   #32
        'mp4':    ('SD', u'流畅 360P'),   #16
        'flv360': ('SD', u'流畅 360P'),   #15
        }

    sorted_format = ['BD', 'TD', 'HD', 'SD']


    def prepare(self, url):
        vid, title, artist = self.get_page_info(url)
        print(vid)
        print(title)
        print(artist)

        def get_video_info(vid, qn=0):
            # need login with "qn=112"
            if int(qn) > 80:
                return

            api_url = self.get_api_url(vid, qn)
            html = get_content(api_url)
            # self.logger.debug('HTML> ' + html)
            code = match1(html, '<code>([^<])')
            if code:
                return

            urls, size, fmt, qlt, aqlts = parse_cid_playurl(html)
            if 'mp4' in fmt:
                ext = 'mp4'
            elif 'flv' in fmt:
                ext = 'flv'
                
            print(urls, size, fmt, qlt, aqlts)
            st, prf = self.format_2_type_profile[fmt]
            if urls and st not in info.streams:
                info.stream_types.append(st)
                info.streams[st] = {'container': ext, 'video_profile': prf, 'src' : urls, 'size': size}

            if qn == 0:
                aqlts.remove(qlt)
                for aqlt in aqlts:
                    get_video_info(aqlt)
        
        get_video_info(vid)



    def get_page_info(self, url):
        html = get_content(url)
        date = json.loads(match1(html, '__INITIAL_STATE__=({.+?});'))
        # print(date)
        vid = date['epInfo']['cid']
        mediaInfo = date['mediaInfo']
        self.seasonType = mediaInfo.get('ssType')
        if self.seasonType == 1:
            title = date.get('h1Title')
        else:
            title = match1(html, '<title>(.+?)_\w+_bilibili_哔哩哔哩<')
        upInfo = mediaInfo.get('upInfo')
        artist = upInfo and upInfo.get('name')

        return vid, title, artist

    def get_api_url(self, vid, qn):
        params_str = urlencode([
            ('appkey', APPKEY),
            ('cid', vid),
            ('module', 'bangumi'),
            ('platform', 'html5'),
            ('player', 1),
            ('qn', qn),
            ('season_type', self.seasonType)
        ])
        return sign_api_url(api_url, params_str, SECRETKEY)


if __name__ == '__main__':
    # url = 'https://www.bilibili.com/bangumi/play/ss38353/?spm_id_from=333.851.b_62696c695f7265706f72745f616e696d65.12'
    url = 'https://www.bilibili.com/bangumi/play/ep399420'
    bili = BiliBan()
    bili.prepare(url)