# **Python Tornado 实现WEB服务器Socket服务器共存并实现交互**

# 1、背景

最近有个项目，需要搭建一个socket服务器，一个web服务器，然后实现两个服务器之间的通讯交互。刚开始的方案是用Python中socket模块实现一个多线程的socket服务器，然后用Flask实现一个web服务器，他们之前通过线程交互实现通讯。
但是在我看来这个方案有例外一个更好的解决方法，就是用Torndao框架。鉴于网上用Tornado实现一个程序同时实现web服务和socket服务器并且实现交互的文章几乎没有，所以记录一下。觉得写得好麻烦点个赞，写得不好请指出，有疑问可以留言。

# 2、准备
## 2.1、环境部署
- **Python3.x**
 - **pip3 install Tornado**
 
## 2.2、目录结构
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200520220321720.png)
目录结构如上图，这个目录结构包括文件命名只是我的个人习惯。其实目录结构不固定，只要合理就行。另外，原本项目是前后分离的只需要实现API接口，所以我这里就没有涉及到HTML的东西。

# 3、服务器的实现
## 3.1、Socket服务器实现
socket服务器部分实现主要靠 Tornado中的TCPServer类
### 3.1.1、 导入类

*socket_server.py:*
```python
from tornado.iostream import IOStream   # 这句可以没有，只是作为参数的代码提示
from tornado.tcpserver import TCPServer
```
### 3.1.2、 构建一个Connecter类 
*socket_server.py:*
```python
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
                # TODO:接收到数据的处理
            except: 
                pass

    def send(self, data):
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
```

### 3.1.3、 构建一个SocketServer类
*socket_server.py:*
```python
class SocketServer(TCPServer):      # 需要继承TCPServer这个类
    async def handle_stream(self, stream: IOStream, address: tuple):   # 实现类里面的handle_stream方法
        await Connecter().init(stream, address)      # 每次有客户端连入都实例化一个Connecter类
```

##  3.2、Web服务器实现
### 3.2.1、 实现一个requestHandler 
*web_test.py:*
```python
from tornado.web import RequestHandler      # 导入RequestHandler类


class TestApiHandler(RequestHandler):       # 继承RequestHandler类

    def get(self):      # 实现GET方法，GET请求会执行这个方法
        pass

    def post(self):     # 实现POST方法，POST请求会执行这个方法
        pass
```

### 3.2.2、 实现web app
 *web_server.py:*
 
```python
from tornado.web import Application         # 导入Tornado的Application类
from .src.web_test import TestApiHandler    # 导入我们自己写的TestApiHandler类


def webServerApp():     # 构造出webApp
    return Application([
        (r'/api_test/', TestApiHandler),    # 把/api_test/路由到TestApiHandler
    ])
```

## 3.3、程序入口
### 3.3.1、 导入web_server和socket_server,还有导入tornado的ioloop

*main.py：*

```python
from web_server.web_server import webServerApp
from socket_server.socket_server import SocketServer
from tornado import ioloop
from tornado.options import define, options
```
### 3.3.2、 定义默认端口
*main.py*
```python
#这里用define定义端口，可以方便使用命令行参数的形式修改端口
define("socketPort", 8888, type=int)    # socket默认使用8888端口
define("webPort", 8080, type=int)       # web默认使用8080端口
```

### 3.3.3、 启动代码
*main.py*
```python
def main():
    socket_server = SocketServer()
    socket_server.listen(options.socketPort, '0.0.0.0')
    print("socket服务器启动，端口：{port}".format(port=options.socketPort))
    app = webServerApp()
    app.listen(options.webPort, '0.0.0.0')
    print("web服务器启动，端口：{port}".format(port=options.webPort))
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
```
# 4、服务器运行效果
到此，一个混合型的socket+web服务器已经搭建好了。我们我们运行main.py文件可以看到打印的信息，socket和web都正常运行。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200521095130786.png)
我在这里简单地写了一个socket客户端测试，代码如下：

```python
import socket
import datetime


class Client:

    def __init__(self):
        with socket.create_connection(("127.0.0.1", 8888)) as sock:
            while True:
                msg = sock.recv(1024)
                if len(msg) > 0:
                    print(msg)
                    sock.send(bytes(str(datetime.datetime.now).encode('utf8')))
                msg = []
                        
                

if __name__ == "__main__":
    Client()
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200521101224553.png)
可以看到tornado异步的形式实现了多客户端同时接入socket。同时也可以测试web接口是正常的，如下图：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200521101807518.png)


# 5、Web服务器与Socket服务器交互
重点来了，web和socket怎样实现交互呢？其实很简单。
## 5.2、 web >> socket
*web_test.py -> TestApiHandler -> post:*

### 5.2.1、 导入Connecter类

```python
from socket_server.socket_server import Connecter
```

### 5.2.2、 实现请求接口发送消息到socket客户端
```python
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
```

### 5.2.3、 效果
请求接口可以返回数据，已经成功发送一个客户端
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200521110952191.png)
客户端也能收到消息：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200521111304831.png)


## 5.1、 socket >> web
其实socket发送的消息让web马上收到消息是不太现实的，但是我们可以把数据保存起来（可以是数据库、全局变量、缓存……），然后通过api接口再把数据取出。另外还有一种方法是通过socket和websocket进行交互通讯，这种方法是推荐的方法，同样的也可以用Tornado去实现，感兴趣可以去研究一下也很简单。如何有需要我提供socket、websocket、web三个端都互相交互的例子可以留言。
这里为了简单一点，我使用一个类作为全局变量来保存数据，然后用接口访问，拿出这个类的值来演示一下效果。
### 5.1.1、 声明类作为全局变量
*socket_data_processing.py*

```python
class SocketData:
    msg = ""
```
### 5.1.2、 接受到的消息保存到这个类里面的msg
*socket_server.py -> Connecter ->  receive*

```python
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
```
### 5.1.3、 用get方法显示socket显示回来的数据
*web_test.py -> TestApiHandler -> get:*

```python
    def get(self):      # 实现GET方法，GET请求会执行这个方法
        from socket_server.src.socket_data_processing import SocketData
        self.write(SocketData.msg)
```

### 5.1.4、 效果
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200521113100395.png)
可以看到，从socket传过来的字符串，被我通过Api读取到了。
<br>
# 6、完整代码
##### GitHub：[https://github.com/JohnDoe1996/socket-web](https://github.com/JohnDoe1996/socket-web)
喜欢的话麻烦在github也点个星，谢谢！



