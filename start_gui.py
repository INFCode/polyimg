import sys
from PySide6.QtWidgets import QApplication
from gui.model import GeneticModel
from gui.view import GeneticView
from gui.controller import GeneticController
from genetic.genetic import genetic_algorithm, GeneticAlgorithmConfig

# Placeholder for your actual genetic function
def genetic(image_array):
    # This should be a generator that yields (genes_list, fitness_list, images_list)
    # For demonstration, we yield dummy data
    import time
    genes = ["gene1", "gene2", "gene3"]
    for i in range(10): # simulate 10 iterations
        # Just generate random fitness and random images
        fitness = [i*0.1, i*0.2, i*0.15]
        images = [image_array, image_array, image_array] 
        yield (genes, fitness, images)
        time.sleep(0.5)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = GeneticModel()
    view = GeneticView()
    config = GeneticAlgorithmConfig.DEFAULT_CONFIG
    controller = GeneticController(model, view, lambda ref_img: genetic_algorithm(ref_img, config))

    view.show()
    sys.exit(app.exec())
