#!/bin/python3
"""Simple CUrl porting for Python3
"""

import urllib.request, re
import sys
import argparse
from urllib.parse import urlencode

def main():
    """"main method"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', metavar='outfile', help='Write output to file')
    parser.add_argument('-i', action='store_true', help='Show request headers')
    parser.add_argument('url', help='Define target URL')
    parser.add_argument('-d', metavar='DATA', help='Http POST data between quotation marks')
    parser.add_argument('-c', action='store_true', help='Show Http code')
    print(parser.parse_args())
    control(parser.parse_args())

def control(args):
    """arguments control and methods invoke"""
    headers = ""
    post_data = None
    url = str(args.url)
    if args.d != None:
        post_data = data_post_format(args.d)
    if not re.match("http://", url):
        url = "http://" + url
    text = get_file(url, post_data, args.c)
    if args.i == True:
        if args.o != None:
            headers = get_headers(url)
            save_to_file(text, args.o, headers)
        else:
            headers = get_headers(url)
            print(headers)
            print(text)
    elif args.o != None:
        save_to_file(text, args.o, headers)
    else:
        print(text)

def connect(url, post_data):
    """connection method"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent" : "PyUrl V1.0"
                    }
            )
        if post_data != None:
            req.data = post_data.encode('utf-8')
        src = urllib.request.urlopen(req)
    except urllib.error.HTTPError as err:
        sys.exit(err)
    except urllib.error.URLError:
        sys.exit("Could not resolve host %s\nCheck your connection" % url)
    return src

def data_post_format(data_string):
    """format input data to be handled by urllib.request"""
    data_list = data_string.split("&")
    data_map = {}
    for dato in data_list:
        temp = dato.split("=")
        data_map[temp[0]] = temp[1]
    return urlencode(data_map)

def get_file(url, post_data, http_code):
    """print to stdout"""
    src = connect(url, post_data)
    charset = src.headers.get_param('charset')
    if not charset:
        charset = 'latin-1'
        # workaround for missing charset header data
    content = []
    if http_code:
        content.append("Http code: %d\n\n "% src.getcode())
    while True:
        line = src.readline()
        if line:
            content.append(line.decode(charset))
        else:
            src.close()
            break
    return "".join(content)

def get_headers(url):
    """return URL headers"""
    src = connect(url, None)
    return str(src.headers)

def save_to_file(text, outfile, headers):
    """file to write"""
    try:
        file_write = open(outfile, 'w')
    except FileNotFoundError:
        sys.exit("Specified directory does not exists")
    except IsADirectoryError:
        sys.exit("Target path is a directory,include file name")
    except IOError:
        sys.exit("Input/Output error\nMaybe you don't have enough privileges?")
    if headers:
        file_write.write(headers)
    file_write.write(text)
    file_write.close()

if __name__ == "__main__":
    main()
