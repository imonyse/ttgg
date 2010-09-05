#!/usr/bin/env python
#-*-coding=utf-8-*-
# Copyright (C) 2009 by Huang Wei
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import maze_rc

# 定义的水平和垂直的块数
hcnt = 5
vcnt = 5

# 这个是右边的示例图片
class GoalImage(QLabel):
    def __init__(self, parent=None):
        super(GoalImage, self).__init__(parent)
        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 500)

# 这个是左边玩游戏的地方
class PuzzleWidget(QWidget):
    def __init__(self, parent=None):
        super(PuzzleWidget, self).__init__(parent)

        # inPlace -> 各就各位了:)
        # 初始化完毕后，在setPuzzle()里一个打乱拷贝的过程会改变此值
        self.inPlace = hcnt*vcnt
        layout = QGridLayout()
        layout.setSpacing(0)

        # 绘出里面的游戏格
        for row in range(vcnt):
            for column in range(hcnt):
                # 最后一列空一个地方出来不画格子
                cellWidget = CellWidget()
                cellWidget.setObjectName("cell_%d_%d" % (row, column))
                layout.addWidget(cellWidget, row, column)

        self.setLayout(layout)
        self.setMinimumSize(520, 520)
        self.setMaximumSize(520, 520)

    # 在设置puzzle的时候调用，把图片打乱
    # 挨着空格的那个特殊格子是不可以换地方的
    # 此函数，从(column,row)处取出一片 然后追加到widget末尾
    def takeItemInsert(self, row, column):
        cellList = []
        itemList = []
        cellWidget = self.findChild(QListWidget, "cell_%d_%d" % (row,column))
        if cellWidget:
            cellList.append(cellWidget)

            for y in range(column+1, hcnt):
                cell = self.findChild(QListWidget, "cell_%d_%d" % (row,y))
                if cell.inPlace:
                    self.inPlace -= 1
                    cell.inPlace = 0
                cellList.append(cell)
                item = cell.takeItem(0)
                itemList.append(item)

            for x in range(row+1, vcnt):
                for y in range(hcnt):
                    cell = self.findChild(QListWidget, "cell_%d_%d" % (x,y))
                    if cell.inPlace:
                        self.inPlace -= 1
                        cell.inPlace = 0
                    cellList.append(cell)
                    item = cell.takeItem(0)
                    itemList.append(item)

            item = cellWidget.takeItem(0)
            if cellWidget.inPlace:
                self.inPlace -= 1
                cellWidget.inPlace = 0
            itemList.append(item)

        self.insertItemList(cellList, itemList)

    # 把一个item表的数据依次插入一个cell表，两个表的大小必须相同
    def insertItemList(self, cellList, itemList):
        k = 0
        if len(cellList) != len(itemList):
            return

        while(k < len(cellList)):
            cell = cellList[k]
            item = itemList[k]
            k += 1
            location = item.data(Qt.UserRole+1).toPoint()
            name = cell.objectName()
            y = int(name[name.indexOf('_') + 1])
            x = int(name[name.lastIndexOf('_') + 1])
            cell.insertItem(0, item)

            if location == QPoint(x, y):
                cell.inPlace = 1
                self.inPlace += 1

    def tryToMove(self, row, column):
        pass

