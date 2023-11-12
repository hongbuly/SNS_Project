import socket
from _thread import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.setStyleSheet("background-color: white;")
        self.setGeometry(300, 300, 400, 300)
        self.setFixedSize(QSize(400, 300))
        
        self.count = 0
        btn_socket = QPushButton("Socket", self)
        btn_socket.clicked.connect(self.btn_socket_clicked)
        btn_bind = QPushButton("Bind", self)
        btn_bind.clicked.connect(self.btn_bind_clicked)
        btn_listen = QPushButton("Listen", self)
        btn_listen.clicked.connect(self.btn_listen_clicked)
        self.btn_send = QPushButton("Send", self)
        self.btn_send.clicked.connect(self.btn_send_clicked)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_socket)
        hbox.addWidget(btn_bind)
        hbox.addWidget(btn_listen)
        hbox.addWidget(self.btn_send)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(6)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)
        
        self.client_sockets = []

        ## Server IP and Port ##
        self.HOST = "127.0.0.1" # socket.gethostbyname(socket.gethostname())
        self.PORT = 9999

        # 서버 아이콘 표시를 위한 QLabel 위젯 생성
        cloud_pixmap = QPixmap('image/cloud.png')
        cloud_scaled_pixmap = cloud_pixmap.scaled(50, 50)  # 원하는 크기로 조절
        self.server_label = QLabel(self)
        self.server_label.setPixmap(cloud_scaled_pixmap)
        self.server_label.setGeometry(25, 80, 50, 50)
        # Server Text
        self.serverT_label = QLabel(self)
        self.serverT_label.setText("<b>Server</b>")
        self.serverT_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
        self.serverT_label.setGeometry(25, 105, 50, 50)  # 위치 및 크기 조절
        
        # 소켓 아이콘 표시를 위한 QLabel 위젯 생성
        doorC_pixmap = QPixmap('image/door_close.png')
        doorC_scaled_pixmap = doorC_pixmap.scaled(50, 50)  # 원하는 크기로 조절
        self.socketC_label = QLabel(self)
        self.socketC_label.setPixmap(doorC_scaled_pixmap)
        self.socketC_label.setGeometry(25, 35, 50, 50)
        self.socketC_label.setVisible(False)

        doorO_pixmap = QPixmap('image/door_open.png')
        doorO_scaled_pixmap = doorO_pixmap.scaled(50, 50)  # 원하는 크기로 조절
        self.socketO_label = QLabel(self)
        self.socketO_label.setPixmap(doorO_scaled_pixmap)
        self.socketO_label.setGeometry(25, 35, 50, 50)
        self.socketO_label.setVisible(False)

        # ip/port를 보여줄 텍스트 
        self.IP_PORT_label = QLabel(self)

        #Listen 및 waiting을 할 때 나타날 로딩 gif
        self.loading_label = QLabel(self)
        self.loading_label.setGeometry(0, 140, 100, 50)
        self.movie = QMovie("image/loading.gif")
        self.movie.setScaledSize(self.loading_label.size())
        self.loading_label.setMovie(self.movie)
        self.show_gif = False   #초기화면에는 안 보이도록 설정
        self.show_and_hide()    #gif를 보이거나 숨기는 함수
        
        # Client 아이콘 표시를 위한 3개의 QLabel 위젯 생성
        client_pixmap = QPixmap('image/client.png')
        client_scaled_pixmap = client_pixmap.scaled(40, 40)  # 원하는 크기로 조절
        self.client_label1 = QLabel(self)
        self.client_label1.setPixmap(client_scaled_pixmap)
        self.client_label1.setGeometry(300, 30, 40, 40)
        # self.client_label1.setVisible(False)

        self.client_label2 = QLabel(self)
        self.client_label2.setPixmap(client_scaled_pixmap)
        self.client_label2.setGeometry(300, 80, 40, 40)
        # self.client_label2.setVisible(False)

        self.client_label3 = QLabel(self)
        self.client_label3.setPixmap(client_scaled_pixmap)
        self.client_label3.setGeometry(300, 130, 40, 40)
        # self.client_label3.setVisible(False)

        # Client Text 
        self.serverT_label = QLabel(self)
        self.serverT_label.setText("<b>Client</b>")
        self.serverT_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
        self.serverT_label.setGeometry(295, 160, 50, 50)  # 위치 및 크기 조절

        # arrow 아이콘 표시를 위한 3개의 QLabel 위젯 생성
        arrow_pixmap = QPixmap('image/arrow1.png')
        arrow_scaled_pixmap = arrow_pixmap.scaled(560, 30)  # 원하는 크기로 조절
        self.arrow_label1 = QLabel(self)
        self.arrow_label1.setPixmap(arrow_scaled_pixmap)
        self.arrow_label1.setGeometry(80, 90, 200, 30)
        # self.message_label1.setVisible(False)

        arrow2_pixmap = QPixmap('image/arrow2.png')
        arrow2_scaled_pixmap = arrow2_pixmap.scaled(560, 90)  # 원하는 크기로 조절
        self.arrow_label2 = QLabel(self)
        self.arrow_label2.setPixmap(arrow2_scaled_pixmap)
        self.arrow_label2.setGeometry(80, 0, 200, 90)
        # self.message_label1.setVisible(False)

        arrow3_pixmap = QPixmap('image/arrow3.png')
        arrow3_scaled_pixmap = arrow3_pixmap.scaled(560, 90)  # 원하는 크기로 조절
        self.arrow_label3 = QLabel(self)
        self.arrow_label3.setPixmap(arrow3_scaled_pixmap)
        self.arrow_label3.setGeometry(80, 120, 200, 90)
        # self.message_label1.setVisible(False)

        # message 아이콘 표시를 위한 3개의 QLabel 위젯 생성
        message_pixmap = QPixmap('image/msg_g.png')
        message_scaled_pixmap = message_pixmap.scaled(30, 30)  # 원하는 크기로 조절
        self.message_label1 = QLabel(self)
        self.message_label1.setPixmap(message_scaled_pixmap)
        self.message_label1.setGeometry(270, 40, 30, 30)
        # self.message_label1.setVisible(False)

        message_r_pixmap = QPixmap('image/msg_r.png')
        message_r_scaled_pixmap = message_r_pixmap.scaled(30, 30)  # 원하는 크기로 조절
        self.message_label2 = QLabel(self)
        self.message_label2.setPixmap(message_r_scaled_pixmap)
        self.message_label2.setGeometry(270, 90, 30, 30)
        # self.message_label2.setVisible(False)

        message_y_pixmap = QPixmap('image/msg_y.png')
        message_y_scaled_pixmap = message_y_pixmap.scaled(30, 30)  # 원하는 크기로 조절
        self.message_label3 = QLabel(self)
        self.message_label3.setPixmap(message_y_scaled_pixmap)
        self.message_label3.setGeometry(270, 140, 30, 30)
        # self.message_label3.setVisible(False)

        # send 버튼 클릭 시 나타나는 gif
        self.sendLabel = QLabel(self)
        self.sendLabel.setGeometry(160, 140, 100, 100)
        self.sendgif = QMovie('image/send.gif')
        self.sendgif.setScaledSize(self.sendLabel.size())
        self.sendLabel.setMovie(self.sendgif)

        
        self.sendTarget = '' # 메시지 보낼 대상

        self.recvMsg = QLabel(self)
        self.recvMsg.setFixedSize(200, 50)
        self.recvMsg.setGeometry(130, 140, 100, 100)

        # 서버 쪽 message 아이콘
        self.recvLabel = QLabel(self)
        self.recvLabel.setPixmap(message_r_scaled_pixmap)
        self.recvLabel.setGeometry(100, 90, 30, 30)
        self.recvLabel.setVisible(False)
        

    def show_and_hide(self):    #loading gif를 화면에 띄우고 숨기는 함수
        if self.show_gif:
            self.movie.start()
            self.loading_label.setVisible(True)
        else:
            self.movie.stop()
            self.loading_label.setVisible(False)

    def btn_socket_clicked(self):
        if self.count == 0:
            self.count += 1
            print('>> Server Start with ip :', self.HOST)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socketC_label.setVisible(True)

    def btn_bind_clicked(self):
        if self.count == 1:
            self.count += 1
            self.server_socket.bind((self.HOST, self.PORT))

            combined_text = "<b>IP :" + self.HOST + "<br>Port : "+ str(self.PORT) + "</b>"
            self.IP_PORT_label.setText(combined_text)
            self.IP_PORT_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
            self.IP_PORT_label.setGeometry(10, 0, 100, 30)  # 위치 및 크기 조절
            
    def btn_listen_clicked(self):
        if self.count == 2:
            self.count += 1
            self.server_socket.listen()
            self.socketC_label.setVisible(False)    #문 애니메이션을 위해 door_close는 숨기기
            self.socketO_label.setVisible(True)     #문 애니메이션을 위해 door_open는 보이기
            self.show_gif = True
            self.show_and_hide()    #loading gif 화면에 보이기
            start_new_thread(self.btn_waiting_clicked,())   #waiting동안 동시에 loading gif를 보여야 하므로 thread로 분리
    

    def btn_send_clicked(self):
        self.recvLabel.setVisible(False) # 서버(보내는 사람)쪽 아이콘 안보임
        self.message_label2.setVisible(True) # 클라이언트(받는 사람)쪽 아이콘 보임
        
        # send 버튼 짧은 주기로 여러 번 누르는 것 방지. 3초동안 버튼 비활성화
        self.btn_send.setEnabled(False)
        QTimer.singleShot(3000, lambda: self.btn_send.setDisabled(False))

        # 클라이언트에게 데이터 보내기
        temp_str = "server"
        send_data = bytearray(temp_str, 'utf-8')
        try:
            self.sendTarget.send(send_data)
            # 편지가 지나가는 gif 실행
            self.sendgif.start()
            QTimer.singleShot(2000, lambda: self.sendLabel.setDisabled(False))
            QTimer.singleShot(2000, lambda: self.sendgif.stop())
        except:
            print("메시지를 전달할 대상이 없습니다.")
    

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
                self.recvMsg.setText('[받은 메시지]: ' + data.decode())
                self.recvLabel.setVisible(True)
                self.message_label2.setVisible(False)

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
                    self.sendTarget = client_socket
                    print("참가자 수 : ", len(self.client_sockets))
                    start_new_thread(self.threaded, (client_socket, addr))
                    
                    #최대 3개의 Client만 접속 가능
                    while len(self.client_sockets) == 3:
                        self.show_gif = False   #최대 3개가 연결되면 listen 중지를 표현하기위해
                        self.show_and_hide()    #loading gif 숨기기
                        self.socketC_label.setVisible(True)    #문 애니메이션을 위해 door_close는 보이기
                        self.socketO_label.setVisible(False)     #문 애니메이션을 위해 door_open는 숨기기
                        pass
            except Exception as e:
                print('에러 : ', e)

            finally:
                self.server_socket.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
