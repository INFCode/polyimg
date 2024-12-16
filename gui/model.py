import numpy as np

class GeneticModel:
    """
    Holds the state for the genetic algorithm run:
     - Reference image
     - Best fitness ever
     - Current generation's best image
    """
    def __init__(self):
        self.reference_image = None
        self.best_fitness_ever = float('-inf')
        self.best_image_ever = None
        self.current_best_image = None
        self.current_best_fitness = float('-inf')
    def set_reference_image(self, image_array: np.ndarray):
        self.reference_image = image_array
        self.best_fitness_ever = float('-inf')
        self.best_image_ever = None
        self.current_best_image = None

    def update_state(self, genes_list):
        # Find current generation best
        max_fit = max(genes_list, key=lambda x: x.fitness)
        self.current_best_image = max_fit.render
        self.current_best_fitness = max_fit.fitness

        # Update best image ever
        if max_fit.fitness > self.best_fitness_ever:
            self.best_fitness_ever = max_fit.fitness
            self.best_image_ever = max_fit.render
