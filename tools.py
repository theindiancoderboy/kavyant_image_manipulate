from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import (
    QPixmap, QTransform, QColor, QPen,
)
from PyQt5.QtCore import QRectF,Qt

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
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None

def default_image(editor, imagepatj):
    if imagepatj:
        editor.scene.clear()
        editor.pixmap = QPixmap(imagepatj)
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None
