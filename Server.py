import socket
from _thread import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 400, 400)
        
        self.count = 0
        btn_socket = QPushButton("Socket", self)
        btn_socket.clicked.connect(self.btn_socket_clicked)
        btn_bind = QPushButton("Bind", self)
        btn_bind.clicked.connect(self.btn_bind_clicked)
        btn_listen = QPushButton("Listen", self)
        btn_listen.clicked.connect(self.btn_listen_clicked)
        btn_waiting = QPushButton("Waiting", self)
        btn_waiting.clicked.connect(self.btn_waiting_clicked)

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(btn_socket)
        layout.addWidget(btn_bind)
        layout.addWidget(btn_listen)
        layout.addWidget(btn_waiting)
        layout.addStretch(1)
        self.setLayout(layout)

        self.client_sockets = []

        ## Server IP and Port ##
        self.HOST = "127.0.0.1" # socket.gethostbyname(socket.gethostname())
        self.PORT = 9999

        # 서버 아이콘 표시를 위한 QLabel 위젯 생성
        cloud_pixmap = QPixmap('cloud.png')
        cloud_scaled_pixmap = cloud_pixmap.scaled(50, 50)  # 원하는 크기로 조절
        self.server_label = QLabel(self)
        self.server_label.setPixmap(cloud_scaled_pixmap)
        self.server_label.setGeometry(25, 100, 50, 50)
        # ip/port를 보여줄 텍스트 
        self.serverT_label = QLabel(self)
        self.serverT_label.setText("<b>Server</b>")
        self.serverT_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
        self.serverT_label.setGeometry(25, 125, 50, 50)  # 위치 및 크기 조절
        
        # 소켓 아이콘 표시를 위한 QLabel 위젯 생성
        doorC_pixmap = QPixmap('door_close.png')
        doorC_scaled_pixmap = doorC_pixmap.scaled(50, 50)  # 원하는 크기로 조절
        self.socket_label = QLabel(self)
        self.socket_label.setPixmap(doorC_scaled_pixmap)
        self.socket_label.setGeometry(25, 55, 50, 50)
        self.socket_label.setVisible(False)

        # ip/port를 보여줄 텍스트 
        self.IP_PORT_label = QLabel(self)
    
    def btn_socket_clicked(self):
        if self.count == 0:
            self.count += 1
            print('>> Server Start with ip :', self.HOST)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_label.setVisible(True)  # 초기에는 아이콘 숨김

    def btn_bind_clicked(self):
        if self.count == 1:
            self.count += 1
            self.server_socket.bind((self.HOST, self.PORT))

            combined_text = "<b>IP :" + self.HOST + "<br>Port : "+ str(self.PORT) + "</b>"
            self.IP_PORT_label.setText(combined_text)
            self.IP_PORT_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
            self.IP_PORT_label.setGeometry(10, 20, 100, 30)  # 위치 및 크기 조절
            
    def btn_listen_clicked(self):
        if self.count == 2:
            self.count += 1
            self.server_socket.listen()
    
    def threaded(self, client_socket, addr):
        print('>> Connected by :', addr[0], ':', addr[1])

        ## process until client disconnect ##
        while True:
            try:
                ## send client if data recieved(echo) ##
                data = client_socket.recv(1024)

                if not data:
                    print('>> Disconnected by ' + addr[0], ':', addr[1])
                    break

                print('>> Received from ' + addr[0], ':', addr[1], data.decode())

                ## chat to client connecting client ##
                ## chat to client connecting client except person sending message ##
                for client in self.client_sockets:
                    if client != client_socket:
                        client.send(data)
            
            except ConnectionResetError as e:
                print('>> Disconnected by ' + addr[0], ':', addr[1])
                break
        
        if client_socket in self.client_sockets:
            self.client_sockets.remove(client_socket)
            print('remove client list : ', len(self.client_sockets))

        client_socket.close()

    def btn_waiting_clicked(self):
        if self.count == 3:
            self.count += 1
            try:
                while True:
                    print('>> Wait')

                    client_socket, addr = self.server_socket.accept()
                    self.client_sockets.append(client_socket)
                    start_new_thread(self.threaded, (client_socket, addr))
                    print("참가자 수 : ", len(self.client_sockets))
            except Exception as e:
                print('에러 : ', e)

            finally:
                self.server_socket.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
