#!/usr/bin/env python
#-*-coding:gb18030-*-
# 原理：把矩阵的图片看成一个完整的数列；
# 把游戏看作移动空白格，使图片复原的过程。
# 空白格的移动对数列奇偶性不会产生影响。
# 要使得打乱顺序后的图片能够复原，则保证
# 打乱前后两种图片的奇偶性一致即可。

import sys, random
from PyQt4 import QtCore, QtGui, phonon

FORMWIDTH     = 324
FORMHEIGHT    = 354
SCENESIZE     = 300
COUNT         = 5
PIECESIZE     = SCENESIZE/COUNT
BLANKPIECE    = "piece44"
FILENAME      = "beauty.jpg"
check         = 0             # 矩阵奇偶性校验 原始图案矩阵为偶数列

# 完成拼图后播放的声音
class YeahPlayer(phonon.Phonon.MediaObject):
    def __init__(self):
        super(YeahPlayer, self).__init__()
        self.source = phonon.Phonon.MediaSource("yeah.wav")
        self.setCurrentSource(self.source)

        self.audio  = phonon.Phonon.AudioOutput(phonon.Phonon.MusicCategory)

        phonon.Phonon.createPath(self, self.audio)    

class Piece(QtGui.QGraphicsWidget):
    def __init__(self, image, pos, parent=None):
        super(Piece, self).__init__(parent)
        self.image     = image
        self.setPos(pos.x(), pos.y())
        self.animation = QtCore.QPropertyAnimation(self, "geometry")
        self.animation.setDuration(500)
        self.connect(self.animation, QtCore.SIGNAL("valueChanged(const QVariant)"), self.bravo)

    # 查找当前piece四周的pieces 判断其是否为blank
    # 若找到则返回此piece，否则返回None
    def findBlank(self):
        x = self.pos().x()
        y = self.pos().y()

        l = QtCore.QPointF(x-PIECESIZE-1,y)
        r = QtCore.QPointF(x+PIECESIZE+1,y)
        t = QtCore.QPointF(x,y-PIECESIZE-1)
        b = QtCore.QPointF(x,y+PIECESIZE+1)

        for item in self.scene().items():
            if item.pos() in [l,r,t,b] and item.objectName() == QtCore.QString(BLANKPIECE):
                return item

        return None

    # 检查图片是否复原了
    def check(self):
        for item in self.scene().items():
            name = item.objectName()
            ox = float(name[-2])
            oy = float(name[-1])
            cx = item.pos().x()/(PIECESIZE+1)
            cy = item.pos().y()/(PIECESIZE+1)

            if ox != cx or oy != cy:
                return False
        
        return True

    # 计算自己到最左上角位置的偏移量
    def sum(self):
        x = self.pos().x()/(PIECESIZE+1)
        y = self.pos().y()/(PIECESIZE+1)
        return x + COUNT*y

    # 现在，我们有了动画支持
    def swap(self, other, anim=False):
        o = other.pos()
        c = self.pos()

        if anim == False:
            self.setPos(o)
            other.setPos(c)
        elif anim == True:
            self.animation.setStartValue(QtCore.QRect(c.x(),c.y(),
                                                      PIECESIZE,PIECESIZE))
            self.animation.setEndValue(QtCore.QRect(o.x(),o.y(),
                                                PIECESIZE,PIECESIZE))
            other.setPos(c)
            self.animation.start()
        # 重绘整个scene 不然显示会不正常
        self.scene().update()

    def kick(self):
        if self.objectName() == QtCore.QString(BLANKPIECE):
            return

        for item in self.scene().items():
            if item.objectName() == QtCore.QString(BLANKPIECE):
                curr_len = self.sum()
                item_len = item.sum()

                self.swap(item)
                # 和空白格相距奇数距离 并作了交换 奇偶性发生改变
                # 相差奇数个，则相隔偶数个
                if abs(curr_len-item_len) % 2 == 0:
                    global check
                    if check == 0:
                        check = 1
                    elif check == 1:
                        check = 0

    def paint(self, painter, option, widget):
        painter.drawImage(QtCore.QRectF(0,0,PIECESIZE, PIECESIZE), self.image)

    def mousePressEvent(self, event):
        blank = self.findBlank()
        if blank:
            blank_len = blank.sum()
            curr_len  = self.sum()
            self.swap(blank, True)
            if abs(curr_len-blank_len) % 2 == 0:
                global check
                if check == 0:
                    check = 1
                elif check == 1:
                    check = 0

        super(Piece, self).mousePressEvent(event)

    def bravo(self):
        if self.check():
            for item in self.scene().items():
                if item.objectName() == QtCore.QString(BLANKPIECE):
                    item.setVisible(True)
                    self.scene().parent().parent().yeah.stop()
                    self.scene().parent().parent().yeah.play()
            self.scene().update()

            self.scene().parent().parent().timer.stop()
            self.scene().parent().parent().hasStart = 0
            QtGui.QMessageBox.information(self.scene().parent().parent(), 
                                          u"完成", u"恭喜啊, 你做到了!\n用时%s" % self.scene().parent().parent().display.text(), 
                                          QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
        


class View(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene(0,0,SCENESIZE, SCENESIZE,self)
        self.scene.setBackgroundBrush(QtCore.Qt.white)
        self.setScene(self.scene)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


class MainForm(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainForm,self).__init__(parent)
        self.setMinimumSize(FORMWIDTH, FORMHEIGHT)
        self.setMaximumSize(FORMWIDTH, FORMHEIGHT)

        self.yeah    = YeahPlayer()
        self.view    = View()
        self.sButton = QtGui.QPushButton(u"开始(&S)")
        self.qButton = QtGui.QPushButton(u"原图(&O)")
        self.qButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.display = QtGui.QLabel(u"  0小时  0分钟  0秒")
        self.timer   = QtCore.QTimer()
        self.time    = QtCore.QTime()
        self.hasStart= 0

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.view)
        bLayout = QtGui.QHBoxLayout()
        bLayout.addWidget(self.sButton)
        bLayout.addWidget(self.qButton)
        bLayout.addWidget(self.display)
        layout.addLayout(bLayout)

        self.setLayout(layout)

        pixmap = QtGui.QPixmap()
        if not pixmap.load(FILENAME):
            QtGui.QMessageBox.warning(self, u"载入", u"无法载入图片 'beauty.jpg'", 
                                      QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton)
            sys.exit(1)

        self.icon = QtGui.QIcon(pixmap)
        self.setWindowIcon(self.icon)

        self.load()
        self.setWindowTitle(u"滑块拼图")
        self.connect(self.sButton, QtCore.SIGNAL("clicked()"), self.setup)
        self.connect(self.qButton, QtCore.SIGNAL("clicked()"), self.load)
        self.connect(self.timer,   QtCore.SIGNAL("timeout()"), self.timeout)


    def timeout(self):
        if self.hasStart:
            el = self.time.elapsed()

            s  = el/1000
            m  = s/60               
            if m > 0:
                s  = s%60
            h  = m/60
            if h > 0:
                m  = m%60
            
            if h < 24:
                self.display.setText(u" %2d小时 %2d分钟 %2d秒" % (h,m,s))
            else:
                self.display.setText(u" 太久了,拒绝显示...")

    def load(self):
        self.view.scene.clear()
        self.hasStart = 0
        self.display.setText(u"  0小时  0分钟  0秒")

        image = QtGui.QImage()
        if not image.load(FILENAME):
            QtGui.QMessageBox.warning(self, u"载入", u"无法载入图片 'beauty.jpg'", 
                                      QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton)
            sys.exit(1)

        for i in range(COUNT):
            for j in range(COUNT):
                piece = Piece(image.copy(i*(PIECESIZE+1),j*(PIECESIZE+1),PIECESIZE,PIECESIZE), QtCore.QPointF(i*(PIECESIZE+1),j*(PIECESIZE+1)))
                piece.setObjectName("piece%d%d" % (i,j))
                piece.setAcceptedMouseButtons(QtCore.Qt.NoButton)
                self.view.scene.addItem(piece)

        self.view.scene.update()

    def setup(self):
        for item in self.view.scene.items():
            if item.objectName() == QtCore.QString(BLANKPIECE):
                item.setVisible(False)

        random.seed(QtGui.QCursor.pos().x()^QtGui.QCursor.pos().y())

        while True:
            for i in range(COUNT):
                for j in range(COUNT):
                    if random.random() < 0.5:
                        if i==COUNT-1 and j==COUNT-1:
                            continue
                        for item in self.view.scene.items():
                            if item.objectName() == QtCore.QString("piece%d%d" % (i,j)):
                                item.kick()
            global check
            if check == 1:
                continue
            elif check == 0:
                break

        for item in self.view.scene.items():
            item.setAcceptedMouseButtons(QtCore.Qt.LeftButton)

        self.time.restart()
        self.timer.start()
        self.hasStart = 1
                    
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    window = MainForm()
    window.show()

    sys.exit(app.exec_())
