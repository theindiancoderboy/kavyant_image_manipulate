import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage, QTransform
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QRectF, Qt
from PIL import Image
import configparser
import os
import subprocess
def save_state(editor, original=False):
    # Save the current pixmap as a state before any changes
    # print("new event added")
    
    if original:
        pass
        # bright_image = editor.original_image.astype(np.float32)
        # height, width, channel = bright_image.shape
        # bytes_per_line = 3 * width
        # bright_image = cv2.cvtColor(bright_image, cv2.COLOR_BGR2RGB)
        # bright_image = cv2.cvtColor(bright_image, cv2.COLOR_RGB2BGR)

        # qimage = QImage(bright_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # pixmap = QPixmap.fromImage(qimage)
        # editor.undo_stack.append(pixmap.copy())
    if editor.pixmap:
        editor.undo_stack.append(editor.pixmap.copy())
    # print(editor.undo_stack)
    # Limit the undo stack to the last 3 states
    if len(editor.undo_stack) > 3:
        editor.undo_stack.pop(0)

def set_select_tool(editor):
    save_state(editor)  # Save current state before changing tool
    editor.current_tool = 'select'

def crop_image(editor):
    if editor.rect_item and editor.current_tool == 'select':
        save_state(editor)  # Save current state before cropping
        rect = editor.rect_item.rect()
        cropped = editor.pixmap.copy(rect.toRect())
        editor.scene.clear()
        editor.pixmap = cropped
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None
        image=editor.pixmap.toImage()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        width = image.width()
        height = image.height()
        arr = np.array(ptr).reshape(height, width, 4)

        pil_image = Image.fromarray(arr, 'RGBA')
        cv2_image = np.array(pil_image)

        # Convert RGB to BGR
        # cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)

        editor.original_image=cv2_image

def undo_change(editor):
    # print(editor.undo_stack)
    if editor.undo_stack:
        # Restore the last state from the undo stack
        editor.redo_stack.append(editor.pixmap.copy())
        editor.pixmap = editor.undo_stack.pop()
        editor.scene.clear()
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        image=editor.pixmap.toImage()
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        pil_image = Image.fromarray(arr, 'RGBA')
        cv2_image = np.array(pil_image)
        
        editor.original_image=cv2_image

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
    
def read_config():
    pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures")
    config = configparser.ConfigParser()
    try:
        command = "wmic cpu get ProcessorId"
        result = subprocess.check_output(command, shell=True)
        licnese_key= result.decode().strip().split("\n")[1].strip()
    except:
        licnese_key=os.urandom(10).hex()
    # Set default values
    config['Settings'] = {
        'default_load_image_path': pictures_folder,
        'license_key': licnese_key
    }
    
    # Write the configuration to a file
    with open("config.ini", 'w') as configfile:
        config.write(configfile)

    configa = configparser.ConfigParser()
    configa.read("config.ini")

    default_load_image_path = configa.get('Settings', 'default_load_image_path')
    license_key = configa.get('Settings', 'license_key')

    return default_load_image_path, license_key
def rotate_image(editor):
    if hasattr(editor, 'pixmap') and editor.pixmap:
        if editor.brightnesslevel !=0:
            # print("saving bright image")
            editor.brightnesslevel=0
            update_original_image(editor)
        save_state(editor)  # Save current state before rotating
        transform = QTransform().rotate(90)  # Rotate 90 degrees clockwise
        editor.pixmap = editor.pixmap.transformed(transform, Qt.SmoothTransformation)
        editor.scene.clear()
        editor.image_item = editor.scene.addPixmap(editor.pixmap)
        editor.scene.setSceneRect(QRectF(editor.pixmap.rect()))
        editor.rect_item = None
        image=editor.pixmap.toImage()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        width = image.width()
        height = image.height()
        arr = np.array(ptr).reshape(height, width, 4)
        
        pil_image = Image.fromarray(arr, 'RGBA')
        cv2_image = np.array(pil_image)

        # Convert RGB to BGR

        editor.original_image=cv2_image


def load_image(editor):
    options = QFileDialog.Options()
    filepath, lc_key= read_config()
    file_path, _ = QFileDialog.getOpenFileName(editor, "Load Image", filepath, 
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
        
        # save_state(editor)  # Save current state before adjusting brightness
        # Ensure that value is in the range [-100, 100]
        value = np.clip(value, -100, 100)

        # Convert the original image to float32 for processing
        bright_image = editor.original_image.astype(np.float32)

        # Adjust brightness
        factor = 1.0 + value / 100.0
        bright_image = cv2.convertScaleAbs(bright_image * factor)
        editor.brightnesslevel=value
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

def update_original_image(editor):
    save_state(editor,True)
    editor.update_brightness_label(editor.brightnesslevel)

def adjust_contrast(editor, value):
    
    if editor.original_image is not None:
        save_state(editor)  # Save current state before adjusting contrast
        # Ensure that value is in the range [-100, 100]
        value = np.clip(value, -100, 100)
        if editor.brightnesslevel !=0:
            editor.brightnesslevel=0
            update_original_image(editor)
            
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

