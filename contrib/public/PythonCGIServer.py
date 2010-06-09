#!/usr/bin/env python
# run this in the output/ subdirectory to start a simple
# cgi server

from CGIHTTPServer import CGIHTTPRequestHandler
import BaseHTTPServer
import SimpleHTTPServer

CGIHTTPRequestHandler.cgi_directories = ['/services']

def test(HandlerClass = CGIHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    SimpleHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
