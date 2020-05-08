from socketserver import TCPServer, StreamRequestHandler
import time

ADDR = ('', 502)
BUFSIZ = 1024

# 创建 StreamRequestHandler 类的子类
class MyRequestHandler(StreamRequestHandler):
    # 重写 handle 方法，该方法在父类中什么都不做
    # 当客户端主动连接服务器成功后，自动运行此方法
    def handle(self):
        # client_address 属性的值为客户端的主机端口元组
        print('... connected from {}'.format(self.client_address))
        # request.recv 方法接收客户端发来的消息
        data = self.request.recv(BUFSIZ)
        print('... connected msg {}'.format(data))

        # request.sendall 方法发送消息给客户端
        self.request.sendall('[{}] {}'.format(
            time.ctime(), data.decode()).encode())


def main():
    # 创建 TCP 服务器并启动，该服务器为单线程设计，不可同时为两个客户端收发消息
    # 该服务器每次连接客户端成功后，运行一次 handle 方法然后断开连接
    # 也就是说，每次客户端的请求就是一次收发消息
    # 连续请求需要客户端套接字不断重新创建
    tcp_server = TCPServer(ADDR, MyRequestHandler)
    print('等待客户端连接...')
    try:
        tcp_server.serve_forever()  # 服务器永远等待客户端的连接
    except KeyboardInterrupt:
        tcp_server.server_close()   # 关闭服务器套接字
        print('\nClose')
        exit()


if __name__ == '__main__':
    main()