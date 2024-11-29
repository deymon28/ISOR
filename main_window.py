'''
Основний файл графічного інтерфейсу програми
'''

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QFrame, QTextEdit, QSizePolicy
from PyQt5.QtCore import Qt, QPoint, QCoreApplication
from PyQt5.QtGui import QPixmap, QImage, QPainter
import sys
import json
import os
import subprocess
from controls import FormControls

class YOLOProcessorApp(QFrame):
    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('YOLO Image Processor GUI')
        self.resize(1200, 800)
        self.center()

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.show_form_controls()

    def show_form_controls(self):
        # Clear the existing widgets from the main layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                del item

        self.setStyleSheet("background-color: white;")

        self.form_controls = FormControls(self)
        form_frame = self.form_controls.get_form_frame()
        self.main_layout.addWidget(form_frame, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

    def start_processing(self):
        # Get values from the UI
        yolo_model_path = self.form_controls.model_path_entry.text()
        image_path = self.form_controls.image_path_entry.text()
        detection_threshold = self.form_controls.threshold_entry.text()
        tile_size = self.form_controls.tile_size_entry.text()
        model_imgsz = self.form_controls.model_imgsz_entry.text()

        if not yolo_model_path or not image_path:
            QMessageBox.critical(self, "Input Error", "Please provide paths for the model and image.")
            return

        # Prepare configuration
        config = {
            "yolo_model_path": yolo_model_path,
            "image_path": image_path,
            "output_path": "output.png",
            "detection_threshold": float(detection_threshold),
            "tile_size": int(tile_size),
            "model_imgsz": int(model_imgsz)
        }

        # Save configuration to JSON file
        config_path = "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Start process.py with config
        self.form_controls.progress_label.setVisible(True)
        QApplication.processEvents()

        try:
            subprocess.run(["python", "process.py", config_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.show_results_ui(config["output_path"])
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Processing Error", f"An error occurred during processing: {e}")
        finally:
            self.form_controls.progress_label.setVisible(False)

    def show_results_ui(self, output_path):
        # Clear the existing widgets from the main layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                del item

        self.setStyleSheet("background-color: white;")

        results_layout = QHBoxLayout()

        # Left Frame for information and buttons
        left_layout = QVBoxLayout()
        left_frame = QFrame(self)
        left_frame.setLayout(left_layout)
        left_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        left_frame.setMaximumWidth(300)  # Set maximum width to avoid excessive enlargement
        results_layout.addWidget(left_frame)

        result_label = QLabel('Detected Objects Information:')
        left_layout.addWidget(result_label)

        info_path = os.path.splitext(output_path)[0] + "_info.txt"
        detected_info = ""
        if os.path.exists(info_path) and os.path.getsize(info_path) > 0:
            with open(info_path, 'r') as f:
                detected_info = f.read()
        else:
            detected_info = "No detection information available."

        detected_text = QTextEdit()
        detected_text.setText(detected_info)
        detected_text.setReadOnly(True)
        left_layout.addWidget(detected_text)

        # Save Button
        save_button = QPushButton('Save Results', self)
        save_button.clicked.connect(lambda: self.save_results(output_path, detected_info))
        save_button.setStyleSheet("padding: 10px; background-color: #5bc0de; color: white; border-radius: 5px;")
        left_layout.addWidget(save_button)

        # Restart Button
        restart_button = QPushButton('+ Restart', self)
        restart_button.clicked.connect(self.restart_application)
        restart_button.setStyleSheet("padding: 10px; background-color: #d9534f; color: white; border-radius: 5px;")
        left_layout.addWidget(restart_button)

        # Right Frame for displaying the image
        right_layout = QVBoxLayout()
        right_frame = QFrame(self)
        right_frame.setLayout(right_layout)
        right_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_layout.addWidget(right_frame)

        zoomable_image = ZoomableImage(right_frame, output_path)
        right_layout.addWidget(zoomable_image)

        self.main_layout.addLayout(results_layout)

    def save_results(self, output_path, detected_info):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Processed Image", "", "PNG Files (*.png);;All Files (*)", options=options)
        if save_path:

            pixmap = QPixmap(output_path)
            pixmap.save(save_path)

            txt_path = os.path.splitext(save_path)[0] + "_info.txt"
            with open(txt_path, 'w') as txt_file:
                txt_file.write(detected_info)

            QMessageBox.information(self, "Save Successful", "Results saved successfully.")

    # def restart_application(self):
    #     # Restart the entire application by quitting and re-executing
    #     QCoreApplication.quit()
    #     os.execv(sys.executable, [sys.executable] + sys.argv)
    def restart_application(self):
        python_path = r"C:\Program Files\Python312\python.exe"

        if not os.path.exists(python_path):
            QMessageBox.critical(self, "Restart Error", f"Python executable not found: {python_path}")
            return

        try:
            QCoreApplication.quit()
            os.execv(python_path, [python_path] + sys.argv)
        except Exception as e:
            QMessageBox.critical(self, "Restart Error", f"Failed to restart the application: {e}")


class ZoomableImage(QLabel):
    def __init__(self, parent, img_path):
        super().__init__(parent)
        self.img = QImage(img_path)
        self.pixmap = QPixmap.fromImage(self.img)
        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignCenter)
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        cursor_pos = event.pos()
        old_x = cursor_pos.x() - self.offset.x()
        old_y = cursor_pos.y() - self.offset.y()

        if event.angleDelta().y() > 0:
            factor = 1.1
        else:
            factor = 0.9

        self.scale_factor *= factor
        new_width = self.pixmap.width() * self.scale_factor
        new_height = self.pixmap.height() * self.scale_factor

        new_x = old_x * (factor - 1)
        new_y = old_y * (factor - 1)
        self.offset -= QPoint(int(new_x), int(new_y))

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.offset)
        scaled_pixmap = self.pixmap.scaled(int(self.pixmap.width() * self.scale_factor),
                                           int(self.pixmap.height() * self.scale_factor),
                                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YOLOProcessorApp()
    ex.show()
    sys.exit(app.exec_())
