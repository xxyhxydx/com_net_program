import datetime
import socket
import time
import statistics

limit_text = 100  # 文本最大长度，不超过900
limit_data = 1024  #最大接受数据量
limit_socket_time = 0.1  #设置套接字超时值100ms
udp_request_packet = 12  #request报文


# udp报文封装
def pack(seq_no, var, send_text):
    udp_client_header = bytearray(limit_text + 50)  # 设定位数
    # 分组号 [0,8)
    seq_no = str(seq_no).encode()
    udp_client_header[0:(0 + len(seq_no))] = seq_no
    # 版本号 [8,10)
    var = var.encode()
    udp_client_header[8:(8 + len(var))] = var
    # 文本[10,limit_text+10)
    send_text = send_text.encode()
    if len(send_text) > limit_text:
        text_len = limit_text
    else:
        text_len = len(send_text)
    udp_client_header[10:(10 + text_len)] = send_text[0:text_len]
    return udp_client_header


# 模拟TCP连接的建立（3次握手）
def tcp_connect(dest_addr):
    try:
        # 发送SYN包
        syn_packet = b'SYN'
        udpClient.sendto(syn_packet, dest_addr)
        # 接收SYN-ACK包
        syn_ack,addr= udpClient.recvfrom(1024)
        if syn_ack == b'SYN-ACK':
            print(dest_addr,"server is ready!")
            # 发送ACK包
        ack_packet = b'ACK'
        udpClient.sendto(ack_packet, dest_addr)
    except:
        print("connect refused error!")
        exit(0)



# 模拟TCP连接的释放
def tcp_disconnect(dest_addr):
    # 发送FIN包
    fin_packet = b'FIN'
    udpClient.sendto(fin_packet, dest_addr)
    # 接收ACK包
    ack,addr = udpClient.recvfrom(1024)
    if ack == b'ACK':
        print(dest_addr,"bye!")
    # 接收FIN-ACK包
    fin_ack,addr= udpClient.recvfrom(1024)
    if fin_ack == b'FIN-ACK':
        # 发送ACK包
        fin_packet = b'ACK'
        udpClient.sendto(fin_packet, dest_addr)


# 创建UDP套接字
udpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 绑定IP和Port
serverIP = input("请输入指定服务器IP：")
serverPort = int(input("请输入指定服务器Port："))
serverAddr = (serverIP, serverPort)
udpClient.settimeout(limit_socket_time)  #设置超时

# 模拟TCP连接的建立
tcp_connect(serverAddr)

#通信
success_udp_packets = 0
sum_udp_packets = 0
rtt_list = []
server_time_list = []
for i in range(udp_request_packet):
    i += 1  #分组号
    text=''
    while True:
        text = input("输入你想发送的信息：")
        if len(text)<limit_text: break
        else: print("文本超出限制！")
    data = pack(i, "2", text)  # 报文数据，bytes类型
    again = 0  #超时重传机会计数
    while again < 3:
        try:
            sendTime = time.time()
            sum_udp_packets += 1
            udpClient.sendto(data, serverAddr)  # 发送数据给服务端
            serverData, serverAddr = udpClient.recvfrom(limit_data)  # 接收来自服务端的数据
            server_time_list.append(serverData[10:18].decode('utf-8'))
            success_udp_packets += 1
            rtt = time.time() - sendTime
            rtt_list.append(rtt)
            print("seq_no：", data[0:8].decode('utf_8'), " rtt：", rtt)
            print("serverIP：", serverAddr[0], " serverPort：", serverAddr[1])
            again = 3
        except socket.timeout:
            print("seq_no：", data[0:8].decode('utf_8'), " request time out.")
            again += 1

# 通信反馈
print("receive udp packets：", success_udp_packets)
print("packet loss rate：", 1 - (success_udp_packets / sum_udp_packets))
print("max rtt：", max(rtt_list), "min rtt：", min(rtt_list), "mean rtt：", sum(rtt_list) / len(rtt_list), "stdev rtt：",
      statistics.stdev(rtt_list))
t1 = datetime.datetime.strptime(server_time_list[4], '%H:%M:%S')
t2 = datetime.datetime.strptime(server_time_list[0], '%H:%M:%S')
print("server overall responsiveness：", t1 - t2)
# 模拟TCP连接的释放
tcp_disconnect(serverAddr)

#关闭套接字
udpClient.close()
