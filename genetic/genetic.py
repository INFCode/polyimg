import random
from environment import PolygonEnvironment, PolygonEnvironmentConfig
import numpy as np
from genetic.gene import Gene
from genetic.mutate import (
    GeneMutator, 
    PolygonwiseGeneMutator,
    MutateWithSomeOf, 
    NoisyVerticesPolygonMutation, 
    NoisyColorPolygonMutation, 
    SwapPolygonsGeneMutator, 
    ReplacePolygonGeneMutator
)
from genetic.crossover import GeneCrossover, SinglePointGeneCrossover, CrossoverWithOneOf, KeepFirstParentGeneCrossover, KeepSecondParentGeneCrossover
from dataclasses import dataclass
from scanline import SampleOffset2D, FillRule
import math

class GeneInfo:
    gene: Gene
    fitness: float | None
    render: np.ndarray | None

    def __init__(self, gene: Gene):
        self.gene = gene
        self.fitness = None
        self.render = None
    
    def evaluate(self, environment: PolygonEnvironment):
        if self.fitness is not None:
            return
        diff, canvas = environment.add_polygons(self.gene.as_polygons())
        environment.reset()
        self.fitness = diff
        self.render = canvas

def create_initial_population(population_size: int, num_polygons: int, num_vertices: int) -> list[GeneInfo]:
    return [GeneInfo(Gene.random_gene(num_polygons, num_vertices)) for _ in range(population_size)]

def roulette_wheel_selection(population: list[GeneInfo], selection_size: int) -> list[GeneInfo]:
    # weight as softmax(10 * fitness_scores)
    weights = [math.exp(10 * gene.fitness) for gene in population]
    selected = random.choices(population, weights=weights, k=selection_size)
    return selected

@dataclass
class GeneticAlgorithmConfig:
    environment_config: PolygonEnvironmentConfig
    generations: int
    population_size: int
    initial_num_polygons: int
    initial_num_vertices: int
    mutator: GeneMutator
    crossover: GeneCrossover

GeneticAlgorithmConfig.DEFAULT_CONFIG = GeneticAlgorithmConfig(
    environment_config=PolygonEnvironmentConfig(
        sample_offset=SampleOffset2D.CENTER,
        fill_rule=FillRule.EVEN_ODD,
        similarity_measure="psnr"
    ),
    generations=1000,
    population_size=10,
    initial_num_polygons=20,
    initial_num_vertices=8,
    mutator=MutateWithSomeOf([
        PolygonwiseGeneMutator(NoisyVerticesPolygonMutation(lambda: random.gauss(0, 0.1))),
        PolygonwiseGeneMutator(NoisyColorPolygonMutation(lambda: random.gauss(0, 0.1))),
        SwapPolygonsGeneMutator(),
        ReplacePolygonGeneMutator()
    ], repeat=2, weights=[16, 8, 2, 1]),
    crossover=CrossoverWithOneOf([
        SinglePointGeneCrossover(),
        KeepFirstParentGeneCrossover(),
    ], weights=[1, 9])
)

def genetic_algorithm(reference_image: np.ndarray, config: GeneticAlgorithmConfig):
    print("Starting genetic algorithm")
    environment = PolygonEnvironment(config.environment_config)
    environment.setup(reference_image)
    print("Environment setup")
    
    population = create_initial_population(config.population_size, config.initial_num_polygons, config.initial_num_vertices)
    print("Population created")
    for i, gene in enumerate(population):
        print(f"Evaluating fitness {i}/{len(population)}")
        gene.evaluate(environment)
    yield population

    print("Starting main loop")
    for generation in range(config.generations):
        # Select parents
        survivors = roulette_wheel_selection(population, config.population_size // 4)
        survivors.append(max(population, key=lambda x: x.fitness))

        # Create next generation
        next_generation = survivors
        while True:
            parents1 = roulette_wheel_selection(population, config.population_size // 4 * 2)
            parents2 = roulette_wheel_selection(population, config.population_size // 4 * 2)
            for p1, p2 in zip(parents1, parents2):
                child_gene = config.crossover.crossover(p1.gene, p2.gene)
                if child_gene is not None:
                    config.mutator.mutate(child_gene)
                    next_generation.append(GeneInfo(child_gene))
                    if len(next_generation) >= config.population_size:
                        break
            if len(next_generation) >= config.population_size:
                break
        
        population = next_generation[:config.population_size]

        for i, gene in enumerate(population):
            print(f"Evaluating fitness {i}/{len(population)}")
            gene.evaluate(environment)

        yield population
