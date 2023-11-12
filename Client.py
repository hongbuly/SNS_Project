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

        self.HOST = '127.0.0.1'
        self.PORT = 9999

        # 서버 접속 정보
        infobox = QHBoxLayout()
        gb = QGroupBox()
        infobox.addWidget(gb)
 
        box = QHBoxLayout()
        label = QLabel('IP : '+ self.HOST)
        box.addWidget(label)
        label = QLabel('Port : '+ str(self.PORT))
        box.addWidget(label)
        
        gb.setLayout(box)      
        
        # 메시지 출력란
        self.message_display = QTextEdit(self)
        self.message_display.setReadOnly(True)
        
        # 입력란
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("메시지 입력")
        self.input_box.returnPressed.connect(self.send_message)  # Enter 키로도 메시지 전송 가능

        # 전송 버튼
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        # 수직 레이아웃
        vbox = QVBoxLayout()
        vbox.addLayout(infobox)
        vbox.addWidget(self.message_display)
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(self.input_box)
        hbox.addWidget(self.send_button)
        self.setLayout(vbox)
        

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        print('>> Connect Server')
        start_new_thread(self.recv_data, (self.client_socket,))
        
  
    def send_message(self):
        message = self.input_box.text()
        if message == 'quit':
            self.client_socket.send(message.encode())
            self.client_socket.close()
            QApplication.quit()
            return
        try:
            self.client_socket.send(message.encode())
            self.input_box.clear()
            self.message_display.append("나: " + message)
            print("메시지 전송 성공:", message)
        except Exception as e:
            print("메시지 전송 실패:", e)
                
    def recv_data(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode()
            self.message_display.append("상대방: " + message)
            print("recive : ", repr(data.decode()))
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
