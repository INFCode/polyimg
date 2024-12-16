from scanline import Polygon, SampleOffset2D, FillRule, render_polygons
import numpy as np
from image_similarity import similarity_score

class PolygonEnvironmentConfig:
    def __init__(self, sample_offset: SampleOffset2D, fill_rule: FillRule, similarity_measure: str):
        self.sample_offset = sample_offset
        self.fill_rule = fill_rule
        self.similarity_measure = similarity_measure

class PolygonEnvironment:
    def __init__(self, config: PolygonEnvironmentConfig):
        self.reference_image = None
        self.config = config
        self.similarity_score = 0

    def setup(self, reference_image: np.ndarray):
        self.reset(reference_image)
    
    def reset(self, reference_image: np.ndarray | None = None):
        if reference_image is not None:
            self.reference_image = reference_image
        self.canvas = np.ones_like(self.reference_image)
        self.similarity_score = 0
    
    def add_polygons(self, polygons: list[Polygon]) -> tuple[float, np.ndarray]:
        render_polygons(polygons, self.config.sample_offset, self.config.fill_rule, self.canvas)
        similarity = similarity_score(self.canvas, self.reference_image, self.config.similarity_measure)
        # print(f"Similarity: {similarity}")
        diff = similarity - self.similarity_score 
        self.similarity_score = similarity
        return diff, self.canvas
