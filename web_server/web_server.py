from tornado.web import Application         # 导入Tornado的Application类
from .src.web_test import TestApiHandler    # 导入我们自己写的TestApiHandler类


def webServerApp():     # 构造出webApp
    return Application([
        (r'/api_test/', TestApiHandler),    # 把/api_test/路由到TestApiHandler
    ])