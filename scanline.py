import matplotlib.pyplot as plt
from math import floor
from enum import Enum
from dataclasses import dataclass
import numpy as np
from polygon import Polygon
class SampleOffset:
    """
    This class calculates the first position that is scanned by the scanline.

    The i-th scanline is at position i+offset and the region that is scanned for
    the first time is [i+offset - 1, i + offset).
    """
    def __init__(self, offset):
        if not (0.0 <= offset < 1.0):
            raise ValueError("Offset should be between 0 and 1")
        self.offset = offset 
    
    def first_scanned_position(self, x):
        """
        Return the lowest position that is first time scanned by the scanline.
        """
        return self.scanline_index(x) + self.offset - 1
    
    def scanline_index(self, x):
        """
        Return the index of the scanline that first scans the position x.
        """
        return floor(x + 1 - self.offset)
    
    def scanline_position(self, index):
        """
        Return the position of the i-th scanline.
        """
        return index + self.offset

@dataclass(frozen=True)
class SampleOffset2D:
    offset_x: SampleOffset
    offset_y: SampleOffset

# Predefined sample offsets for common positions
SampleOffset2D.TOP_LEFT = SampleOffset2D(SampleOffset(0.0), SampleOffset(0.0))
SampleOffset2D.TOP_RIGHT = SampleOffset2D(SampleOffset(1.0 - 1e-6), SampleOffset(0.0))
SampleOffset2D.BOTTOM_LEFT = SampleOffset2D(SampleOffset(0.0), SampleOffset(1.0 - 1e-6))
SampleOffset2D.BOTTOM_RIGHT = SampleOffset2D(SampleOffset(1.0 - 1e-6), SampleOffset(1.0 - 1e-6))
SampleOffset2D.CENTER = SampleOffset2D(SampleOffset(0.5), SampleOffset(0.5))

class ScanLineEdge:
    """
    Represents an edge in the scanline algorithm, storing necessary information
    for processing the edge during scanline filling.
    """
    def __init__(self, x_start, y_start, x_end, y_end, offset):
        if y_start == y_end:
            raise ValueError("Should never construct horizontal edge")
        
        # Ensure the edge is oriented from top to bottom
        if y_start > y_end:
            x_start, x_end = x_end, x_start
            y_start, y_end = y_end, y_start
            self.winding_number = -1
        else:
            self.winding_number = 1

        self.start_index = offset.scanline_index(y_start)
        self.end_index = offset.scanline_index(y_end)
        self.inv_slope = (x_end - x_start) / (y_end - y_start)
        self.current_x = x_start  # Current x for the active edge table
        self.update_current_x(offset.scanline_position(self.start_index) - y_start)

    def update_current_x(self, step: float = 1.0):
        """
        Increment the x-coordinate for the next scanline.
        """
        self.current_x += self.inv_slope * step

def create_edge_table(polygon, offset):
    """
    Create an edge table for the given polygon, used in the scanline fill algorithm.
    """
    edge_table = {}
    num_vertices = len(polygon)
    for i in range(num_vertices):
        x_start, y_start = polygon[i]
        x_end, y_end = polygon[(i + 1) % num_vertices]  # Wrap around to form edges
        if y_start == y_end:  # Ignore horizontal edges to avoid infinite inv_slope
            continue
        edge = ScanLineEdge(x_start, y_start, x_end, y_end, offset)
        if edge.start_index == edge.end_index:
            # Skip almost horizontal edges, will not be rendered anyway
            continue
        edge_table.setdefault(edge.start_index, []).append(edge)
    return edge_table

class FillRule(Enum):
    EVEN_ODD = 1
    NON_ZERO = 2

