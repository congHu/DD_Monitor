from threading import Thread
from PyQt5.QtCore import QStringListModel, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QListView
from PyQt5.QtGui import QImage,QPixmap
from flask import Flask,jsonify,request,render_template
# from websocket_server import WebsocketServer
from flask_socketio import SocketIO, emit
import socket
import qrcode
import io
import os
import json
import logging

webRemotePort = 30148
# wsRemotePort = 30149

class WebRemoteServer:
    getRoomIds = pyqtSignal(str)

    liverInfo = []
    # ws = WebsocketServer(wsRemotePort, host='0.0.0.0', loglevel=logging.INFO)

    def __init__(self, config):
        self.config = config
    
    def run(self):
        # Thread(target=self.startWs, daemon=True).start()

        app = Flask('DDWebRemote', template_folder=os.path.abspath('webRemote'), static_folder=os.path.abspath('webRemote/static'))
        app.config['JSON_AS_ASCII'] = False
        app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
        self.socketio = SocketIO(app)
    
        @app.route('/')
        def index():
            return render_template('index.html', config=self.config, liverInfo=self.liverInfo)
        # @app.route('/cards')
        # def cards():
        #     # uid, str(roomID), uname, face, liveStatus, keyFrame, title
        #     return jsonify(self.liverInfo)
        # @app.route('/config')
        # def config():
        #     return jsonify(self.config)
        
        @app.route('/setroom')
        def setroom():
            request.form.get('')

        @self.socketio.event
        def my_event(message):
            # emit('my response', {'data': 'got it!'})
            print('recv', message)

        # app.run('0.0.0.0', webRemotePort)
        self.socketio.run(app, '0.0.0.0', webRemotePort)


    def syncInfo(self, liverInfo):
        self.liverInfo = liverInfo
    def deleteRoomId(self, roomId):
        self.socketio.emit('delete_roomid', roomId)
    def syncConfig(self, config):
        self.config = config
        self.socketio.emit('config', config)



class WebRemoteDialog(QWidget):
    def __init__(self):
        super(WebRemoteDialog, self).__init__()
        self.resize(350, 150)
        self.setWindowTitle('遥控器二维码')
        layout = QGridLayout(self)

        # self.serverSwitch = QPushButton()
        # self.serverSwitch.setText("服务开关")
        # layout.addWidget(self.serverSwitch, 0, 0)
        # self.serverSwitch.clicked.connect(self.toggleServerSwitch)

        self.listview = QListView()
        self.listview.setVisible(False)
        layout.addWidget(self.listview, 0, 0)
        self.listview.clicked.connect(self.listClicked)

        self.qrview = QLabel()
        self.qrview.setText("二维码")
        self.qrview.setMinimumSize(210,210)
        self.qrview.setScaledContents(True)
        self.qrview.setVisible(False)
        layout.addWidget(self.qrview, 0, 1)

        # self.webRemoteServer = WebRemoteServer()
        # Thread(target=self.webRemoteServer.run, daemon=True).start()
        # self.webRemoteServer.run()
    
    def show(self):
        # if self.webRemoteServer.isRunning():
        #     self.serverSwitch.setText("关闭遥控服务")
        #     self.showIpListAndGenQR()
        # else:
        #     self.serverSwitch.setText("开启遥控服务")
        self.showIpListAndGenQR()
        
        super().show()

    def showIpListAndGenQR(self):
        self.listview.setVisible(True)
        self.qrview.setVisible(True)
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        self.ipList = list(filter(lambda ip:':' not in ip and ip != '127.0.0.1', map(lambda a:a[4][0], addrs)))

        model = QStringListModel()
        model.setStringList(self.ipList)
        self.listview.setModel(model)

        if len(self.ipList) > 0:
            self.listview.setCurrentIndex(model.index(0))
            self.generateQrcode(0)
    
    def listClicked(self,index):
        self.generateQrcode(index.row())
    
    def generateQrcode(self,index):
        print(self.ipList[index])
        qr = qrcode.QRCode(
            version=1,
            box_size=10
        )
        qr.add_data("http://%s:%s" % (self.ipList[index],webRemotePort))
        qrimg = qr.make_image()
        fp = io.BytesIO()
        qrimg.save(fp,"BMP")
        image = QImage()
        image.loadFromData(fp.getvalue(),"BMP")
        self.qrview.setPixmap(QPixmap.fromImage(image))
        pass