'''
Файл стилів графічного інтерфейсу програми
'''


import os
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QFrame, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

class FormControls:
    def __init__(self, parent):
        self.parent = parent
        self.init_controls()

    def init_controls(self):
        self.form_frame = QFrame(self.parent)
        self.form_layout = QVBoxLayout()
        self.form_frame.setLayout(self.form_layout)
        self.form_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.form_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.form_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f7f7f7;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #dcdcdc;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
            QLineEdit {
                border: 2px solid #5bc0de;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0275d8;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #025aa5;
            }
            """
        )

        self.model_path_label = QLabel('YOLO Model Path:')
        self.form_layout.addWidget(self.model_path_label, alignment=Qt.AlignCenter)

        model_layout = QHBoxLayout()
        model_layout.setAlignment(Qt.AlignCenter)
        self.model_path_entry = QLineEdit(self.parent)
        self.model_path_entry.setMaximumWidth(250)
        model_layout.addWidget(self.model_path_entry)

        self.model_path_button = QPushButton('Browse', self.parent)
        self.model_path_button.setMaximumWidth(100)
        self.model_path_button.clicked.connect(self.browse_model_path)
        model_layout.addWidget(self.model_path_button)
        self.form_layout.addLayout(model_layout)

        self.image_path_label = QLabel('Image Path:')
        self.form_layout.addWidget(self.image_path_label, alignment=Qt.AlignCenter)

        image_layout = QHBoxLayout()
        image_layout.setAlignment(Qt.AlignCenter)
        self.image_path_entry = QLineEdit(self.parent)
        self.image_path_entry.setMaximumWidth(250)
        image_layout.addWidget(self.image_path_entry)

        self.image_path_button = QPushButton('Browse', self.parent)
        self.image_path_button.setMaximumWidth(100)
        self.image_path_button.clicked.connect(self.browse_image_path)
        image_layout.addWidget(self.image_path_button)
        self.form_layout.addLayout(image_layout)

        self.threshold_label = QLabel('Detection Threshold:')
        self.form_layout.addWidget(self.threshold_label, alignment=Qt.AlignCenter)

        self.threshold_entry = QLineEdit(self.parent)
        self.threshold_entry.setMaximumWidth(150)
        self.threshold_entry.setText("0.5")
        self.form_layout.addWidget(self.threshold_entry, alignment=Qt.AlignCenter)

        self.tile_size_label = QLabel('Tile Size:')
        self.form_layout.addWidget(self.tile_size_label, alignment=Qt.AlignCenter)

        self.tile_size_entry = QLineEdit(self.parent)
        self.tile_size_entry.setMaximumWidth(150)
        self.tile_size_entry.setText("4096")
        self.form_layout.addWidget(self.tile_size_entry, alignment=Qt.AlignCenter)

        self.model_imgsz_label = QLabel('Model Image Size:')
        self.form_layout.addWidget(self.model_imgsz_label, alignment=Qt.AlignCenter)

        self.model_imgsz_entry = QLineEdit(self.parent)
        self.model_imgsz_entry.setMaximumWidth(150)
        self.model_imgsz_entry.setText("2048")
        self.form_layout.addWidget(self.model_imgsz_entry, alignment=Qt.AlignCenter)

        self.start_button = QPushButton('Start Processing', self.parent)
        self.start_button.setMaximumWidth(200)
        self.start_button.clicked.connect(self.parent.start_processing)
        self.form_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.progress_label = QLabel('Processing...', self.parent)
        self.progress_label.setStyleSheet("font-size: 14px; color: #ff0000;")
        self.progress_label.setVisible(False)
        self.form_layout.addWidget(self.progress_label, alignment=Qt.AlignCenter)

    def browse_model_path(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Select YOLO Model", "", "YOLO Model Files (*.pt)", options=options)
        if file_path:
            self.model_path_entry.setText(os.path.normpath(file_path))

    def browse_image_path(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Select Image", "", "Image Files (*.jpg *.jpeg *.png *.tif)", options=options)
        if file_path:
            self.image_path_entry.setText(os.path.normpath(file_path))

    def get_form_frame(self):
        return self.form_frame
