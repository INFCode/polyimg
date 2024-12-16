from environment import Polygon
import random
from typing import Self
class Gene:
    """
    A gene is a sequence of polygons with a color.
    """
    def __init__(self, polygons: list[list[float]] = [], colors: list[list[float]] = []):
        self.polygons = polygons
        self.colors = colors

    @classmethod
    def random_gene(cls, num_polygons: int, num_vertices: int) -> Self:
        return cls([[random.random() for _ in range(num_vertices * 2)] for _ in range(num_polygons)],
                    [[random.random() for _ in range(4)] for _ in range(num_polygons)])

    def as_polygons(self) -> list[Polygon]:
        return [Polygon(vertices=list(zip(*[iter(self.polygons[i])]*2)), color=self.colors[i]) for i in range(len(self.polygons))]

    def copy(self) -> Self:
        return Gene(self.polygons.copy(), self.colors.copy())