def scanline_fill(vertices: list[tuple[float, float]], offsets: SampleOffset2D, fill_rule: FillRule, pointwise_function):
    """
    Perform scanline fill on a polygon defined by vertices, using the specified fill rule.
    """
    edge_table = create_edge_table(vertices, offsets.offset_y)
    if not edge_table:
        return  # No edges to process

    min_y = min(edge_table.keys())
    max_y = max(max(edge.end_index for edge in edges) for edges in edge_table.values())
    
    active_edge_table = []

    for y in range(min_y, max_y):
        # Add edges starting at this y to the AET
        if y in edge_table:
            active_edge_table.extend(edge_table[y])

        # Remove edges from AET where y >= ymax
        active_edge_table = [edge for edge in active_edge_table if edge.end_index > y]

        # Sort AET by current x-coordinate
        active_edge_table.sort(key=lambda edge: edge.current_x)

        winding_number = 0
        is_prev_inside = False
        boundaries = []
        for edge in active_edge_table:
            winding_number += edge.winding_number
            if fill_rule == FillRule.EVEN_ODD:
                winding_number = winding_number % 2
            is_inside = winding_number != 0
            if is_inside != is_prev_inside:
                boundaries.append(edge.current_x)
            is_prev_inside = is_inside

        # Fill spans between pairs of intersections
        for i in range(0, len(boundaries), 2):
            x_start = boundaries[i]
            x_end = boundaries[i + 1]

            # Convert intersection range to pixel centers
            pixel_start = offsets.offset_x.scanline_index(x_start)
            pixel_end = offsets.offset_x.scanline_index(x_end)

            # Add filled pixels for the current span
            for x in range(pixel_start, pixel_end):
                pointwise_function(x, y)

        # Update current x-coordinates of edges in AET
        for edge in active_edge_table:
            edge.update_current_x()

def render_polygons(polygons: list[Polygon], offsets: SampleOffset2D, fill_rule: FillRule, image: np.ndarray | tuple):
    """
    Render a list of polygons onto an image using the scanline fill algorithm.
    """
    # breakpoint()
    if not all(0.0 <= v[0] <= 1.0 and 0.0 <= v[1] <= 1.0 for polygon in polygons for v in polygon.vertices):
        print(polygons)
        raise ValueError("Vertices should be normalized to the range [0, 1]")
    
    if isinstance(image, np.ndarray):
        canvas = image
    elif isinstance(image, tuple) and all(isinstance(dim, int) for dim in image):
        canvas = np.ones(image)
    else:
        raise ValueError("Invalid image argument: must be either a tuple or a numpy array")
    
    # Scale the polygons to the image size
    canvas_w, canvas_h = canvas.shape[:2]
    scaled_polygons = [
        Polygon(
            [(v[0] * canvas_h, v[1] * canvas_w) for v in p.vertices],
            p.color
        ) 
        for p in polygons
    ]

    def blend_with_color(color: tuple[float, float, float, float]):
        """
        Create a function to blend a given color with the canvas.
        """
        a = color[-1]
        premultiplied_rgb = np.array([channel * a for channel in color[:-1]])
        def record_pixel(x, y):
            canvas[y][x] = canvas[y][x] * (1-a) + premultiplied_rgb
        return record_pixel

    # Get filled pixels using the scanline fill algorithm with center sampling
    for p in scaled_polygons:
        #print("rendering", p.vertices)
        scanline_fill(p.vertices, offsets, fill_rule, blend_with_color(p.color))

    return canvas

if __name__ == "__main__":
    def show_image(image: np.ndarray):
        """
        Display the given image using matplotlib.
        """
        plt.imshow(image, interpolation='nearest')
        plt.show()
    
    # Example Usage
    polygon1 = Polygon([(0.452, 0.255), (0.931, 0.896), (0.477, 0.945), (0.192, 0.664), (0.878, 0.322), (0.481, 0.855), (0.684, 0.811)], (0.8, 0.5, 0.6, 0.9))
    polygon2 = Polygon([(0.342, 0.275), (0.931, 0.896), (0.477, 0.845), (0.222, 0.684), (0.879, 0.322), (0.491, 0.855), (0.784, 0.811)], (0.2, 0.7, 0.3, 0.4))
    offsets = SampleOffset2D(SampleOffset(0.5), SampleOffset(0.5))
    image = render_polygons([polygon1, polygon2], offsets, FillRule.EVEN_ODD, (100, 100, 3))
    show_image(image)
