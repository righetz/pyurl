#!/usr/bin/python3
"""Simple CUrl porting for Python3
"""

import urllib.request, re
import sys
import argparse

def main():
    """"main method"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', metavar='outfile', help='Write output to file')
    parser.add_argument('-i', action='store_true', help='Show request headers')
    parser.add_argument('url', help='Define target URL')
    control(parser.parse_args())

def control(args):
    """arguments control and methods invoke"""
    headers = ""
    url = str(args.url)
    if not re.match("http://", url):
        url = "http://" + url
    text = get_file(url)
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

def connect(url):
    """connection method"""
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={"User-Agent" : "PyUrl V1.0"
                    }
            )
        src = urllib.request.urlopen(req)
    except urllib.error.URLError:
        sys.exit("Could not resolve host %s\nCheck connection issues or format URL properly" % url)
    return src

def get_file(url):
    """print to stdout"""
    src = connect(url)
    charset = src.headers.get_param('charset')
    content = []
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
    src = connect(url)
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
