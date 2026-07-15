class BuildCandidate:
    def __init__(self, build):
        self.build = build.copy()
        self.fitness = process_raster(candidates, dwellings, self.build)
        
    def evaluate(self):
        return self.fitness
        
    def breed(self, other):
        n = min(len(self.build), len(other.build))
        num_swaps = np.random.randint(1, n)
        swap_indices = np.random.choice(range(n), num_swaps, replace=False)
        new1, new2 = self.build.copy(), other.build.copy()
        for i in swap_indices:
            new1[i], new2[i] = new2[i], new1[i]
        bc1, bc2 = BuildCandidate(new1), BuildCandidate(new2)
        bc1.mutate()
        bc2.mutate()
        return bc1, bc2
    
    def mutate(self, mutation_rate=0.5):
        for i in range(len(self.build)):
            if np.random.rand() < mutation_rate:
                self.build[i] = np.random.choice(list(set(k) - set(self.build)))
                
    def compare(self, other):
        d1 = dominates(self, other)
        d2 = dominates(other, self)
        
        # neither dominates the other
        if not d1 and not d2:
            return self if np.random.rand() < 0.5 else other
        # both better in atleast one
        elif d1 and d2:
            return self if np.random.rand() < 0.5 else other
        # self dominates other
        elif d1:
            return self
        # other dominates self
        elif d2:
            return other
        else:
            print("Edge case")
        
        
            
    def __repr__(self):
        return f"BuildCandidate(build={self.build}, value={self.fitness})"
    
    def __eq__(self, other):
        return sorted(self.build) == sorted(other.build)

class NSGAII:
    def __init__(self, population_size=100, num_builds=4):
        population_size = 2*(population_size//2)
        self.population_size = population_size
        population = [BuildCandidate(np.random.choice(k, num_builds, replace=False)) for _ in range(population_size)]
        sorted_population = sorted(population, key=lambda x: x.evaluate(), reverse=True)
        self.curr_population = sorted_population
        
    def tournament_selection(self, tournament_size=2):
        selected = []
        for _ in range(self.population_size):
            tournament = np.random.choice(self.curr_population, tournament_size, replace=False)
            winner = tournament[0]
            for candidate in tournament[1:]:
                winner = winner.compare(candidate)
            selected.append(winner)
        return selected
        
    def next_generation(self):
        selected_parents = self.tournament_selection()
        
        for i in range(0, len(selected_parents), 2):
            parent1, parent2 = selected_parents[i], selected_parents[i+1]
            child1, child2 = parent1.breed(parent2)
            self.curr_population.append(child1)
            self.curr_population.append(child2)
            
        fronts = non_dominated_sorting(self.curr_population)
        
        new_population = []
        
        for front in fronts:
            if len(new_population) + len(front) <= self.population_size:
                new_population.extend([self.curr_population[i] for i in front])
            else:
                crowding_distances = calculate_crowding_distance(front, self.curr_population)
                sorted_front_indices = sorted(range(len(front)), key=lambda x: crowding_distances[x], reverse=True)
                remaining_slots = self.population_size - len(new_population)
                new_population.extend([self.curr_population[front[i]] for i in sorted_front_indices[:remaining_slots]])
                break
        
        self.curr_population = new_population
        
    def best_candidates(self):
        fronts = non_dominated_sorting(self.curr_population)
        best_front = [self.curr_population[i] for i in fronts[0]]
        return best_front
        
    def run(self, num_iter):
        fronts = []
        for i in range(num_iter):
            self.next_generation()
            best_front = self.best_candidates()
            print(f'Length of best front in generation {i+1}: {len(best_front)}')
            fronts.append(self.best_candidates())
            if len(best_front) > 0.9 * self.population_size:
                print('Increasing population size')
                self.population_size += 50
        return fronts
            
    
