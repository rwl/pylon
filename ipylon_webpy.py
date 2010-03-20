import web
import json
#from django.utils import simplejson
import pylon
urls = ('/json', 'IPylonHandler')
app = web.application(urls, globals())

class IPylonHandler:
    def __init__(self):
        self.case = pylon.Case.load("./pylon/test/data/bench30.raw")


    def json_buses(self, args):
        print "ARGS:", args
        return [[getattr(bus, args[0]) for bus in self.case.buses]]


    def POST(self):
#        args = simplejson.loads(web.data())
        args = json.read(web.data())
        json_func = getattr(self, 'json_%s' % args[u"method"])
        json_params = args[u"params"]
#        json_method_id = args[u"id"]
        result = json_func(json_params)
        # reuse args to send result back
        args.pop(u"method")
        args["result"] = result[0]
        args["error"] = None # IMPORTANT!!
        web.header("Content-Type","text/html; charset=utf-8")
        return json.write(args)
#        return simplejson.dumps(args)

if __name__ == "__main__":
    app.run()
