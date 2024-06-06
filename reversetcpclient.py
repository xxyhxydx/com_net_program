import socket
import random

limit_data = 1024  #最大接受数据量
limit_socket_time = 0.1  #设置套接字超时值1000ms
udp_request_packet = 5  #request报文


# tcp报文封装
def pack(type, length, send_text):
    tcp_client_header = bytearray()  # 设定位数
    if type == "1":
        # 类型 [0,8)
        type = type.encode()
        header_type = bytearray(8)
        header_type[0:(0 + len(type))] = type
        tcp_client_header.extend(header_type)
        # 长度 [8,20)
        header_length = bytearray(12)
        length = str(length).encode()
        header_length[0:(0 + len(length))] = length
        tcp_client_header.extend(header_length)
        return tcp_client_header
    else:
        # 类型 [0,8)
        type = type.encode()
        header_type = bytearray(8)
        header_type[0:(0 + len(type))] = type
        tcp_client_header.extend(header_type)
        # 长度 [8,20)
        header_length = bytearray(12)
        length = str(length).encode()
        header_length[0:(0 + len(length))] = length
        tcp_client_header.extend(header_length)
        # 文本[20,20+length)
        tcp_client_header.extend(send_text)
        return tcp_client_header


def read_and_split_text():
    with open("dream.txt", 'r', encoding='utf-8') as file:
        text = file.read()
    paragraphs = text.replace('\n', '')
    return paragraphs


# 创建TCP套接字
tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定IP和Port
serverIP = input("请输入指定服务器IP：")
serverPort = int(input("请输入指定服务器Port："))
serverAddr = (serverIP, serverPort)
try:
    tcpClient.connect(serverAddr)
    tcpClient.settimeout(limit_socket_time)  #设置超时
except:
    print("connect refused error!")
    exit(0)

# 文本分块
while True:
    up_text = int(input("块最大位（文本总共1364位，但为了不丢失数据尽量最不能超过1000位）："))
    down_text = int(input("块最小位："))
    if down_text <= up_text <= 1000:
        break
    else:
        print("error!")

p = read_and_split_text()
p_length_sum = len(p)
p_length_list = []  # 每块length
N = 0  #块数
while (True):
    N += 1
    random_num = random.randint(down_text, up_text)
    if p_length_sum > random_num:
        p_length_sum -= random_num
        p_length_list.append(random_num)
    else:
        p_length_list.append(p_length_sum)
        break

#通信
tcpClient.send(pack("1", N, ''))  # 发送数据给服务端
serverData = tcpClient.recv(limit_data)  # 接收来自服务端的数据
low = 0
high = 0
for i in range(N):
    high += p_length_list[i]
    text = p[low:high].encode()
    low += p_length_list[i]
    data = pack("3", p_length_list[i], text)  # 报文数据，bytes类型
    try:
        tcpClient.send(data)  # 发送数据给服务端
        serverData = tcpClient.recv(limit_data)  # 接收来自服务端的数据
        show_data = serverData[20:].decode('utf-8')
        print("第{0}块：{1}".format(i + 1, show_data))
    except socket.timeout:
        print(f" {i + 1}： request time out.")

#关闭套接字
tcpClient.close()
