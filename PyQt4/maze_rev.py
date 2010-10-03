#!/usr/bin/env python
#-*-coding:gb18030-*-
# 原理：把矩阵的图片看成一个完整的数列；
# 把游戏看作移动空白格，使图片复原的过程。
# 空白格的移动对数列奇偶性不会产生影响。
# 要使得打乱顺序后的图片能够复原，则保证
# 打乱前后两种图片的奇偶性一致即可。

import sys, random
from PyQt4 import QtCore, QtGui

FORMWIDTH     = 324
FORMHEIGHT    = 354
SCENESIZE     = 300
COUNT         = 5
PIECESIZE     = SCENESIZE/COUNT
BLANKPIECE    = "piece44"

check         = 0             # 矩阵奇偶性校验 原始图案矩阵为偶数列

class Piece(QtGui.QGraphicsWidget):
    def __init__(self, image, parent=None):
        super(Piece, self).__init__(parent)
        self.image   = image
        self.next    = None     # 将要和自己交换位置的那个piece

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
            ox = int(name[-2])
            oy = int(name[-1])
            cx = item.pos().toPoint().x()/(PIECESIZE+1)
            cy = item.pos().toPoint().y()/(PIECESIZE+1)

            if ox != cx or oy != cy:
                return False
        
        return True

    # 计算自己到最左上角位置的偏移量
    def sum(self):
        x = self.pos().x()/(PIECESIZE+1)
        y = self.pos().y()/(PIECESIZE+1)
        return x + COUNT*y

    # @other: Piece
    def swap(self, other):
        o = other.pos()
        c = self.pos()

        self.setPos(o)
        other.setPos(c)
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
            self.swap(blank)
            if abs(curr_len-blank_len) % 2 == 0:
                global check
                if check == 0:
                    check = 1
                elif check == 1:
                    check = 0

        if self.check():
            for item in self.scene().items():
                if item.objectName() == QtCore.QString(BLANKPIECE):
                    item.setVisible(True)
            self.scene().update()
        
        super(Piece, self).mousePressEvent(event)



class View(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene(0,0,SCENESIZE, SCENESIZE,self)
        self.scene.setBackgroundBrush(QtCore.Qt.white)
        self.setScene(self.scene)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


class MainForm(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MainForm,self).__init__(parent)
        self.setMinimumSize(FORMWIDTH, FORMHEIGHT)
        self.setMaximumSize(FORMWIDTH, FORMHEIGHT)

        self.view    = View()
        self.sButton = QtGui.QPushButton(u"开始(&S)")
        self.qButton = QtGui.QPushButton(u"原图(&O)")
        self.qButton.setFocusPolicy(QtCore.Qt.NoFocus)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.view)
        bLayout = QtGui.QHBoxLayout()
        bLayout.addWidget(self.sButton)
        bLayout.addWidget(self.qButton)
        layout.addLayout(bLayout)
        self.setLayout(layout)

        self.load()
        self.setWindowTitle(u"滑块拼图")
        self.connect(self.sButton, QtCore.SIGNAL("clicked()"), self.setup)
        self.connect(self.qButton, QtCore.SIGNAL("clicked()"), self.load)

    def load(self):
        self.view.scene.clear()

        fileName = 'beauty.jpg'
        image = QtGui.QImage()
        if not image.load(fileName):
            QtGui.QMessageBox.warning(self, u"载入", u"无法载入图片 'beauty.jpg'", QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton)
            sys.exit(1)

        for i in range(COUNT):
            for j in range(COUNT):
                piece = Piece(image.copy(i*(PIECESIZE+1),j*(PIECESIZE+1),PIECESIZE,PIECESIZE))
                piece.setObjectName("piece%d%d" % (i,j))
                piece.setPos(i*(PIECESIZE+1),j*(PIECESIZE+1))
                piece.setAcceptedMouseButtons(QtCore.Qt.NoButton)
                self.view.scene.addItem(piece)

        self.view.scene.update()

    def setup(self):
        for item in self.view.scene.items():
            item.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
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
                            
                    
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    window = MainForm()
    window.show()

    sys.exit(app.exec_())
