import socket
import threading

limit_data = 1024  # 最大接收数据量


def pack(type, length, send_text):
    tcp_server_header = bytearray()  # 设定位数
    if type == "2":
        # 类型 [0,8)
        type = type.encode()
        header_type = bytearray(8)
        header_type[0:(0 + len(type))] = type
        tcp_server_header.extend(header_type)
        return tcp_server_header
    else:
        # 类型 [0,8)
        type = type.encode()
        header_type = bytearray(8)
        header_type[0:(0 + len(type))] = type
        tcp_server_header.extend(header_type)
        # 长度 [8,20)
        header_length = bytearray(12)
        length = str(length).encode()
        header_length[0:(0 + len(length))] = length
        tcp_server_header.extend(header_length)
        # 文本[20,20+length)
        tcp_server_header.extend(send_text)
        return tcp_server_header


def discuss(tcp_socket, tcp_addr):
    print(tcp_addr, "hello!")
    initialization = tcp_socket.recv(limit_data)
    N = int(initialization[8:20].decode('utf-8').replace('\x00', ''))
    tcp_socket.send(pack("2", '', ''))
    while (N):
        N -= 1
        data = tcp_socket.recv(limit_data)
        if not data[8:20]:
            break
        length = int(data[8:20].decode('utf-8').replace("\x00", ''))
        reverse_data = ''.join(reversed(data[20:20 + length].decode('utf-8')))
        tcp_socket.send(pack("3", length, reverse_data.encode()))

    tcp_socket.close()
    print(tcp_addr, "bye!")


if __name__ == "__main__":
    # 绑定IP和Port
    serverIP = ""
    serverPort = 12323
    serverAddr = (serverIP, serverPort)
    # TCP
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServer.bind(serverAddr)  # 绑定服务端地址
    tcpServer.listen(5)  # 设置socket最多监听个数
    while True:
        connSock, addr = tcpServer.accept()
        thread = threading.Thread(target=discuss, args=(connSock, addr))
        thread.setDaemon = True
        thread.start()
