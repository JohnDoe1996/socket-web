from web_server.web_server import webServerApp
from socket_server.socket_server import SocketServer
from tornado import ioloop
from tornado.options import define, options


#这里用define定义端口，可以方便使用命令行参数的形式修改端口
define("socketPort", 8888, type=int)    # socket默认使用8888端口
define("webPort", 8080, type=int)       # web默认使用8080端口


def main():
    socket_server = SocketServer()
    socket_server.listen(options.socketPort, '0.0.0.0')
    print("socket服务器启动，端口：{port}".format(port=options.socketPort))
    app = webServerApp()
    app.listen(options.webPort, '0.0.0.0')
    print("web服务器启动，端口：{port}".format(port=options.webPort))
    try:    # 此处修复不能使用一次Ctrl+C结束程序
        print("按 Ctrl+C 可结束程序!")
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:   
        ioloop.IOLoop.current().stop()
        print("程序已经结束!")


if __name__ == '__main__':
    main()