#!/usr/bin/env python
#-*-coding:gb18030-*-
# ԭ���Ѿ����ͼƬ����һ�����������У�
# ����Ϸ�����ƶ��հ׸�ʹͼƬ��ԭ�Ĺ��̡�
# �հ׸���ƶ���������ż�Բ������Ӱ�졣
# Ҫʹ�ô���˳����ͼƬ�ܹ���ԭ����֤
# ����ǰ������ͼƬ����ż��һ�¼��ɡ�

import sys, random
from PyQt4 import QtCore, QtGui

FORMWIDTH     = 324
FORMHEIGHT    = 354
SCENESIZE     = 300
COUNT         = 5
PIECESIZE     = SCENESIZE/COUNT
BLANKPIECE    = "piece44"

check         = 0             # ������ż��У�� ԭʼͼ������Ϊż����

class Piece(QtGui.QGraphicsWidget):
    def __init__(self, image, parent=None):
        super(Piece, self).__init__(parent)
        self.image   = image
        self.next    = None     # ��Ҫ���Լ�����λ�õ��Ǹ�piece

    # ���ҵ�ǰpiece���ܵ�pieces �ж����Ƿ�Ϊblank
    # ���ҵ��򷵻ش�piece�����򷵻�None
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

    # ���ͼƬ�Ƿ�ԭ��
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

    # �����Լ��������Ͻ�λ�õ�ƫ����
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
        # �ػ�����scene ��Ȼ��ʾ�᲻����
        self.scene().update()

    def kick(self):
        if self.objectName() == QtCore.QString(BLANKPIECE):
            return

        for item in self.scene().items():
            if item.objectName() == QtCore.QString(BLANKPIECE):
                curr_len = self.sum()
                item_len = item.sum()

                self.swap(item)
                # �Ϳհ׸������������ �����˽��� ��ż�Է����ı�
                # ����������������ż����
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
        self.sButton = QtGui.QPushButton(u"��ʼ(&S)")
        self.qButton = QtGui.QPushButton(u"ԭͼ(&O)")
        self.qButton.setFocusPolicy(QtCore.Qt.NoFocus)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.view)
        bLayout = QtGui.QHBoxLayout()
        bLayout.addWidget(self.sButton)
        bLayout.addWidget(self.qButton)
        layout.addLayout(bLayout)
        self.setLayout(layout)

        self.load()
        self.setWindowTitle(u"����ƴͼ")
        self.connect(self.sButton, QtCore.SIGNAL("clicked()"), self.setup)
        self.connect(self.qButton, QtCore.SIGNAL("clicked()"), self.load)

    def load(self):
        self.view.scene.clear()

        fileName = 'beauty.jpg'
        image = QtGui.QImage()
        if not image.load(fileName):
            QtGui.QMessageBox.warning(self, u"����", u"�޷�����ͼƬ 'beauty.jpg'", QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton)
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
