from genetic.gene import Gene
from environment import Polygon
from abc import ABC, abstractmethod
import random
from typing import Callable

def clip(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))

class GeneMutator(ABC):
    @abstractmethod
    def mutate(self, gene: Gene):
        pass

# Combinators
class MutateWithProbability(GeneMutator):
    def __init__(self, probability: float, mutator: GeneMutator):
        self.probability = probability
        self.mutator = mutator

    def mutate(self, gene: Gene):
        if random.random() < self.probability:
            self.mutator.mutate(gene)

class MutateWithSomeOf(GeneMutator):
    def __init__(self, mutators: list[GeneMutator], repeat: int = 1, weights: list[int] | None = None):
        self.mutators = mutators
        self.repeat = repeat
        self.weights = weights

    def mutate(self, gene: Gene):
        # choose a mutator based on the weights
        for _ in range(self.repeat):
            mutator = random.choices(self.mutators, weights=self.weights)[0]
            mutator.mutate(gene)

class MutateWithAll(GeneMutator):
    def __init__(self, mutators: list[GeneMutator]):
        self.mutators = mutators

    def mutate(self, gene: Gene):
        for mutator in self.mutators:
            mutator.mutate(gene)

# Mutator that mutates a single polygon
class PolygonwiseGeneMutator(GeneMutator):
    class PolygonMutation(ABC):
        @abstractmethod
        def mutate_polygon(self, vertices: list[float], color: list[float]):
            pass

    def __init__(self, mutation_method: PolygonMutation):
        self.mutation_method = mutation_method
    
    def mutate(self, gene: Gene):
        # find a polygon to mutate
        polygon_index = random.randint(0, len(gene.polygons) - 1)
        polygon = gene.polygons[polygon_index]
        # mutate the polygon
        self.mutation_method.mutate_polygon(gene.polygons[polygon_index], gene.colors[polygon_index])

# shape mutations
class NoisyVerticesPolygonMutation(PolygonwiseGeneMutator.PolygonMutation):
    def __init__(self, noise_source: Callable[[], float]):
        self.noise_source = noise_source

    def mutate_polygon(self, vertices: list[float], _: list[float]):
        # add noise to a random vertex
        index = random.randint(0, len(vertices) // 2 - 1)
        for i in range(2):
            vertices[index * 2 + i] += self.noise_source()
            vertices[index * 2 + i] = clip(vertices[index * 2 + i], 0, 1)

class SwapVerticesPolygonMutation(PolygonwiseGeneMutator.PolygonMutation):
    def mutate_polygon(self, vertices: list[float], _: list[float]):
        # swap two random vertices
        index1 = random.randint(0, len(vertices) // 2 - 1)
        index2 = random.randint(0, len(vertices) // 2 - 1)
        vertices[index1 * 2], vertices[index2 * 2] = vertices[index2 * 2], vertices[index1 * 2]
        vertices[index1 * 2 + 1], vertices[index2 * 2 + 1] = vertices[index2 * 2 + 1], vertices[index1 * 2 + 1]

class AddVertexPolygonMutation(PolygonwiseGeneMutator.PolygonMutation):
    def mutate_polygon(self, vertices: list[float], _: list[float]):
        # add a new vertex
        new_vertex = [random.uniform(0, 1), random.uniform(0, 1)]
        #insert it in the middle of the polygon
        vertices.insert(random.randint(0, len(vertices) // 2), new_vertex)

class RemoveVertexPolygonMutation(PolygonwiseGeneMutator.PolygonMutation):
    def mutate_polygon(self, vertices: list[float], _: list[float]):
        # remove a random vertex
        if len(vertices) > 3:
            index = random.randint(0, len(vertices) // 2 - 1)
            vertices.pop(index * 2)
            vertices.pop(index * 2)

# color mutations
class NoisyColorPolygonMutation(PolygonwiseGeneMutator.PolygonMutation):
    def __init__(self, noise_source: Callable[[], float]):
        self.noise_source = noise_source

    def mutate_polygon(self, _: list[float], color: list[float]):
        # add noise to the color
        for i in range(len(color)):
            color[i] += self.noise_source()
            color[i] = clip(color[i], 0, 1)

class NewColorPolygonMutation(PolygonwiseGeneMutator.PolygonMutation):
    def mutate_polygon(self, _: list[float], color: list[float]):
        # set a new random color
        color.clear()
        color.extend([random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)])

class SwapPolygonsGeneMutator(GeneMutator):
    def mutate(self, gene: Gene):
        # swap two random polygons
        index1 = random.randint(0, len(gene.polygons) - 1)
        index2 = random.randint(0, len(gene.polygons) - 1)
        gene.polygons[index1], gene.polygons[index2] = gene.polygons[index2], gene.polygons[index1]

class AddPolygonGeneMutator(GeneMutator):
    def __init__(self, num_vertices_sampler: Callable[[], int], max_polygons: int = -1):
        self.num_vertices_sampler = num_vertices_sampler
        self.max_polygons = max_polygons

    def mutate(self, gene: Gene):
        if self.max_polygons < 0 or len(gene.polygons) < self.max_polygons:
            # add a new polygon
            vertices = [random.uniform(0, 1) for _ in range(2 * self.num_vertices_sampler())]
            color = [random.uniform(0, 1) for _ in range(4)]
            gene.polygons.append(vertices)
            gene.colors.append(color)

class RemovePolygonGeneMutator(GeneMutator):
    def mutate(self, gene: Gene):
        # remove a random polygon
        if len(gene.polygons) > 0:
            index = random.randint(0, len(gene.polygons) - 1)
            gene.polygons.pop(index)
            gene.colors.pop(index)

class ReplacePolygonGeneMutator(GeneMutator):
    def mutate(self, gene: Gene):
        # replace a random polygon
        if len(gene.polygons) > 0:
            index = random.randint(0, len(gene.polygons) - 1)
            gene.polygons[index] = [random.uniform(0, 1) for _ in range(len(gene.polygons[index]))]
            gene.colors[index] = [random.uniform(0, 1) for _ in range(len(gene.colors[index]))]
