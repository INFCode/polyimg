import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PIL import Image

class ImageModel:
    def __init__(self, reference_image: np.ndarray, trial_image: np.ndarray, score: int):
        self.reference_image = reference_image
        self.trial_image = trial_image
        self.score = score
        self.is_started = False
        self.is_paused = False
        self.is_reference_replaced = False

    def update_reference_image(self, new_reference_image: np.ndarray):
        self.reference_image = new_reference_image
        self.trial_image = new_reference_image.copy()
        self.is_reference_replaced = True

    def update_trial_image(self, new_trial_image: np.ndarray):
        self.trial_image = new_trial_image

    def update_score(self, new_score: int):
        self.score = new_score

    def reset(self):
        self.is_started = False
        self.is_paused = False
        self.is_reference_replaced = False

class ImageView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Display App")

        # Create labels to display images
        self.label_reference = QLabel()
        self.label_trial = QLabel()

        # Create a label to display the score
        self.score_label = QLabel()

        # Add a button to select a new reference image
        self.select_image_button = QPushButton("Select Reference Image")

        # Add start/reset and pause/resume buttons
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.pause_button.setEnabled(False)

        # Layout setup
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.label_reference)
        image_layout.addWidget(self.label_trial)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(image_layout)
        main_layout.addWidget(self.score_label)
        main_layout.addWidget(self.select_image_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def set_controller(self, controller):
        self.controller = controller
        self.select_image_button.clicked.connect(self.controller.select_image)
        self.start_button.clicked.connect(self.controller.start)
        self.pause_button.clicked.connect(self.controller.pause)

    def update_images(self, reference_image: QImage, trial_image: QImage):
        self.label_reference.setPixmap(QPixmap.fromImage(reference_image))
        self.label_trial.setPixmap(QPixmap.fromImage(trial_image))

    def update_score(self, score: int):
        self.score_label.setText(f"Score: {score}")

    def set_buttons_state(self, is_started: bool, is_paused: bool):
        self.start_button.setText("Reset" if is_started else "Start")
        self.pause_button.setEnabled(is_started)
        self.pause_button.setText("Resume" if is_paused else "Pause")

class ImageController:
    def __init__(self, model: ImageModel, view: ImageView):
        self.model = model
        self.view = view
        self.view.update_images(self.numpy_to_qimage(self.model.reference_image), self.numpy_to_qimage(self.model.trial_image))
        self.view.update_score(self.model.score)

    def numpy_to_qimage(self, array: np.ndarray) -> QImage:
        height, width, channel = array.shape
        bytes_per_line = 3 * width
        return QImage(array.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self.view, "Select Image", "", "Image files (*.jpg *.jpeg *.png)")
        if file_path:
            new_reference_image = Image.open(file_path)
            new_reference_image = new_reference_image.resize((self.model.reference_image.shape[1], self.model.reference_image.shape[0]))
            new_reference_image_np = np.array(new_reference_image)
            self.model.update_reference_image(new_reference_image_np)
            self.view.update_images(self.numpy_to_qimage(self.model.reference_image), self.numpy_to_qimage(self.model.trial_image))

    def start(self):
        if not self.model.is_started:
            self.model.is_started = True
            self.model.is_paused = False
        else:
            self.model.reset()
        self.view.set_buttons_state(self.model.is_started, self.model.is_paused)

    def pause(self):
        if not self.model.is_paused:
            self.model.is_paused = True
        else:
            self.model.is_paused = False
        self.view.set_buttons_state(self.model.is_started, self.model.is_paused)

def main_loop(controller: ImageController) -> None:
    while True:
        state = controller.model
        if state.is_started and not state.is_paused:
            new_trial_image = np.random.randint(0, 255, state.reference_image.shape, dtype=np.uint8)
            new_score = np.random.randint(0, 100)
            controller.model.update_trial_image(new_trial_image)
            controller.model.update_score(new_score)
            controller.view.update_images(controller.numpy_to_qimage(controller.model.reference_image), controller.numpy_to_qimage(controller.model.trial_image))
            controller.view.update_score(controller.model.score)

        QApplication.processEvents()

def main() -> None:
    reference_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    trial_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    score = 0

    app = QApplication(sys.argv)
    model = ImageModel(reference_image, trial_image, score)
    view = ImageView()
    controller = ImageController(model, view)
    view.set_controller(controller)
    view.show()

    main_loop(controller)

if __name__ == "__main__":
    main()
