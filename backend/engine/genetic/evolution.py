import random
import operator
import numpy as np
import pandas as pd
from deap import base, creator, tools, gp
from .primitives import create_primitive_set
from .fitness import evaluate_fitness, evaluate_strategy_signals

class StrategyEvolver:
    """Evolves trading strategies using Genetic Programming (DEAP) matching MT5 risk settings."""

    def __init__(
        self,
        ohlcv_data: pd.DataFrame,
        indicator_values: dict[str, np.ndarray],
        population_size: int = 100,
        n_generations: int = 25,
        crossover_prob: float = 0.7,
        mutation_prob: float = 0.2,
        tournament_size: int = 3,
        risk_config: dict | None = None
    ):
        self.df = ohlcv_data
        self.indicator_names = list(indicator_values.keys())
        self.indicator_arrays = [indicator_values[k] for k in self.indicator_names]
        self.pop_size = max(10, population_size)
        self.n_gen = max(1, n_generations)
        self.cx_prob = crossover_prob
        self.mut_prob = mutation_prob
        self.tourn_size = tournament_size
        self.risk_config = risk_config or {}

        # Fast training sample for lightning-fast GP search across 50 generations
        if len(self.df) > 2500:
            self.eval_df = self.df.iloc[-2500:].copy().reset_index(drop=True)
            self.eval_indicators = [arr[-2500:] for arr in self.indicator_arrays]
        else:
            self.eval_df = self.df
            self.eval_indicators = self.indicator_arrays

        self.pset = create_primitive_set(len(self.indicator_names))
        for i, name in enumerate(self.indicator_names):
            self.pset.renameArguments(**{f"ARG{i}": name.replace(" ", "_").replace("%", "pct").replace("-", "_")})

        self._setup_deap()

    def _setup_deap(self):
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("expr", gp.genHalfAndHalf, pset=self.pset, min_=1, max_=4)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("compile", gp.compile, pset=self.pset)
        self.toolbox.register("evaluate", self._evaluate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=self.tourn_size)
        self.toolbox.register("mate", gp.cxOnePoint)
        self.toolbox.register("mutate", gp.mutUniform, expr=self.toolbox.expr, pset=self.pset)

        self.toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=8))
        self.toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=8))

    def _evaluate_individual(self, individual):
        func = self.toolbox.compile(expr=individual)
        score, _ = evaluate_fitness(
            func, 
            self.eval_indicators, 
            self.eval_df, 
            risk_config=self.risk_config, 
            tree_len=len(individual)
        )
        return (score,)

    def evolve(self, progress_callback=None) -> list[dict]:
        """Run the GP evolution loop and return top strategies evaluated on full dataset."""
        pop = self.toolbox.population(n=self.pop_size)
        hof = tools.HallOfFame(20)

        fitnesses = list(map(self.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        hof.update(pop)

        for gen in range(1, self.n_gen + 1):
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.cx_prob:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.mut_prob:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            pop[:] = offspring
            hof.update(pop)

            if progress_callback:
                progress_callback(
                    phase="genetic",
                    progress=int((gen / self.n_gen) * 100),
                    generation=gen,
                    total_generations=self.n_gen,
                    best_sharpe=hof[0].fitness.values[0] if len(hof) > 0 else 0.0
                )

        results = []
        direction = self.risk_config.get("direction", "both")
        
        # Evaluate Top Finalists on 100% full dataset
        for i, ind in enumerate(hof):
            func = self.toolbox.compile(expr=ind)
            sharpe, bt_res = evaluate_fitness(
                func, 
                self.indicator_arrays, 
                self.df, 
                risk_config=self.risk_config,
                tree_len=len(ind)
            )
            entries, exits = evaluate_strategy_signals(
                func, 
                self.indicator_arrays, 
                len(self.df),
                direction=direction
            )
            results.append({
                "id": f"gp_strategy_{i+1}",
                "tree": str(ind),
                "fitness": sharpe,
                "compiled": func,
                "entries": entries,
                "exits": exits,
                "backtest": bt_res
            })

        return results
