#!/usr/bin/env python

class Service:
    def buses(self, msg):
        print "MSG:", msg
        return "Bus_1"


if __name__ == '__main__':
    # this is if JSONService.py is run as a CGI
    from jsonrpc.cgihandler import handleCGIRequest
    handleCGIRequest(Service())
else:
    # this is if JSONService.py is run from mod_python:
    # rename .htaccess.mod_python to .htaccess to activate,
    # and restart Apache2
    from jsonrpc.apacheServiceHandler import handler
