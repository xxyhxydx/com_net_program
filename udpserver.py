import random
import socket
import threading
from datetime import datetime

limit_data = 1024  #最大接收数据量


def pack(seq_no, var, send_text):
    udp_server_header = bytearray(150)  # 设定位数
    # 分组号 [0,8)
    udp_server_header[0:(0 + len(seq_no))] = seq_no
    # 版本号 [8,10)
    var = var.encode()
    udp_server_header[8:(8 + len(var))] = var
    # 系统时间 [10,20)
    now = datetime.now()
    send_time = now.strftime('%H:%M:%S').encode()
    udp_server_header[10:(10 + len(send_time))] = send_time
    # 文本[20,40)
    send_text = send_text.encode()
    if len(send_text) > 100:
        text_len = 100
    else:
        text_len = len(send_text)
    udp_server_header[20:(20 + text_len)] = send_text[0:text_len]
    return udp_server_header


def receive_udp(ip,port,packet_loss_rate):
    serverAddr = (ip, port)
    # AF_INET指示底层网络使用IPv4，SOCK_DGRAM指示UDP
    udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建socket对象，走udp通道
    udpServer.bind(serverAddr)  # 绑定服务端地址


    #通信
    while True:
        clientData, clientAddr = udpServer.recvfrom(limit_data)  # 接收来自客户端的数据
        # 模拟TCP连接的建立（3次握手）与释放（4次挥手）
        # 接受FIN包
        if clientData == b'FIN':
            print(clientAddr, "bye!")
            # 发送ACK包
            ack = b'ACK'
            udpServer.sendto(ack, clientAddr)
            # 发送FIN-ACK包
            fin_ack = b'FIN-ACK'
            udpServer.sendto(fin_ack, clientAddr)
            continue
        # 接收SYN包
        if clientData == b'SYN':
            print(clientAddr, "hello!")
            # 发送SYN-ACK包
            syn_packet = b'SYN-ACK'
            udpServer.sendto(syn_packet, clientAddr)
            continue
        # 接收ACK包
        if clientData == b'ACK':
            continue
        i =random.random()  # 设置丢包
        print(clientData.decode('utf-8'), clientAddr)
        msg = pack(clientData[0:8], "2", "已接收信息！")
        if packet_loss_rate <= i :
            udpServer.sendto(msg, clientAddr)  # 发送数据给客户端


if __name__ == "__main__":
    ip=""
    port = 12327
    # 创建线程监控服务器
    while True:
        packet_loss_rate=float(input("请输入丢包率[0.0-1.0)："))
        if 0.0<=packet_loss_rate<1.0:
            break
    thread0 = threading.Thread(target=receive_udp, args=(ip,port,packet_loss_rate))
    thread0.setDaemon = True
    thread0.start()
