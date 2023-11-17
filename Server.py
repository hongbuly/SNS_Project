import socket
from _thread import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

bubble_margins = QMargins(15, 5, 35, 5)
msg_margins = QMargins(20, 15, 20, 15)
b_margins = bubble_margins * 2

me_color = QColor("#BCE55C") # 나의 말풍선 색
other_color = QColor("#D5D5D5") # 상대방의 말풍선 색

class make_bubble(QStyledItemDelegate):    
    def paint(self, painter, option, index):
        sender, msg = index.model().data(index, Qt.DisplayRole)

        bubble_rect = option.rect.marginsRemoved(bubble_margins)
        b_rect = option.rect.marginsRemoved(b_margins)

        color = 0
        point = 0
        if sender == 'me':
            color = me_color
            point = bubble_rect.topRight()
        else:
            color = other_color
            point = bubble_rect.topLeft()
        
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawRoundedRect(bubble_rect, 2, 2)


        painter.drawPolygon(point + QPoint(-20, 0), point + QPoint(20, 0), point + QPoint(0, 20))
        
        painter.setPen(Qt.black)

        painter.drawText(b_rect, Qt.TextWordWrap, msg)

    def sizeHint(self, option, index):
        _, msg = index.model().data(index, Qt.DisplayRole)
        metrics = QApplication.fontMetrics()
        rect = option.rect.marginsRemoved(msg_margins)
        rect = metrics.boundingRect(rect, Qt.TextWordWrap, msg)
        rect = rect.marginsAdded(msg_margins)
        return rect.size()
    