#        me = self.findChild(QListWidget, "cell_%d_%d" % (row, column))
#        leftCell = self.findChild(QListWidget, "cell_%d_%d" % (row, column-1))
#        rightCell = self.findChild(QListWidget, "cell_%d_%d" % (row, column+1))
#        upperCell = self.findChild(QListWidget, "cell_%d_%d" % (row-1, column))
#        lowerCell = self.findChild(QListWidget, "cell_%d_%d" % (row+1, column))
#
#        for eachCell in (leftCell, rightCell, upperCell, lowerCell):
#            if not eachCell:
#                name = eachCell.objectName()
#                y = int(name[name.indexOf('_') + 1])
#                x = int(name[name.lastIndexOf('_') + 1])
#                
#                if x == 4 and y == 2:
#                    me.move(QPoint(x,y))
#                elif 0<=y<=2 and 0<=x<=3:
#                    me.move(QPoint(x,y))
#                else:
#                    return

    # 统一在这里管理Drag&Drop的状态. flag为1时，是设定空白格附近的四个格子都可以移动；
    # flag为0是，则是因为有别的格子移了过来，所以设置附近四个格子不可移动
    def changeDragDropStatus(self, row, column, flag):
        me = self.findChild(QListWidget, "cell_%d_%d" % (row, column))

        leftCell = self.findChild(QListWidget, "cell_%d_%d" % (row, column-1))
        rightCell = self.findChild(QListWidget, "cell_%d_%d" % (row, column+1))
        upperCell = self.findChild(QListWidget, "cell_%d_%d" % (row-1, column))
        lowerCell = self.findChild(QListWidget, "cell_%d_%d" % (row+1, column))

        if flag:
            me.setAcceptDrops(True)
            for eachCell in (leftCell, rightCell, upperCell, lowerCell):
                if eachCell:
                    eachCell.dragable = 1
        else:
            me.setAcceptDrops(False)
            for eachCell in (leftCell, rightCell, upperCell, lowerCell):
                if eachCell:
                    eachCell.dragable = 0
            
    # 此函数只在生成puzzle的时候调用
    def addPiece(self, pixmap, location):
        pos = QVariant(location).toPoint()
        row = pos.y()
        column = pos.x()
        cellWidget = self.findChild(QListWidget, "cell_%d_%d" % (row, column))
        pieceItem = QListWidgetItem(cellWidget)
        pieceItem.setIcon(QIcon(pixmap))
        pieceItem.setData(Qt.UserRole, QVariant(pixmap))
        pieceItem.setData(Qt.UserRole+1, QVariant(location))
        pieceItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

    def clear(self):
        self.inPlace = hcnt*vcnt
        for row in range(vcnt):
            for column in range(hcnt):
                cellWidget = self.findChild(QListWidget, "cell_%d_%d" % (row, column))
                cellWidget.clear()


