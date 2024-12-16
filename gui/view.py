from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Signal, Qt
import numpy as np

def numpy_to_qimage(image_array: np.ndarray) -> QImage:
    # image_array: H x W x 3 (RGB)
    h, w, ch = image_array.shape
    bytes_per_line = ch * w
    qimg = QImage((image_array * 255.0).astype(np.uint8).data, w, h, bytes_per_line, QImage.Format_RGB888)
    return qimg.copy()

class GeneticView(QWidget):
    # Signals for controller
    pauseClicked = Signal(bool)    # Emitted with True for pause, False for resume
    startClicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Genetic Algorithm GUI")

        # Create layout
        main_layout = QVBoxLayout(self)

        # Top row: reference image and control buttons
        top_row = QHBoxLayout()
        self.reference_label = QLabel("Reference Image")
        self.reference_label.setAlignment(Qt.AlignCenter)
        top_row.addWidget(self.reference_label)

        button_layout = QVBoxLayout()
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.pause_state = False

        self.start_button.clicked.connect(self.startClicked)
        
        def on_pause():
            self.pause_state = not self.pause_state
            self.pause_button.setText("Resume" if self.pause_state else "Pause")
            self.pauseClicked.emit(self.pause_state)
        
        self.pause_button.clicked.connect(on_pause)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)

        top_row.addLayout(button_layout)
        main_layout.addLayout(top_row)

        # Middle row: display best fitness and images
        middle_row = QHBoxLayout()

        # Show best fitness
        fitness_layout = QVBoxLayout()
        self.best_fitness_label = QLabel("Best Fitness Ever: N/A")
        self.current_best_fitness_label = QLabel("Current Gen Best: N/A")
        fitness_layout.addWidget(self.best_fitness_label)
        fitness_layout.addWidget(self.current_best_fitness_label)
        middle_row.addLayout(fitness_layout)

        # Show best-ever image
        self.best_image_label = QLabel("Best Image Ever")
        self.best_image_label.setAlignment(Qt.AlignCenter)
        middle_row.addWidget(self.best_image_label)

        # Show current generation best image
        self.current_best_label = QLabel("Current Gen Best")
        self.current_best_label.setAlignment(Qt.AlignCenter)
        middle_row.addWidget(self.current_best_label)

        main_layout.addLayout(middle_row)

        self.setLayout(main_layout)

    def update_reference_image(self, image_array: np.ndarray):
        qimg = numpy_to_qimage(image_array)
        pixmap = QPixmap.fromImage(qimg)
        self.reference_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

    def update_best_fitness(self, fitness: float):
        self.best_fitness_label.setText(f"Best Fitness Ever: {fitness:.4f}")

    def update_current_best_fitness(self, fitness: float):
        self.current_best_fitness_label.setText(f"Current Gen Best: {fitness:.4f}")

    def update_best_image_ever(self, image_array: np.ndarray):
        if image_array is not None:
            qimg = numpy_to_qimage(image_array)
            pixmap = QPixmap.fromImage(qimg)
            self.best_image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        else:
            self.best_image_label.setText("Best Image Ever")

    def update_current_best_image(self, image_array: np.ndarray):
        if image_array is not None:
            qimg = numpy_to_qimage(image_array)
            pixmap = QPixmap.fromImage(qimg)
            self.current_best_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        else:
            self.current_best_label.setText("Current Gen Best")
    
    def set_start_button_text(self, text: str):
        self.start_button.setText(text)
   