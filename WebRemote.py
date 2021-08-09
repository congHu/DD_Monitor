from threading import Thread
from PyQt5.QtCore import QObject, QStringListModel, QThread, pyqtSignal
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

class WebRemoteServer(QObject):
    setRoomId = pyqtSignal(list)
    setVolume = pyqtSignal(list)

    liverInfo = []
    # ws = WebsocketServer(wsRemotePort, host='0.0.0.0', loglevel=logging.INFO)

    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def run(self):
        # Thread(target=self.startWs, daemon=True).start()

        app = Flask('DDWebRemote', template_folder=os.path.abspath('webRemote'), static_folder=os.path.abspath('webRemote/static'))
        app.config['JSON_AS_ASCII'] = False
        app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
        self.socketio = SocketIO(app)
    
        @app.route('/')
        def index():
            liveInfo = {}
            for live in self.liverInfo:
                liveInfo[live[1]] = live
            playerInfo = [{
                'roomid': roomid,
                'face': liveInfo[roomid][3] if roomid in liveInfo else 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==',
                'uname': '#%d: %s%s' % (i+1, '(未开播) ' if roomid in liveInfo and liveInfo[roomid][4]==2 else '', liveInfo[roomid][2] if roomid in liveInfo else '空'),
                'liveStatus': liveInfo[roomid][4] if roomid in liveInfo else 2,
                'mute': self.config['muted'][i],
                'volume': self.config['volume'][i],
            } for i,roomid in enumerate(self.config['player'])]
            self.liverInfo.sort(key=lambda i:i[4])
            return render_template('index.html', config=self.config, liverInfo=self.liverInfo, playerInfo=playerInfo)
        # @app.route('/cards')
        # def cards():
        #     # uid, str(roomID), uname, face, liveStatus, keyFrame, title
        #     return jsonify(self.liverInfo)
        # @app.route('/config')
        # def config():
        #     return jsonify(self.config)
        
        @app.route('/setroom', methods=['POST'])
        def setroom():
            try:
                index = request.form.get('index')
                roomid = request.form.get('roomid')
                if index is None or roomid is None or roomid == '':
                    return jsonify({'msg': 'empty params', 'code': 1})
                index = int(index)
                if index < 0 or index > 16:
                    return jsonify({'msg': 'out of range', 'code': 1})
                self.setRoomId.emit([index, roomid])
                return jsonify({'msg': 'success', 'code': 0})
            except Exception as e:
                return jsonify({'msg': e.args, 'code': 1})

        @app.route('/setvol', methods=['POST'])
        def setvol():
            try:
                index = request.form.get('index')
                vol = request.form.get('vol')
                if index is None or vol is None:
                    return jsonify({'msg': 'empty params', 'code': 1})
                index = int(index)
                if index < 0 or index > 16:
                    return jsonify({'msg': 'out of range', 'code': 1})
                vol = int(vol)
                if vol < 0:
                    vol = 0
                if vol > 100:
                    vol = 100
                self.setVolume.emit([index, vol])
                return jsonify({'msg': 'success', 'code': 0})
            except Exception as e:
                return jsonify({'msg': e.args, 'code': 1})

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
        print('sync-config')
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