import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QRectF

def set_select_tool(editor):
    editor.current_tool = 'select'

def crop_image(editor):
    if editor.rect_item and editor.current_tool == 'select':
        rect = editor.rect_item.rect()
        cropped = editor.pixmap.copy(rect.toRect())
        editor.scene.clear()
        editor.pixmap = cropped
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None

def zoom_in(editor):
    editor.view.scale(1.2, 1.2)

def zoom_out(editor):
    editor.view.scale(0.8, 0.8)

def rotate_image(editor):
    if hasattr(editor, 'pixmap') and editor.pixmap:
        transform = QTransform().rotate(90)  # Rotate 90 degrees clockwise
        editor.pixmap = editor.pixmap.transformed(transform, Qt.SmoothTransformation)
        editor.scene.clear()
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None

def load_image(editor):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(editor, "Load Image", "", 
        "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif);;All Files (*)", 
        options=options)
    if file_path:
        editor.scene.clear()
        editor.pixmap = QPixmap(file_path)
        editor.original_image = cv2.imread(file_path)  # Store the original image as a NumPy array
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None

def default_image(editor, imagepath):
    if imagepath:
        editor.scene.clear()
        editor.pixmap = QPixmap(imagepath)
        editor.original_image = cv2.imread(imagepath)  # Store the original image as a NumPy array
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None

def adjust_brightness(editor, value):
    if editor.original_image is not None:
        factor = (value + 100) / 100  # Range from 0 (completely dark) to 2 (completely bright)
        hsv = cv2.cvtColor(editor.original_image, cv2.COLOR_BGR2HSV)
        hsv[..., 2] = cv2.multiply(hsv[..., 2], factor)
        bright_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        height, width, channel = bright_image.shape
        bytes_per_line = 3 * width
        qimage = QImage(bright_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        editor.pixmap = QPixmap.fromImage(qimage)
        editor.scene.clear()
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None
