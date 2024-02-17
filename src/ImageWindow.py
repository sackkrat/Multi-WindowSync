import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ImageWindow(QMainWindow):
    imageMoved = pyqtSignal(QPoint)
    windowClosing = pyqtSignal(object)

    def __init__(self, parent=None, imagePath=None):
        super().__init__(parent)
        self.initUI()
        self.initSettings(imagePath)
        
    def setMoveWithWindow(self, state):
        self.moveWithWindow = state    

    def setKeepCentered(self, state):
        self.keepCentered = state        
    
    def initUI(self):
        screen = QApplication.primaryScreen().size()
        screenWidth = screen.width()
        screenHeight = screen.height()
        
        self.setGeometry(random.randint(screenWidth//4, screenWidth//2),
                         random.randint(0, screenHeight//2),
                         int(screenWidth//2.5), int(screenHeight//2))
        
        self.setWindowIcon(QIcon('Files/logo.png'))
        self.setWindowTitle('Image Window')
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(self.rect())
    
    def initSettings(self, imagePath):
        self.currentImagePath = imagePath
        self.movie = None
        
        self.moveWithWindow = False
        self.keepCentered = False
        
        if imagePath:
            self.loadImage(imagePath, 1)        
        self.updateFunction(1)
        
    def updateFunction(self, timeStep):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateImagePosition)
        self.timer.start(timeStep)    
        self.isImageMoved = False

    def moveEvent(self, event):
        if not self.moveWithWindow:
            return
        super().moveEvent(event)
        if self.currentImagePath:
            globalPos = self.mapToGlobal(self.imageLabel.pos())
            self.imageMoved.emit(globalPos)
            self.isImageMoved = True

    def loadImage(self, imagePath, scaleFactor):
        self.currentImagePath = imagePath
        if imagePath.lower().endswith('.gif'): 
            self.movie = QMovie(imagePath)
            self.movie.setScaledSize(self.imageLabel.size() * scaleFactor)             
            self.imageLabel.setMovie(self.movie)
            self.movie.start()  
            self.initScale = self.imageLabel.size()
        else:
            self.movie = None
            pixmap = QPixmap(imagePath)
            if not pixmap.isNull(): 
                scaledPixmap = pixmap.scaled(self.size() * scaleFactor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imageLabel.setPixmap(scaledPixmap)
            self.initScale = self.size()

    def centerImage(self):
        if self.movie: 
            rect = QRect(0, 0, self.movie.scaledSize().width(), self.movie.scaledSize().height())
        elif self.imageLabel.pixmap() and not self.imageLabel.pixmap().isNull():
            pixmap = self.imageLabel.pixmap()
            rect = pixmap.rect()
        else:
            return 

        rect.moveCenter(self.rect().center())
        self.imageLabel.setGeometry(rect)
    
    def updateImagePosition(self): 
        if self.isImageMoved:
            return

        if self.currentImagePath:
            activeWindow = QApplication.activeWindow()

            if self == activeWindow and self.keepCentered:
                self.centerImage()
                return

            if self.parent().imageWindows:
                if isinstance(activeWindow, ImageWindow) and self.keepCentered: 
                    refWindow = activeWindow
                else:
                    refWindow = self.parent().imageWindows[0]
                globalPos = refWindow.mapToGlobal(refWindow.imageLabel.pos())
                localPos = self.mapFromGlobal(globalPos)
                self.imageLabel.move(localPos)
                self.update()
        
                
    def restartGif(self):
        if self.currentImagePath and self.currentImagePath.lower().endswith('.gif'):
            if self.movie:
                self.movie.stop()
                self.movie.start()
                
    def setScale(self, scaleFactor):
        if self.movie and self.initScale:
            newSize = self.initScale * scaleFactor
            self.movie.setScaledSize(newSize)
        elif self.imageLabel.pixmap() and not self.imageLabel.pixmap().isNull() and self.initScale:
            newSize = self.initScale * scaleFactor
            scaledPixmap = QPixmap(self.currentImagePath).scaled(newSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imageLabel.setPixmap(scaledPixmap)
        self.imageLabel.setFixedSize(newSize)
        self.imageLabel.adjustSize()
        
    def closeEvent(self, event):
        self.windowClosing.emit(self) 
        super().closeEvent(event)