from abc import ABC, abstractmethod
from genetic.gene import Gene
import random

class GeneCrossover(ABC):
    @abstractmethod
    def crossover(self, parent1: Gene, parent2: Gene) -> Gene | None:
        pass

class CrossoverWithProbability(GeneCrossover):
    def __init__(self, probability: float):
        self.probability = probability

    def crossover(self, parent1: Gene, parent2: Gene) -> Gene | None:
        if random.random() < self.probability:
            return self.crossover_func(parent1, parent2)
        else:
            return None

class CrossoverWithOneOf(GeneCrossover):
    def __init__(self, crossovers: list[GeneCrossover], weights: list[int] | None = None):
        self.crossovers = crossovers
        self.weights = weights

    def crossover(self, parent1: Gene, parent2: Gene) -> Gene | None:
        crossover = random.choices(self.crossovers, weights=self.weights)[0]
        return crossover.crossover(parent1, parent2)

class DoNothingGeneCrossover(GeneCrossover):
    def crossover(self, parent1: Gene, _: Gene) -> Gene | None:
        return None

class KeepFirstParentGeneCrossover(GeneCrossover):
    def crossover(self, parent1: Gene, _: Gene) -> Gene | None:
        return parent1.copy()

class KeepSecondParentGeneCrossover(GeneCrossover):
    def crossover(self, _: Gene, parent2: Gene) -> Gene | None:
        return parent2.copy()

class SinglePointGeneCrossover(GeneCrossover):
    def crossover(self, parent1: Gene, parent2: Gene) -> Gene | None:
        new_gene = Gene()
        short_length = min(len(parent1.polygons), len(parent2.polygons))
        long_length = max(len(parent1.polygons), len(parent2.polygons))
        final_length = random.randint(short_length, long_length)
        first_half = random.randint(0, final_length - 2) # the second half is at least 1
        second_half = final_length - first_half
        new_gene.polygons = parent1.polygons[:first_half].copy() + parent2.polygons[-second_half:].copy()
        new_gene.colors = parent1.colors[:first_half].copy() + parent2.colors[-second_half:].copy()
        assert len(new_gene.polygons) == final_length
        return new_gene

