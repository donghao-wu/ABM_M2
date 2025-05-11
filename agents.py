import math
## Using experimental agent type with native "cell" property that saves its current position in cellular grid
from mesa.experimental.cell_space import CellAgent

## Helper function to get distance between two cells
def get_distance(cell_1, cell_2):
    x1, y1 = cell_1.coordinate
    x2, y2 = cell_2.coordinate
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)

class SugarAgent(CellAgent):
    ## Initiate agent, inherit model property from parent class
    def __init__(self, model, cell, sugar=0, metabolism=0, vision = 0):
        super().__init__(model)
        ## Set variable traits based on model parameters
        self.cell = cell
        self.sugar = sugar 
        self.metabolism = metabolism
        self.vision = vision
        self.class_status = "middle" ##initialize every agent as middle class
        self.sugar_history = [] ##initialize the status mobility as empty
        self.living_expense = 1 ## initialize the living expense as 1
        
    ## define class update function
    def update_class_status(self):
        self.sugar_history.append(self.sugar)
        if len(self.sugar_history) >10:
            self.sugar_history.pop(0)
        avg_sugar = sum(self.sugar_history) / len(self.sugar_history) ## calculate the average sugar history to classify agents later
        
        #setting criteria for each social class based on the average sugar
        if avg_sugar < 15:
            self.class_status = "low"
        elif 15 <= avg_sugar < 50:
            self.class_status = "middle"
        else:
            self.class_status = "high"
    ## Define update living expense function
    def update_living_expense(self):
        if self.sugar_history:
            avg_sugar = sum(self.sugar_history) / len(self.sugar_history)
            self.living_expense = 1 +math.log(avg_sugar + 1) ## using log function to calculate the living expense
            self.sugar -= self.living_expense
    ## Define movement action, this function is modified by introducing penalty terms and change the move logic
    def move(self):
    # Get all empty cells within the agent's vision
        possibles = [
            cell
            for cell in self.cell.get_neighborhood(self.vision, include_center=True)
            if cell.is_empty
        ]
        
        ## This line of code should solve the max() iterable argument is empty error
        if not possibles:
            return
        
        # Initialize class_scores if not already present
        if not hasattr(self.cell, "class_score"):
            self.cell.class_scores = []
        
        # Define a mapping of class status to integer values
        class_values = {
            "low": 0,
            "middle": 1,
            "high": 2
        } [self.class_status]

        self.cell.class_scores.append(class_values)

        #Limit the number of class scores to 20
        if len(self.cell.class_scores) > 20:
            self.cell.class_scores.pop(0)

        # Define a class-aware scoring function for each possible destination
        def score(cell):
            # Look at neighbors of the candidate cell
            neighbors = cell.get_neighborhood(include_center=False)

            # Count how many neighboring agents are in the "low" class
            poor_neighbors = sum(
                1 for agent in neighbors
                if isinstance(agent, SugarAgent) and agent.class_status == "low"
            )

             # High-class agents are sensitive to poverty — avoid poor neighbors
            penalty = poor_neighbors if self.class_status == "high" else 0

            # Final score = sugar at the cell minus social penalty
            return cell.sugar - penalty

        # Step 1: Find the highest score among all candidate cells
        best_score = max(score(cell) for cell in possibles)

        # Step 2: Keep only the cells with this best score
        best_cells = [cell for cell in possibles if score(cell) == best_score]

        # Step 3: Among these, find the ones closest to current position
        min_dist = min(get_distance(self.cell, cell) for cell in best_cells)
        final_cells = [
            cell for cell in best_cells
            if math.isclose(get_distance(self.cell, cell), min_dist, rel_tol=1e-02)
        ]

        # Step 4: Randomly choose one of the best, closest cells
        self.cell = self.random.choice(final_cells)

    ## consumer sugar in current cell, depleting it, then consumer metabolism
    def gather_and_eat(self):
        self.sugar += self.cell.sugar
        self.cell.sugar = 0
        self.sugar -= self.metabolism
    ## If an agent has zero or negative suger, it dies and is removed from the model
    def see_if_die(self):
        if self.sugar <= 0:
            self.remove()
    
    
        