class msg_model(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(msg_model, self).__init__(*args, **kwargs)
        self.messages = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.messages[index.row()]
        
    def rowCount(self, index):
        return len(self.messages)
    
    def add_msg(self, sender, msg):
        if msg:
            self.messages.append((sender, msg))
            self.layoutChanged.emit()


class MyWindow(QWidget):
    # PyQt 신호를 만들어 메시지를 수신할 때 신호를 발생
    message_received = pyqtSignal()
    update_chat = pyqtSignal() # 채팅방 갱신 신호
    
    def __init__(self):
        super().__init__()
        
        self.setGeometry(300, 300, 800, 300)
        self.setFixedSize(QSize(800, 300))
        
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

        self.message_display = QListView(self)
        self.message_display.setItemDelegate(make_bubble())

        self.msgModel = msg_model()
        self.message_display.setModel(self.msgModel)

        # 입력란
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("메시지 입력")
        self.input_box.returnPressed.connect(self.btn_send_clicked)  # Enter 키로도 메시지 전송 가능
        

        vbox = QVBoxLayout()
        vbox.addStretch(6)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.message_display)
        vbox2.addWidget(self.input_box)

        hbox2 = QHBoxLayout()
        hbox2.addLayout(vbox)
        hbox2.addLayout(vbox2)
        self.setLayout(hbox2)
        
        self.client_sockets = []

        ## Server IP and Port ##
        self.HOST = "127.0.0.1" # socket.gethostbyname(socket.gethostname())
        self.PORT = 9999

        # 서버 아이콘 표시를 위한 QLabel 위젯 생성
        cloud_pixmap = QPixmap('Images/cloud.png')
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
        doorC_pixmap = QPixmap('Images/door_close.png')
        doorC_scaled_pixmap = doorC_pixmap.scaled(50, 50)  # 원하는 크기로 조절
        self.socketC_label = QLabel(self)
        self.socketC_label.setPixmap(doorC_scaled_pixmap)
        self.socketC_label.setGeometry(25, 35, 50, 50)
        self.socketC_label.setVisible(False)

        doorO_pixmap = QPixmap('Images/door_open.png')
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
        self.movie = QMovie("Images/loading.gif")
        self.movie.setScaledSize(self.loading_label.size())
        self.loading_label.setMovie(self.movie)
        self.show_gif = False   #초기화면에는 안 보이도록 설정
        self.show_and_hide()    #gif를 보이거나 숨기는 함수
        
        # Client 아이콘 표시를 위한 QLabel 위젯 생성
        client_pixmap = QPixmap('Images/client.png')
        client_scaled_pixmap = client_pixmap.scaled(40, 40)  # 원하는 크기로 조절
        self.client_label = QLabel(self)
        self.client_label.setPixmap(client_scaled_pixmap)
        self.client_label.setGeometry(300, 80, 40, 40)
        self.client_label.setVisible(False)

        # Client Text 
        self.serverT_label = QLabel(self)
        self.serverT_label.setText("<b>Client</b>")
        self.serverT_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
        self.serverT_label.setGeometry(295, 105, 50, 50)  # 위치 및 크기 조절

        # arrow 아이콘 표시를 위한 QLabel 위젯 생성
        arrow_pixmap = QPixmap('Images/arrow1.png')
        arrow_scaled_pixmap = arrow_pixmap.scaled(200, 30)  # 원하는 크기로 조절
        self.arrow_label = QLabel(self)
        self.arrow_label.setPixmap(arrow_scaled_pixmap)
        self.arrow_label.setGeometry(80, 90, 200, 30)
        self.arrow_label.setVisible(False)

        # arrow 아이콘 표시를 위한 QLabel 위젯 생성
        arrow2_pixmap = QPixmap('Images/arrow2.png')
        arrow2_scaled_pixmap = arrow2_pixmap.scaled(200, 30)  # 원하는 크기로 조절
        self.arrow2_label = QLabel(self)
        self.arrow2_label.setPixmap(arrow2_scaled_pixmap)
        self.arrow2_label.setGeometry(80, 90, 200, 30)
        self.arrow2_label.setVisible(False)

        # message 아이콘 표시를 위한 QLabel 위젯 생성
        message_r_pixmap = QPixmap('Images/msg_r.png')
        message_r_scaled_pixmap = message_r_pixmap.scaled(30, 30)  # 원하는 크기로 조절
        self.message_label = QLabel(self)
        self.message_label.setPixmap(message_r_scaled_pixmap)
        self.message_label.setGeometry(270, 90, 30, 30)
        self.message_label.setVisible(False)

        # message가 오는 에니메이션
        self.message_anim2 = QPropertyAnimation(self.message_label, b"pos")
        self.message_anim2.setStartValue(QPoint(70, 90))
        self.message_anim2.setEndValue(QPoint(270, 90))
        self.message_anim2.setDuration(1500)

        self.sendTarget = '' # 메시지 보낼 대상

        # 서버 쪽 message 아이콘
        self.recvLabel = QLabel(self)
        self.recvLabel.setPixmap(message_r_scaled_pixmap)
        self.recvLabel.setGeometry(100, 90, 30, 30)
        self.recvLabel.setVisible(False)

        self.message_temp = False
        self.nonstop = True

        #신호를 받을 경우 해당 함수로 연결
        self.message_received.connect(self.update_message_anim)
        self.update_chat.connect(self.update_chat_room)

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
        # send 버튼 짧은 주기로 여러 번 누르는 것 방지. 3초동안 버튼 비활성화
        self.btn_send.setEnabled(False)
        QTimer.singleShot(3000, lambda: self.btn_send.setDisabled(False))

        # 클라이언트에게 데이터 보내기
        temp_str = self.input_box.text()
        send_data = bytearray(temp_str, 'utf-8')
        try:
            self.input_box.clear()
            self.sendTarget.send(send_data)

            self.arrow_label.setVisible(False)
            self.arrow2_label.setVisible(True)
            self.message_label.setVisible(True)
            self.message_anim2.start()

            # self.message_display.append("나: " + temp_str)
            self.msgModel.add_msg('me', "나: " + temp_str)
            self.message_display.scrollToBottom()
        except:
            print("메시지를 전달할 대상이 없습니다.")

    def hide_client(self):
        self.client_label.setVisible(False)
        self.arrow_label.setVisible(False)
        self.message_label.setVisible(False)

    def update_message_anim(self):
        # 수신된 메시지로 UI를 업데이트하는 슬롯 함수
        self.arrow2_label.setVisible(False)
        self.arrow_label.setVisible(True)
        self.message_label.setVisible(True)
        # message 이동 에니메이션
        self.message_anim = QPropertyAnimation(self.message_label, b"pos")
        self.message_anim.setStartValue(QPoint(270, 90))
        self.message_anim.setEndValue(QPoint(70, 90))
        self.message_anim.setDuration(1500)
        
        self.message_anim.start()

    def update_chat_room(self):
        self.msgModel.layoutChanged.emit()
        self.message_display.scrollToBottom()
        
    def threaded(self, client_socket, addr):
        print('>> Connected by :', addr[0], ':', addr[1])
        ## process until client disconnect ##
        while True:
            try:
                ## send client if data recieved(echo) ##
                data = client_socket.recv(1024)

                if not data:
                    print('>> Disconnected by ' + addr[0], ':', addr[1])
                    self.hide_client()
                    self.nonstop = False
                    break

                print('>> Received from ' + addr[0], ':', addr[1], data.decode())
                self.msgModel.add_msg('other', "상대방: " + data.decode())

                # 단계 3: UI를 업데이트하기 위해 신호를 발생시킵니다.
                self.message_received.emit()
                self.update_chat.emit()
            
                ## chat to client connecting client ##
                ## chat to client connecting client except person sending message ##
                for client in self.client_sockets:
                    if client != client_socket:
                        client.send(data)
            
            except ConnectionResetError as e:
                print('>> Disconnected by ' + addr[0], ':', addr[1])
                self.hide_client()
                self.nonstop = False
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
                    
                    self.show_gif = False   #1개가 연결되면 listen 중지를 표현하기위해
                    self.show_and_hide()    #loading gif 숨기기
                    self.socketC_label.setVisible(True)    #문 애니메이션을 위해 door_close는 보이기
                    self.socketO_label.setVisible(False)     #문 애니메이션을 위해 door_open는 숨기기

                    self.client_label.setVisible(True)
                    self.threaded(client_socket, addr)
                    
            except Exception as e:
                print('에러 : ', e)

            finally:
                self.server_socket.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
