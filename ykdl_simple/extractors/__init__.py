# -*- coding: utf-8 -*-
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_path = os.path.dirname(current_dir)
sys.path.append(parent_path)

from util.html import add_header

import re


add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30')

def get_extractor(url):
    if 'lunbo' in url:
        from . import lunbo as s
    elif re.search("(live[\./]|/izt/)", url):
        from . import live as s
    elif 'bcloud' in url:
        from . import letvcloud as s
    else:
        from . import le as s

    return url