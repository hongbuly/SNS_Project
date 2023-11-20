import socket
from _thread import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class make_bubble(QStyledItemDelegate):
    bubble_margins = QMargins(15, 5, 35, 5)
    msg_margins = QMargins(20, 15, 20, 15)
    b_margins = bubble_margins * 2

    me_color = QColor("#BCE55C") # 나의 말풍선 색
    other_color = QColor("#D5D5D5") # 상대방의 말풍선 색

    def paint(self, painter, option, index):
        sender, msg = index.model().data(index, Qt.DisplayRole)

        bubble_rect = option.rect.marginsRemoved(self.bubble_margins)
        b_rect = option.rect.marginsRemoved(self.b_margins)

        color = 0
        point = 0
        if sender == 'me':
            color = self.me_color
            point = bubble_rect.topRight()
        else:
            color = self.other_color
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
        rect = option.rect.marginsRemoved(self.msg_margins)
        rect = metrics.boundingRect(rect, Qt.TextWordWrap, msg)
        rect = rect.marginsAdded(self.msg_margins)
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
    
    def add_message(self, sender, msg):
        if msg:
            self.messages.append((sender, msg))
            self.layoutChanged.emit()


class MyWindow(QWidget):
    update_chat = pyqtSignal()

    def __init__(self):
        super().__init__()

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
        self.message_display = QListView(self)
        self.message_display.setItemDelegate(make_bubble())

        self.msgModel = msg_model()
        self.message_display.setModel(self.msgModel)

        
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

        self.update_chat.connect(self.update_chat_room)
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        print('>> Connect Server')
        start_new_thread(self.recv_data, (self.client_socket,))

    def update_chat_room(self):
        self.msgModel.layoutChanged.emit()
        self.message_display.scrollToBottom()  
  
    def send_message(self):
        message = self.input_box.text()
        if message == 'quit':
            self.client_socket.send(message.encode())
            self.client_socket.close()
            QApplication.quit()
            return
        elif len(message) == 0:
            return
        
        try:
            self.client_socket.send(message.encode())
            self.input_box.clear()
            self.msgModel.add_message('me', "나: " + message)
            self.message_display.scrollToBottom()
            print("메시지 전송 성공:", message)
        except Exception as e:
            print("메시지 전송 실패:", e)
                
    def recv_data(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode()
            self.msgModel.add_message('other', "상대방: " + message)
            self.message_display.scrollToBottom()
            self.update_chat.emit()
            print("recive : ", repr(data.decode()))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
