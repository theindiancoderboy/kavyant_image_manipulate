import sys
from PyQt5.QtWidgets import QApplication
from image_editor import ImageEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.showMaximized()
    sys.exit(app.exec_())
