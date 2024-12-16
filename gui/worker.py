from PySide6.QtCore import QObject, Signal, Slot
import numpy as np

class GeneticWorker(QObject):
    """Worker that runs the genetic algorithm in a separate thread."""
    iterationDone = Signal(list) 
    # genes_list

    finished = Signal()

    def __init__(self, genetic_function, image_array):
        super().__init__()
        self.genetic_function = genetic_function
        self.image_array = image_array
        self._pause = False
        self._running = True
        self.best_fitness_ever = float('-inf')
        self.best_image_ever = None

    @Slot()
    def run(self):
        # Run the genetic algorithm generator
        gen = self.genetic_function(self.image_array)

        for genes_list in gen:
            print("Iteration done")
            # Check running state
            if not self._running:
                break

            # Handle pause
            while self._pause:
                # Just sleep a bit waiting to resume
                # Use a busy-wait or QThread.usleep() or QThread.msleep()
                from time import sleep
                sleep(0.1)
                if not self._running:
                    break
            if not self._running:
                break

            self.iterationDone.emit(genes_list)

        self.finished.emit()

    def pause(self):
        self._pause = True

    def resume(self):
        self._pause = False

    def stop(self):
        self._running = False
