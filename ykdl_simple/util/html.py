# -*- coding: utf-8 -*-
import re
import requests
from urllib.request import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler, getproxies
from urllib.parse import urlencode, urlparse, urlsplit, urljoin, parse_qs

from .match import match1


fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.1) Gecko/20100101 Firefox/60.1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'
}

fake_headers_without_ae = fake_headers.copy()
del fake_headers_without_ae['Accept-Encoding']


def add_header(key, value):
    global fake_headers, fake_headers_without_ae
    fake_headers[key] = value
    if key != 'Accept-Encoding':
        fake_headers_without_ae[key] = value

def unicodize(text):
    return re.sub(r'\\u([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])', lambda x: chr(int(x.group(0)[2:], 16)), text)

def ungzip(data):
    """Decompresses data for Content-Encoding: gzip.
    """
    from io import BytesIO
    import gzip
    buffer = BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()

def undeflate(data):
    """Decompresses data for Content-Encoding: deflate.
    (the zlib compression is used.)
    """
    import zlib
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data)+decompressobj.flush()


def get_content(url, headers=fake_headers, data=None, charset=None):
    """Gets the content of a URL via sending a HTTP GET request.
    Args:
        url: A URL.
        headers: Request headers used by the client.
        decoded: Whether decode the response body using UTF-8 or the charset specified in Content-Type.
    Returns:
        The content as a string.
    """
    req = Request(url, headers=headers, data=data)
    #if cookies_txt:
    #    cookies_txt.add_cookie_header(req)
    #    req.headers.update(req.unredirected_hdrs)
    response = urlopen(req)
    data = response.read()

    # Handle HTTP compression for gzip and deflate (zlib)
    resheader = response.info()
    if 'Content-Encoding' in resheader:
        content_encoding = resheader['Content-Encoding']
    elif hasattr(resheader, 'get_payload'):
        payload = resheader.get_payload()
        if isinstance(payload, str):
            content_encoding =  match1(payload, r'Content-Encoding:\s*([\w-]+)')
        else:
            content_encoding = None
    else:
        content_encoding = None
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    if charset == 'ignore':
        return data

    # Decode the response body
    if charset is None:
        if 'Content-Type' in resheader:
            charset = match1(resheader['Content-Type'], r'charset=([\w-]+)')
        charset = charset or match1(str(data), r'charset=\"([\w-]+)', 'charset=([\w-]+)') or 'utf-8'
    # print("get_content> Charset: " + charset)
    try:
        data = data.decode(charset, errors='replace')
    except:
        print("wrong charset for {}".format(url))
    return data


def get_content_fallback(url):
    result = requests.get(url, headers=fake_headers)
    return result.text