# coding: utf-8

import os
import os.path

from tornado.options import define, options

try:
    import simplejson as json
except ImportError:
    import json

os.environ['DJANGO_SETTINGS_MODULE'] = 'api_platform.settings'
from api_platform.settings import IP, PORT

define("port", default=PORT, help="run on the given port", type=int)
define("host", default=IP, help="run port on given host", type=str)


def main():
    from django.core.wsgi import get_wsgi_application
    import tornado.wsgi
    wsgi_app = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(wsgi_app)
    setting = {
        'cookie_secret': 'DFksdfsasdfkasdfFKwlwfsdfsa1204mx',
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'debug': False,
    }
    tornado_app = tornado.web.Application(
        [
            (r"/static/(.*)", tornado.web.StaticFileHandler,
             dict(path=os.path.join(os.path.dirname(__file__), "static"))),
            ('.*', tornado.web.FallbackHandler, dict(fallback=container)),
        ], **setting)

    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port, address=IP)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    # tornado.options.parse_command_line()
    # app = Application()
    # server = tornado.httpserver.HTTPServer(app)
    # server.bind(options.port, options.host)
    # #server.listen(options.port)
    # server.start(num_processes=5)
    # tornado.ioloop.IOLoop.instance().start()
    print "Run server on %s:%s" % (options.host, options.port)
    main()
