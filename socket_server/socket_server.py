from tornado.iostream import IOStream       # 这句可以没有，只是作为参数的代码提示
from tornado.tcpserver import TCPServer

class Connecter:

    clients = set()     # 存放连接的客户端

    async def init(self, stream: IOStream, address: tuple):
        """
        注意这个不是构造方法，这里不用构造方法是为了方便后续的与web端相互通信
        """
        self.stream, self.address = stream, address
        self.clients.add(self)
        print("{address} 上线!".format(address=address))
        self.stream.set_close_callback(self.onClose)  # 客户端离线的时候会被调用
        await self.receive()        # 接受消息

    async def receive(self):
        """
        接受消息
        """
        while True:
            try:    # 因为异步的原因。可能设备离线后还在接收消息，所以try一下，不让错误打印出来，其实打印了错误也不影响程序运行
                data = await self.stream.read_bytes(num_bytes=1024, partial=True)   # num_bytes:每次最多接收字节，partial:数据中断后视为接收完成
                print(data)
                from .src.socket_data_processing import SocketData
                SocketData.msg = data.decode('utf8')
            except:
                pass

    def send(self, data:str):
        """
        发送消息
        :param data: 消息内容
        """
        self.stream.write(bytes(data.encode('utf8')))

    def onClose(self):
        """
        客户端离线
        """
        print("{address} 离线!".format(address=self.address))
        self.clients.remove(self)  # 在clients内删掉该客户端



class SocketServer(TCPServer):      # 需要继承TCPServer这个类
    async def handle_stream(self, stream: IOStream, address: tuple):   # 实现类里面的handle_stream方法
        await Connecter().init(stream, address)      # 每次有客户端连入都实例化一个Connecter类