# PyQt5 Video player
#!/usr/bin/env python

id = 2

array_out =[11,id,0,0,0,0]

video_state = 0




from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal,QUrl)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,QSizeGrip)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
from PyQt5 import QtGui
import ASUS.GPIO as GPIO
import time

import serial
ser = serial.Serial("/dev/ttyS1", 9600, timeout=1)





GPIO.setwarnings(False)
GPIO.setmode(GPIO.ASUS)

Sw = 257

class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)
        wid = QWidget(self)
        self.setCentralWidget(wid)


        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(videoWidget)

        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.test = AThread()
        self.test.start()
        self.test.my_signal.connect(self.my_event)

    def my_event(self,data):
        # gets executed on my_signal 
        print("hello")
        print(data)
        self.openFile()
        self.play()
        pass


    def openFile(self):
        fileName= "/home/linaro/prog/gpio video/Pista Memory ENG.mp4"

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        global video_state

        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            video_state = 1
            self.mediaPlayer.play()

    def stop(self):
        global video_state
        self.mediaPlayer.stop()
        video_state = 0

    def state_check(self):
        global video_state
        if(self.mediaPlayer.state() == 0):
            video_state = 0
        else:
            video_state = 1


class AThread(QThread):
    global array_out
    my_signal = pyqtSignal(str)     
    def run(self):
        GPIO.setup(Sw, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(224, GPIO.OUT)
        GPIO.output(224, GPIO.LOW)
        gpio_counter = 0
        sw_pres = 0
        data_uart=[0,0,0,0,0,0]
        uart_coutner = 0
        while True:
            video_check()
            response = ser.read()
            response = int.from_bytes(response, byteorder='big', signed=False)
            if(response == 240 and uart_coutner == 0):
                uart_coutner = 1
                data_uart[0] = response
            elif(uart_coutner > 0):
                
                data_uart[uart_coutner] = response
                uart_coutner = uart_coutner + 1
                if(uart_coutner == 6):
                    cs = data_uart[0] + data_uart[1] +data_uart[2] + data_uart[3] +data_uart[4]
                    while(cs > 256):
                        cs = cs-256
                    if(data_uart[1]== id and cs == data_uart[5]):
                        GPIO.output(224, GPIO.HIGH)
                        self.mount_array()
                        frame = bytearray()
                        for x in array_out:
                            frame.append(x)

                        ser.write(frame)
                        ser.flush()
                        if(data_uart[2] == 1):
                            play_video()
                        elif(data_uart[2] == 2):
                            stop_video()
                    uart_coutner = 0
                    GPIO.output(224, GPIO.LOW)
                    print(data_uart)
#gpio manange
            if(GPIO.input(Sw) == 0):
                gpio_counter += 1
                if(gpio_counter == 50):
                    sw_pres =1
            else:
                gpio_counter = 0
                if(sw_pres == 1):
                    sw_pres = 0
                    self.my_signal.emit("1")       

    def mount_array(self):
        global video_state
        global array_out
        if(video_state == 1):
            array_out[2] = 100
        else:
            array_out[2] = 0

        array_out[5] =  array_out[0]+ array_out[1]+ array_out[2]+ array_out[3]+ array_out[4]
        




def play_video():
    print("in2")
    player.openFile()
    player.play()

def stop_video():
    print("stop")
    player.stop()
    player.openFile()

def video_check():
    player.state_check()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QVideoWidget::item { border: 0px solid black }; ")
    player = VideoWindow()
    player.showFullScreen()
    player.setWindowOpacity(0.95)
    player.show()
    # player.openFile()
    # player.play()
    # thread = AThread()
    # thread.finished.connect(app.exit)
    # thread.start()
    sys.exit(app.exec_())