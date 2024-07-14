import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, 
    QGraphicsScene, QGraphicsRectItem, QAction, QFileDialog, QToolBar, QPushButton
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QTransform, QIcon
from PyQt5.QtCore import Qt, QRectF, QPointF

class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Editor")
        self.setGeometry(0, 0, QApplication.primaryScreen().availableGeometry().width(),
                         QApplication.primaryScreen().availableGeometry().height())

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.rect_item = None
        self.start_pos = QPointF()
        self.end_pos = QPointF()
        self.current_tool = 'select'
        self.selecting = False

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

        self.create_menu()
        self.create_toolbox()
        self.default_image("default.jpg")

    def create_menu(self):
        load_action = QAction("&Load Image", self)
        load_action.triggered.connect(self.load_image)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(load_action)

    def create_toolbox(self):
        toolbox = QToolBar("Tools", self)
        self.addToolBar(Qt.RightToolBarArea, toolbox)

        select_tool = QPushButton("Select")
        icon =QIcon("assets/select.png")
        select_tool.setIcon(icon)    
        # select_tool.setFixedSize(50,50)
        # select_tool.size()    
        # select_tool.setIconSize(icon.actualSize(icon.availableSizes()[0]))
        # select_tool.setStyleSheet('QPushButton { background-color: #4CAF50; color: white; border: 2px solid #4CAF50; border-radius: 4px; }')
        select_tool.clicked.connect(self.set_select_tool)
        toolbox.addWidget(select_tool)

        crop_tool = QPushButton("Crop")
        icon = QIcon("assets/crop.png")
        crop_tool.setIcon(icon)
        crop_tool.clicked.connect(self.crop_image)
        toolbox.addWidget(crop_tool)

        zoom_in_tool = QPushButton("Zoom In")
        icon = QIcon("assets/zoomin.png")
        zoom_in_tool.setIcon(icon)
        zoom_in_tool.clicked.connect(self.zoom_in)
        toolbox.addWidget(zoom_in_tool)

        zoom_out_tool = QPushButton("Zoom Out")
        icon = QIcon("assets/zoomout.png")
        zoom_out_tool.setIcon(icon)
        zoom_out_tool.clicked.connect(self.zoom_out)
        toolbox.addWidget(zoom_out_tool)
        
        rotate_tool = QPushButton("Rotate")
        icon = QIcon("assets/rotate.png")
        rotate_tool.setIcon(icon)
        rotate_tool.clicked.connect(self.rotate_image)
        toolbox.addWidget(rotate_tool)

    def set_select_tool(self):
        self.current_tool = 'select'

    def crop_image(self):
        if self.rect_item and self.current_tool == 'select':
            rect = self.rect_item.rect()
            cropped = self.pixmap.copy(rect.toRect())
            self.scene.clear()
            self.pixmap = cropped
            self.image_item = self.scene.addPixmap(self.pixmap)
            self.scene.setSceneRect(QRectF(self.pixmap.rect()))
            self.rect_item = None

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(0.8, 0.8)

    def rotate_image(self):
        if hasattr(self, 'pixmap') and self.pixmap:
            transform = QTransform().rotate(90)  # Rotate 90 degrees clockwise
            self.pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
            self.scene.clear()
            self.image_item = self.scene.addPixmap(self.pixmap)
            self.scene.setSceneRect(QRectF(self.pixmap.rect()))
            self.rect_item = None

    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Image", "", 
            "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif);;All Files (*)", 
            options=options)
        if file_path:
            self.scene.clear()
            self.pixmap = QPixmap(file_path)
            self.image_item = self.scene.addPixmap(self.pixmap)
            self.scene.setSceneRect(QRectF(self.pixmap.rect()))
            self.rect_item = None
    def default_image(self, imagepatj):
        
        if imagepatj:
            self.scene.clear()
            self.pixmap = QPixmap(imagepatj)
            self.image_item = self.scene.addPixmap(self.pixmap)
            self.scene.setSceneRect(QRectF(self.pixmap.rect()))
            self.rect_item = None

    def eventFilter(self, source, event):
        if self.current_tool == 'select':
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                self.start_pos = self.view.mapToScene(event.pos())
                if self.rect_item:
                    self.scene.removeItem(self.rect_item)
                self.rect_item = QGraphicsRectItem()
                self.rect_item.setPen(QPen(QColor("red"), 2))
                self.scene.addItem(self.rect_item)
                self.selecting = True

            elif event.type() == event.MouseMove and self.selecting:
                self.end_pos = self.view.mapToScene(event.pos())
                self.rect_item.setRect(QRectF(self.start_pos, self.end_pos).normalized())

            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.end_pos = self.view.mapToScene(event.pos())
                self.rect_item.setRect(QRectF(self.start_pos, self.end_pos).normalized())
                self.selecting = False

        return super().eventFilter(source, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.showMaximized()
    sys.exit(app.exec_())
 