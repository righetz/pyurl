#!/usr/bin/python3
"""Simple CUrl porting for Python3
"""

import urllib.request, re
import sys
import argparse
from urllib.parse import urlencode
import gettext
import locale

def main():
    """"main method"""
    language_set()
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', metavar='output_file', help='Write output to file')
    parser.add_argument('-i', action='store_true', help='Show request headers')
    parser.add_argument('url', help='Define target URL')
    parser.add_argument('-d', metavar='DATA', help='Http POST data between quotation marks')
    parser.add_argument('-c', action='store_true', help='Show Http code')
    parser.add_argument('-a', metavar='user_agent', help='Insert custom user agent')
    flags = set_flags(parser.parse_args())
    get_flags(flags)

def language_set():
    """read from UNIX or windows locale informations and set language"""
    ita = gettext.translation('pyurl', localedir='locale', languages=['it'])
    eng = gettext.translation('pyurl', localedir='locale', languages=['en'])
    if locale.getlocale()[0] == 'it_IT' or locale.getlocale()[0] == 'ita':
        ita.install()
    else:
        eng.install()

def set_flags(args):
    """flags setting from namespace"""
    flags = {}
    flags['user_agent'] = args.a
    flags['http_code'] = args.c
    flags['http_post'] = args.d
    flags['headers'] = args.i
    flags['out_file'] = args.o
    flags['url'] = args.url
    return flags

def get_flags(flags):
    """flags control and methods invoke"""
    headers = ""
    post_data = None
    url = str(flags['url'])
    if flags['http_post'] != None:
        post_data = data_post_format(flags['http_post'])
    if not re.match("http://", url):
        url = "http://" + url
    text = get_source(url, post_data, flags['http_code'], flags['user_agent'])
    if flags['headers'] == True:
        if flags['out_file'] != None:
            headers = get_headers(url, flags['user_agent'])
            save_to_file(text, flags['out_file'], headers)
        else:
            headers = get_headers(url, flags['user_agent'])
            print(headers)
            print(text)
    elif flags['out_file'] != None:
        save_to_file(text, flags['out_file'], headers)
    else:
        print(text)

def connect(url, post_data, user_agent):
    """connection method"""
    try:
        if user_agent == None:
            user_agent = "PyUrl V1.0"
        req = urllib.request.Request(
            url,
            headers={"User-Agent" : user_agent
                    }
            )
        if post_data != None:
            req.data = post_data.encode('utf-8')
        src = urllib.request.urlopen(req)
    except urllib.error.HTTPError as err:
        sys.exit(err)
    except urllib.error.URLError:
        sys.exit(_("Could not resolve host %s\nCheck your connection") % url)
    return src

def data_post_format(data_string):
    """format input data to be handled by urllib.request"""
    data_list = data_string.split("&")
    data_map = {}
    for dato in data_list:
        temp = dato.split("=")
        try:
            data_map[temp[0]] = temp[1] #check if user input is correct
        except IndexError:
            sys.exit(_("Specify every POST input as \"key=value\" "))
    return urlencode(data_map)

def get_source(url, post_data, http_code, user_agent):
    """set connection to url and extract source"""
    src = connect(url, post_data, user_agent)
    charset = src.headers.get_param('charset')
    if not charset:
        charset = 'utf-8' # workaround for missing charset header data
    content = []
    if http_code:
        content.append(_("Http code: %d\n\n ")% src.getcode())
    while True:
        line = src.readline()
        if line:
            content.append(line.decode(charset))
        else:
            src.close()
            break
    return "".join(content)

def get_headers(url, user_agent):
    """return URL headers"""
    src = connect(url, None, user_agent)
    return str(src.headers)

def save_to_file(text, outfile, headers):
    """write to file"""
    try:
        file_writer = open(outfile, 'w')
    except FileNotFoundError:
        sys.exit(_("Specified directory does not exists"))
    except IsADirectoryError:
        sys.exit(_("Target path is a directory, include file name"))
    except IOError:
        sys.exit(_("Input/Output error\nMaybe you don't have enough privileges?"))
    if headers:
        file_writer.write(headers)
    file_writer.write(text)
    file_writer.close()

if __name__ == "__main__":
    main()
