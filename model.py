from pathlib import Path

import numpy as np

import mesa
from agents import SugarAgent
## Using experimental cell space for this model that enforces von Neumann neighborhoods
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid
## Use experimental space feature that allows us to save sugar as a property of the grid spaces
from mesa.experimental.cell_space.property_layer import PropertyLayer

class SugarScapeModel(mesa.Model):
    ## Helper function to calculate Gini coefficient, used in plot
    def calc_gini(self):
        agent_sugars = [a.sugar for a in self.agents]
        sorted_sugars = sorted(agent_sugars)
        n = len(sorted_sugars)
        x = sum(el * (n - ind) for ind, el in enumerate(sorted_sugars)) / (n * sum(sorted_sugars))
        return 1 + (1 / n) - 2 * x
    ## Define initiation, inherit seed property from parent class
    def __init__(
        self,
        width = 50,
        height = 50,
        initial_population=200,
        endowment_min=25,
        endowment_max=50,
        metabolism_min=1,
        metabolism_max=5,
        vision_min=1,
        vision_max=5,
        seed = None
    ):
        super().__init__(seed=seed)
        ## Instantiate model parameters
        self.width = width
        self.height = height
        ## Set model to run continuously
        self.running = True
        ## Create grid
        self.grid = OrthogonalVonNeumannGrid(
            (self.width, self.height), torus=True, random=self.random
        )
        ## Define datacollector, which calculates current Gini coefficient
        self.datacollector = mesa.DataCollector(
            model_reporters = {"Gini": self.calc_gini},
        )
        ## Import sugar distribution from raster, define grid property
        self.sugar_distribution = np.genfromtxt(Path(__file__).parent / "sugar-map.txt")
        self.grid.add_property_layer(
            PropertyLayer.from_data("sugar", self.sugar_distribution)
        )
        ## Create agents, give them random properties, and place them randomly on the map
        SugarAgent.create_agents(
            self,
            initial_population,
            self.random.choices(self.grid.all_cells.cells, k=initial_population),
            sugar=self.rng.integers(
                endowment_min, endowment_max, (initial_population,), endpoint=True
            ),
            metabolism=self.rng.integers(
                metabolism_min, metabolism_max, (initial_population,), endpoint=True
            ),
            vision=self.rng.integers(
                vision_min, vision_max, (initial_population,), endpoint=True
            ),
        )
        ## Initialize datacollector
        self.datacollector.collect(self)
    ## Define step function, which is called at each tick
    def step(self):
        ## Update sugar distribution, which is a property of the grid
        ## This will potentially cause the high-class clustering and cause faster sugar regeneration
        ## Poor class agents will have a slower sugar regeneration
        for (x,y), cell in self.grid.coord_iter():
            base_growth = 1
            max_bonus = 2
            if hasattr(cell, "class_score") and cell.class_scores:
                avg_class = sum(cell.class_scores) / len(cell.class_scores) 
                bonus = min(avg_class * 0.5, max_bonus)
            else:
                bonus = 0
            regrowth = base_growth + bonus
            cell.sugar = min(cell.sugar + regrowth, self.sugar_distribution[x,y])
        self.agents.shuffle_do("move")
        self.agents.shuffle_do("gather_and_eat")
        self.agents.shuffle_do("update_living_expense") ## add the movement to update living expense
        self.agents.shuffle_do("update_class_status") ## add the movement to update class status ##
        self.agents.shuffle_do("see_if_die")
        self.datacollector.collect(self)
    