class CellWidget(QListWidget):
    def __init__(self, parent=None):
        super(CellWidget, self).__init__(parent)
        # 单个格子也记录自己是否到位的状态
        # 初始状态到位，接下来首先在setPuzzle()里面可能会改变此状态
        self.inPlace = 1
        # 只有满足特定条件的格子才能Drag&Drop
        self.dragable = 0
        self.setAcceptDrops(False)

        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(90, 90))

        self.setMinimumSize(100, 100)
        self.setMaximumSize(100, 100)

    def clear(self):
        self.inPlace = 1
        self.dragable = 0
        self.setAcceptDrops(False)
        self.takeItem(0)
        self.update()

    # 此函数主要在生drop图片的时候调用，设置CellWidget的item状态
    def addPiece(self, pixmap, location):
        pieceItem = QListWidgetItem(self)
        pieceItem.setIcon(QIcon(pixmap))
        pieceItem.setData(Qt.UserRole, QVariant(pixmap))
        pieceItem.setData(Qt.UserRole+1, QVariant(location))
        pieceItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

    def mousePressEvent(self, event):
        item = self.currentItem()
        if not item:
            return

        location = item.data(Qt.UserRole+1).toPoint()
        pixmap = QPixmap(item.data(Qt.UserRole))
        name = self.objectName()
        y = int(name[name.indexOf('_') + 1])
        x = int(name[name.lastIndexOf('_') + 1])

        if location == QPoint(x, y):
            self.inPlace = 0
            self.parent().inPlace -= 1

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << pixmap << location
        mimeData = QMimeData()
        mimeData.setData("image/x-puzzle-piece", itemData)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width()/2, pixmap.height()/2))

        if self.dragable:
            if not (drag.start(Qt.MoveAction) == Qt.MoveAction):
                if location == QPoint(x,y):
                    self.inPlace = 1
                    self.parent().inPlace += 1
            else:
                self.takeItem(self.row(item))
                self.parent().changeDragDropStatus(y, x, 1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-piece"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-piece"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event): 
        if event.mimeData().hasFormat("image/x-puzzle-piece"):
            pieceData = event.mimeData().data("image/x-puzzle-piece")
            dataStream = QDataStream(pieceData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            location = QPoint()
            dataStream >> pixmap >> location
            
            self.addPiece(pixmap, location)

            event.setDropAction(Qt.MoveAction)
            event.accept()

            # 根据cell的名字，和图片内部存储的位置进行比较，看是否到位了
            # 给定的location(是一个QPoint对象)，来确定一个放置的方块
            # 因为最初切割图像的每个方块的正确位置，都以UserRole+1的类型放置在每一个图片中
            # 所以，如果这个方块的位置和图片存放的location一致，则表明图片放对了
            name = self.objectName()
            y = int(name[name.indexOf('_') + 1])
            x = int(name[name.lastIndexOf('_') + 1])

            if location == QPoint(x, y):
                self.inPlace = 1
                self.parent().inPlace += 1

                if self.parent().inPlace == hcnt*vcnt:
                    self.parent().emit(SIGNAL("puzzleCompleted()"))
                    return
            
            self.parent().changeDragDropStatus(y, x, 0)
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        item = self.currentItem()
        if not item:
            return
        
        name = self.objectName()
        y = int(name[name.indexOf('_') + 1])
        x = int(name[name.lastIndexOf('_') + 1])

        self.parent().tryToMove(x, y)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.puzzleImage = QPixmap()
        self.image = QPixmap()
        self.setupMenus()
        self.setupWidgets()
        self.setWindowTitle(QString(u"拼图游戏"))

    def openImage(self, path=QString()):
        fileName = path

        if fileName.isNull():
            fileName = QFileDialog.getOpenFileName(self, QString(u"打开"),
                                                   "", "Image (*.png *.jpg *.bmp)")

        if not fileName.isEmpty():
            newImage = QPixmap()
            if not newImage.load(fileName):
                QMessageBox.warning(self, QString(u"打开"), QString(u"无法载入指定文件"),
                                    QMessageBox.Cancel, QMessageBox.NoButton)
                return

            self.image = newImage
            self.setupPuzzle()

    def setCompleted(self):
        button = QMessageBox.question(self, u"问题", u"拼图完成\n游戏将重新开始", 
                                      QMessageBox.Ok | QMessageBox.No, QMessageBox.No)
        if button == QMessageBox.Ok:
            self.setupPuzzle()

    def setupPuzzle(self):      
        self.puzzleImage = self.image.copy(0, 0, self.image.width(), 
                                           self.image.height()).scaled(500, 500, 
                                                                       Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        
        self.puzzleWidget.clear()

        for y in range(vcnt):
            for x in range(hcnt):
                pieceImage = self.puzzleImage.copy(x*100, y*100, 100, 100)
                self.puzzleWidget.addPiece(pieceImage, QPoint(x,y))

        # 打乱图片位置。打乱后的图片序列必须和原图奇偶性相同。
        random.seed(QCursor.pos().x() ^ QCursor.pos().y())
        # eo_check 记录图片追加到最后 需要移动多少距离
        eo_check = 0
        for row in range(1,vcnt+1):
            for col in range(1, hcnt+1):
                if random.random() < 0.5:
                    eo_check += vcnt*hcnt - (vcnt*(row-1) + col)
                    self.puzzleWidget.takeItemInsert(row-1, col-1)

        # 共随机移动的距离奇偶校验
        if eo_check %2 != 0:
            eo_check += 1
            # 将倒数第二个格子和倒数第一个交换位置
            self.puzzleWidget.takeItemInsert(vcnt-1, hcnt-2)

        # 一切图片都到位后，设置好初始状态(只有靠近空格的图片才能动)
        specialCell = self.puzzleWidget.findChild(QListWidget, "cell_%d_%d" % (vcnt, hcnt))
        self.puzzleWidget.changeDragDropStatus(vcnt-1, hcnt-1, 1)
        
        #imageLabel = self.puzzleWidget.findChild(QLabel, "cell_0_4")
        #if imageLabel:
        #    imageLabel.setPixmap(self.puzzleImage.scaled(100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                                                    

    def setupMenus(self):
        fileMenu = self.menuBar().addMenu(QString(u"文件(&F)"))
        openAction = fileMenu.addAction(QString(u"打开(&O)..."))
        exitAction = fileMenu.addAction(QString(u"退出(&Q)"))
        gameMenu = self.menuBar().addMenu(QString(u"游戏(&G)"))
        restartAction = gameMenu.addAction(QString(u"重新开始(&R)"))

        self.connect(openAction, SIGNAL("triggered()"), self.openImage)
        self.connect(exitAction, SIGNAL("triggered()"), qApp, SLOT("quit()"))
        self.connect(restartAction, SIGNAL("triggered()"), self.setupPuzzle)    

    def setupWidgets(self):
        frame = QFrame()
        frameLayout = QHBoxLayout(frame)

        self.puzzleWidget = PuzzleWidget()
        self.connect(self.puzzleWidget, SIGNAL("puzzleCompleted()"),
                     self.setCompleted)

        frameLayout.addWidget(self.puzzleWidget)
        self.setCentralWidget(frame)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.openImage(QString(":7.jpg"))
    window.show()
    sys.exit(app.exec_())
