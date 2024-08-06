import sys
from PyQt5.QtWidgets import (
    QMainWindow, 
    QApplication,
    QGraphicsRectItem,
    QSpinBox,
    QSlider,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
    QLabel,
    QDialogButtonBox,
    QGraphicsView,
    QGraphicsScene,
    QAction, 
    QFileDialog,
    QToolBar,
    QPushButton,
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDateTimeEdit
    )
from PyQt5.QtGui import (
    QPen,
    QColor,
    QIcon,
    QKeySequence,
    QFont,
    QPainter
    
)
from PyQt5.QtCore import Qt, QRectF, QPointF,QSize
from tools import (
    set_select_tool,
    crop_image, zoom_in, 
    zoom_out, rotate_image, 
    load_image, default_image,
    adjust_brightness,
    adjust_contrast,
    save_image
)


class PatientInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patient Information")

        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.sex_input = QComboBox()
        self.sex_input.addItems(["Male", "Female", "Transgender"])
        self.dr_name_input = QLineEdit()
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        self.position_input = QComboBox()
        self.position_input.addItems(["Top Left", "Top Right", "Bottom Left", "Bottom Right"])

        self.form_layout.addRow("Patient Name:", self.name_input)
        self.form_layout.addRow("Age:", self.age_input)
        self.form_layout.addRow("Sex:", self.sex_input)
        self.form_layout.addRow("Dr Name:", self.dr_name_input)
        self.form_layout.addRow("Date & Time:", self.datetime_input)
        self.form_layout.addRow("Position:", self.position_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        # Add input validation
        self.name_input.textChanged.connect(self.validate_inputs)
        self.age_input.textChanged.connect(self.validate_inputs)
        self.sex_input.currentTextChanged.connect(self.validate_inputs)
        self.dr_name_input.textChanged.connect(self.validate_inputs)
        self.datetime_input.dateTimeChanged.connect(self.validate_inputs)
        self.position_input.currentTextChanged.connect(self.validate_inputs)

        # Add styles
        self.set_styles()


    def validate_inputs(self):
        if all([self.name_input.text(), self.age_input.text(), self.sex_input.currentText(),
                self.dr_name_input.text(), self.datetime_input.dateTime(), self.position_input.currentText()]):
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
    def set_styles(self):
        self.setStyleSheet("""
            QLineEdit, QComboBox, QDateTimeEdit {
                border: 2px solid gray;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
            }
            QLineEdit:hover, QComboBox:hover, QDateTimeEdit:hover {
                border: 2px solid blue;
            }
            QComboBox {
                padding-left: 7px;
            }
        """)


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Editor")
        self.setGeometry(0, 0, QApplication.primaryScreen().availableGeometry().width(),
                         QApplication.primaryScreen().availableGeometry().height())

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.original_image = None
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
    def open_patient_info_dialog(self):
        dialog = PatientInfoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.name_input.text()
            age = dialog.age_input.text()
            sex = dialog.sex_input.currentText()
            dr_name = dialog.dr_name_input.text()
            datetime = dialog.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            position = dialog.position_input.currentText()
            
            self.add_patient_info(name, age, sex, dr_name, datetime, position)

    def add_patient_info(self, name, age, sex, dr_name, datetime, position):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(255, 0, 0))
        painter.setFont(QFont('Arial', 12))
        rect_top_left = QRectF(10, 30, self.pixmap.width() - 20, self.pixmap.height() - 60)
        rect_top_right = QRectF(self.pixmap.width() - 210, 30, 200, self.pixmap.height() - 60)
        rect_bottom_left = QRectF(10, self.pixmap.height() - 130, self.pixmap.width() - 20, 100)
        rect_bottom_right = QRectF(self.pixmap.width() - 210, self.pixmap.height() - 130, 200, 100)

        text = f"Patient Name: {name}\nAge: {age}\nSex: {sex}\nDr Name: {dr_name}\nDate & Time: {datetime}"

        if position == "Top Left":
            painter.drawText(rect_top_left, Qt.TextWordWrap, text)
        elif position == "Top Right":
            painter.drawText(rect_top_right, Qt.TextWordWrap, text)
        elif position == "Bottom Left":
            painter.drawText(rect_bottom_left, Qt.TextWordWrap, text)
        elif position == "Bottom Right":
            painter.drawText(rect_bottom_right, Qt.TextWordWrap, text)


        painter.end()
        self.scene.clear()
        self.image_item = self.scene.addPixmap(self.pixmap)
        self.scene.setSceneRect(QRectF(self.pixmap.rect()))


    def create_menu(self):
        load_action = QAction("&Load Image", self)
        load_action.triggered.connect(self.load_image)

        save_action = QAction("&Save Image", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_image)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        menubar.setFixedHeight(40)  # Set the height of the menu bar
        menubar.setStyleSheet("QMenuBar { background-color: #0078d7; color: white; font-size:20px;}"
                              "QMenuBar::item { background-color: #0078d7; color: white;  font-size:20px;}"
                              "QMenuBar::item:selected { background-color: #005bb5;font-size:20px; }")

        export_button = QPushButton("Export")
        export_button.setIcon(QIcon("assets/save.png"))  # Replace with your icon path
        export_button.setStyleSheet("QPushButton { background-color: #0078d7; color: white; border: none; padding: 5px 10px; font-size: 14px; }")
        export_button.clicked.connect(self.save_image)

        # Create a QWidgetAction for the export button
        export_action = QWidgetAction(menubar)
        export_action.setDefaultWidget(export_button)

        # Add the export button to the menu bar
        menubar.addAction(export_action)





    def create_toolbox(self):
        toolbox = QToolBar("Tools", self)
        toolbox.setFixedWidth(250)
        self.addToolBar(Qt.LeftToolBarArea, toolbox)

        title_label = QLabel("    Adjust Image \n")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))  # Set font size and style
        toolbox.addWidget(title_label)


        select_tool = QPushButton("  Select Tool")
        icon = QIcon("assets/select.png")
        select_tool.setIcon(icon)
        select_tool.setIconSize(QSize(30,30))
        select_tool.setStyleSheet(
            "QPushButton { background-color:none; color: black; \
             padding: 5px 5px; margin: 5px 5px; font-size: 18px; }"      
            )
        select_tool.clicked.connect(self.set_select_tool)
        toolbox.addWidget(select_tool)

        crop_tool = QPushButton("  Crop Tool")
        crop_tool.setStyleSheet(
             "QPushButton { background-color:none; color: black; \
             padding: 5px 5px; margin: 5px 5px; font-size: 18px; }"         
            )
        icon = QIcon("assets/crop.png")
        crop_tool.setIcon(icon)
        crop_tool.setIconSize(QSize(30,30))
        crop_tool.clicked.connect(self.crop_image)
        toolbox.addWidget(crop_tool)

        zoom_in_tool = QPushButton("  Zoom In")
        icon = QIcon("assets/zoomin.png")
        zoom_in_tool.setIcon(icon)
        zoom_in_tool.setStyleSheet(
             "QPushButton { background-color:none; color: black; \
             padding: 5px 5px; margin: 5px 5px; font-size: 18px; }"      
        )
        zoom_in_tool.setIconSize(QSize(30,30))
        zoom_in_tool.clicked.connect(self.zoom_in)
        toolbox.addWidget(zoom_in_tool)

        zoom_out_tool = QPushButton("  Zoom Out")
        icon = QIcon("assets/zoomout.png")
        zoom_out_tool.setIcon(icon)
        zoom_out_tool.setStyleSheet(
            "QPushButton { background-color:none; color: black; \
             padding: 5px 5px; margin: 5px 5px; font-size: 18px; }"
        )
        zoom_out_tool.setIconSize(QSize(30,30))
        zoom_out_tool.clicked.connect(self.zoom_out)
        toolbox.addWidget(zoom_out_tool)

        rotate_tool = QPushButton("  Rotate")
        icon = QIcon("assets/rotate.png")
        rotate_tool.setIcon(icon)
        rotate_tool.setIconSize(QSize(30,30))
        rotate_tool.setStyleSheet(
            "QPushButton { background-color:none; color: black; \
             padding: 5px 5px; margin: 5px 5px; font-size: 18px; }"
        )
        rotate_tool.clicked.connect(self.rotate_image)
        toolbox.addWidget(rotate_tool)
        
        addinfo = QPushButton("  Insert patient Info")
        icon = QIcon("assets/medical.png")
        addinfo.setIcon(icon)
        addinfo.setIconSize(QSize(30,30))
        addinfo.setStyleSheet(
            "QPushButton { background-color:none; color: black; \
             padding: 5px 5px; margin: 5px 5px; font-size: 18px; }"
        )
        addinfo.clicked.connect(self.open_patient_info_dialog)
        toolbox.addWidget(addinfo)
        
        slider_layout = QVBoxLayout()
        slider_widget = QWidget()
        slider_widget.setLayout(slider_layout)
        
        brightness_slider = QSlider(Qt.Horizontal)
        brightness_slider.setRange(-100, 100)
        brightness_slider.setValue(0)
        brightness_slider.valueChanged.connect(self.adjust_brightness)
        brightness_slider.valueChanged.connect(self.update_brightness_label)
        slider_layout.addWidget(brightness_slider)

        self.brightness_label = QLabel("Brightness: 0")
        slider_layout.addWidget(self.brightness_label)
        self.brightness_label.setStyleSheet(
            "QLabel {font-size: 15px; }"
        )

        toolbox.addWidget(slider_widget)
        
        
        
        
        contrast_slider_layout = QVBoxLayout()
        contrast_slider_widget = QWidget()
        contrast_slider_widget.setLayout(contrast_slider_layout)

        contrast_slider = QSlider(Qt.Horizontal)
        contrast_slider.setRange(-100, 100)
        contrast_slider.setValue(0)
  
        contrast_slider.valueChanged.connect(self.adjust_contrast)
        contrast_slider.valueChanged.connect(self.update_contrast_label)
        contrast_slider_layout.addWidget(contrast_slider)

        self.contrast_label = QLabel("Contrast: 0")
        self.contrast_label.setStyleSheet(
            "QLabel {font-size: 15px; }"
        )
        contrast_slider_layout.addWidget(self.contrast_label)

        toolbox.addWidget(contrast_slider_widget)



    def set_select_tool(self):
        set_select_tool(self)
        
    def update_brightness_label(self, value):
        self.brightness_label.setText(f"Brightness: {value}")

    def save_image(self):
        save_image(self)

    def crop_image(self):
        crop_image(self)

    def zoom_in(self):
        zoom_in(self)

    def zoom_out(self):
        zoom_out(self)

    def rotate_image(self):
        rotate_image(self)

    def load_image(self):
        load_image(self)
    def adjust_brightness(self, value):
        adjust_brightness(self, value)
    
    def adjust_contrast(self, value):
        adjust_contrast(self, value)
        

    def update_contrast_label(self, value):
        self.contrast_label.setText(f"Contrast: {value}")








    def default_image(self, imagepatj):
        default_image(self, imagepatj)

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
