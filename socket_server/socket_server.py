from tornado.iostream import IOStream, StreamClosedError       # IOStream可以没有，只是作为参数的代码提示
from tornado.tcpserver import TCPServer
import traceback

class Connecter:

    clients = set()     # 存放连接的客户端

    async def init(self, stream: IOStream, address: tuple):
        """
        注意这个不是构造方法，这里不用构造方法是为了方便后续的与web端相互通信
        :param stream:      socket的数据流的通道
        :param address:     客户端的 ip 和 id  (ip, id)
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
        # while True:       # while True 是没有错的，但是感觉不够严谨
        while not self.stream.closed():  # 此处改为IOStream没有关闭就继续循环
            try:    
                data = await self.stream.read_bytes(num_bytes=1024, partial=True)   # num_bytes:每次最多接收字节，partial:数据中断后视为接收完成
                print(data)
                from .src.socket_data_processing import SocketData
                SocketData.msg = data.decode('utf8')
            except StreamClosedError as e:  # 因为异步的原因。可能设备离线后还在接收消息。
                pass
                # print(e)
            except:
                traceback.print_exc()  # 把其他错误打印出来

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