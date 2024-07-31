import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage,QTransform
from PyQt5.QtWidgets import QFileDialog
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
def save_image(editor):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(editor, "Save Image", "", 
        "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif);;All Files (*)", 
        options=options)
    if file_path:
        editor.pixmap.save(file_path)

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
        # Ensure that value is in the range [-100, 100]
        value = np.clip(value, -100, 100)

        # Convert the original image to float32 for processing
        bright_image = editor.original_image.astype(np.float32)

        # Adjust brightness
        factor = 1.0 + value / 100.0
        bright_image = cv2.convertScaleAbs(bright_image * factor)

        # Convert back to QImage for display
        height, width, channel = bright_image.shape
        bytes_per_line = 3 * width
        bright_image = cv2.cvtColor(bright_image, cv2.COLOR_BGR2RGB)

        qimage = QImage(bright_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        editor.pixmap = QPixmap.fromImage(qimage)
        editor.scene.clear()
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None


def adjust_contrast(editor, value):
    if editor.original_image is not None:
        # Ensure that value is in the range [-100, 100]
        value = np.clip(value, -100, 100)

        # Convert the original image to float32 for processing
        contrast_image = editor.original_image.astype(np.float32)

        # Adjust contrast
        factor = 1.0 + value / 100.0
        mean = np.mean(contrast_image)
        contrast_image = cv2.convertScaleAbs((contrast_image - mean) * factor + mean)

        # Convert back to QImage for display
        height, width, channel = contrast_image.shape
        bytes_per_line = 3 * width
        contrast_image = cv2.cvtColor(contrast_image, cv2.COLOR_BGR2RGB)
        qimage = QImage(contrast_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        editor.pixmap = QPixmap.fromImage(qimage)
        editor.scene.clear()
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None
