from PySide6.QtCore import QThread
from PySide6.QtWidgets import QFileDialog
import numpy as np
from PIL import Image

class GeneticController:
    def __init__(self, model, view, genetic_function):
        self.model = model
        self.view = view
        self.genetic_function = genetic_function
        self.worker_thread = None
        self.worker = None

        # Connect view signals
        self.view.pauseClicked.connect(self.on_pause_clicked)
        self.view.startClicked.connect(self.on_start_clicked)

    def on_start_clicked(self):
        if self.worker:
            # Currently running, treat this as a reset
            self._stop_genetic_thread()
            self._select_image()
            if self.model.reference_image is not None:
                self._start_genetic_thread()
                self.view.set_start_button_text("Reset")
        else:
            # Not running, treat this as a start
            if self.model.reference_image is None:
                self._select_image()
            if self.model.reference_image is not None:
                self._start_genetic_thread()
                self.view.set_start_button_text("Reset")

    def on_pause_clicked(self, paused):
        if self.worker:
            if paused:
                self.worker.pause()
            else:
                self.worker.resume()

    def _select_image(self):
        filename, _ = QFileDialog.getOpenFileName(self.view, "Select Reference Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            img = Image.open(filename).convert('RGB')
            image_array = np.array(img)
            print("Image loaded, shape:", image_array.shape)
            h, w, _ = image_array.shape
            max_pixels = 10000
            if w * h > max_pixels:
                from PySide6.QtWidgets import QMessageBox
                msg = QMessageBox(self.view)
                msg.setText("The image is too large. Do you want to downscale or choose another image?")
                down_btn = msg.addButton("Downscale", QMessageBox.AcceptRole)
                choose_btn = msg.addButton("Choose Another", QMessageBox.RejectRole)
                msg.exec()

                if msg.clickedButton() == choose_btn:
                    self._select_image()
                    return
                else:
                    # Downscale while maintaining aspect ratio to <= 90000 pixels
                    import math
                    ratio = math.sqrt(max_pixels/(w*h))
                    new_w = int(w * ratio)
                    new_h = int(h * ratio)
                    img = img.resize((new_w, new_h))
                    image_array = np.array(img)
                    print("Image downscaled, shape:", image_array.shape)
            image_array = image_array.astype(float) / 255.0
            self.model.set_reference_image(image_array)
            self.view.update_reference_image(image_array)

    def _start_genetic_thread(self):
        print("Starting genetic thread")
        self.worker_thread = QThread()
        from gui.worker import GeneticWorker
        self.worker = GeneticWorker(self.genetic_function, self.model.reference_image)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.iterationDone.connect(self.on_iteration_done)
        self.worker.finished.connect(self.on_worker_finished)

        self.worker_thread.start()
        print("Genetic thread started")

    def _stop_genetic_thread(self):
        if self.worker:
            self.worker.stop()
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker = None
            self.worker_thread = None

    def on_iteration_done(self, genes_list):
        self.model.update_state(genes_list)
        self.view.update_best_fitness(self.model.best_fitness_ever)
        self.view.update_best_image_ever(self.model.best_image_ever)
        self.view.update_current_best_image(self.model.current_best_image)
        self.view.update_current_best_fitness(self.model.current_best_fitness)

    def on_worker_finished(self):
        # Worker finished running
        pass
