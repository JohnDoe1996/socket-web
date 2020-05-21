from tornado.web import RequestHandler      # 导入RequestHandler类
from socket_server.socket_server import Connecter

class TestApiHandler(RequestHandler):       # 继承RequestHandler类

    def get(self):      # 实现GET方法，GET请求会执行这个方法
        from socket_server.src.socket_data_processing import SocketData
        self.write(SocketData.msg)

    def post(self):     # 实现POST方法，POST请求会执行这个方法
        msg = self.get_argument("msg")  # 得到post请求中的msg的值
        ip = self.get_argument('ip')    # 得到要发送的ip
        c = Connecter()     # 实例化Connecter类
        counter = 0     # 记录发送到客户端的个数
        for client in c.clients:    # type:Connecter
            if client.address[0] == ip:     # 根据ip发送
                client.send(msg)    # 发送消息
                counter += 1        # 计数加1
        self.write("{'send_counter':" + str(counter) + "}")