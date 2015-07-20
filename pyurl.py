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
    parser = argparse.ArgumentParser() #setting possible arguments
    parser.add_argument('-o', metavar='output_file', help=_('Write output to file'))
    parser.add_argument('-i', action='store_true', help=_('Include request headers'))
    parser.add_argument('url', help=_('Define target URL'))
    parser.add_argument('-d', metavar='DATA', help=_('Http POST data between quotation marks'))
    parser.add_argument('-c', action='store_true', help=_('Show Http code'))
    parser.add_argument('-a', metavar='user_agent', help=_('Set custom user agent'))
    parser.add_argument('-k', action='store_true', help=_('headers only'))
    check_args_and_exec(parser.parse_args())

def language_set():
    """read from UNIX or windows locale informations and set language"""
    ita = gettext.translation('pyurl', localedir='locale', languages=['it'])
    eng = gettext.translation('pyurl', localedir='locale', languages=['en'])
    if locale.getlocale()[0] == 'it_IT' or locale.getlocale()[0] == 'ita':
        ita.install()
    else:
        eng.install()

def check_args_and_exec(args):
    """arguments control and functions invoke"""
    headers = ""
    post_data = None
    url = str(args.url)
    if args.d is not None:
        post_data = data_post_format(args.d)
    if not re.match("http://", url):
        url = "http://" + url
    text = get_source(url, post_data, args.c, args.a)
    if args.i or args.k:
        if args.i and not args.k:
            args.c = None
        headers = get_headers(url, args.a, args.c)
    if args.k is True:
        text = ""
    if args.o is not None:
        save_to_file(text, args.o, headers)
    else:
        if headers:
            print(headers)
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

def get_headers(url, user_agent, http_code):
    """return URL headers"""
    src = connect(url, None, user_agent)
    if http_code:
        return (_("Http code: %d\n\n ") % src.getcode()) + str(src.headers)
    else:
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
