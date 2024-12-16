from dataclasses import dataclass

@dataclass
class Polygon:
    vertices: list[tuple[float, float]]
    color: tuple[float, float, float, float]
