import React from 'react';
import { Dna, Bot, Dice5 } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import Select from '../common/Select';
import styles from '../../styles/pages.module.css';

const StepAIConfig: React.FC = () => {
  const { config, updateGenetic, updateRL, updateMonteCarlo } = useJobStore();

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>AI & Backtest Configuration</h2>
      <p className={styles.stepSubtitle}>Configure the core evolutionary engines, neural RL, and Monte Carlo validation.</p>

      {/* 1. Genetic Programming */}
      <div className={styles.configSection}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Dna size={20} className="text-cyan" />
            <h3 className={styles.sectionTitle} style={{ margin: 0 }}>Genetic Programming (DEAP)</h3>
          </div>
          <span className="text-xs text-secondary">Evolves decision trees & indicator rules</span>
        </div>
        
        <div className={styles.formGrid}>
          <Input 
            type="number" 
            label="Population Size" 
            value={config.genetic.populationSize}
            onChange={(e) => updateGenetic({ populationSize: parseInt(e.target.value) || 50 })}
            tooltipTitle="Population Size (Tamaño de Población)"
            tooltip="Número de estrategias candidatas generadas en paralelo por cada generación. Valores altos exploran más combinaciones pero requieren más tiempo de cómputo. Recomendado: 50-200 para pruebas rápidas, 500+ para búsqueda profunda."
          />
          <Input 
            type="number" 
            label="Generations" 
            value={config.genetic.generations}
            onChange={(e) => updateGenetic({ generations: parseInt(e.target.value) || 10 })}
            tooltipTitle="Generations (Ciclos Evolutivos)"
            tooltip="Cantidad de ciclos donde las mejores estrategias se cruzan y mutan para mejorar sus resultados. Más generaciones refinan las reglas. Recomendado: 20-50 generaciones."
          />
          <Input 
            type="number" 
            step="0.05"
            label="Crossover Probability" 
            value={config.genetic.crossoverProb}
            onChange={(e) => updateGenetic({ crossoverProb: parseFloat(e.target.value) || 0.7 })}
            tooltipTitle="Crossover Probability (Probabilidad de Cruce)"
            tooltip="Probabilidad (0.0 a 1.0) de que dos estrategias 'padre' exitosas combinen sus fragmentos de lógica para crear una nueva estrategia. Recomendado: 0.7 (70%)."
          />
          <Input 
            type="number" 
            step="0.05"
            label="Mutation Probability" 
            value={config.genetic.mutationProb}
            onChange={(e) => updateGenetic({ mutationProb: parseFloat(e.target.value) || 0.1 })}
            tooltipTitle="Mutation Probability (Probabilidad de Mutación)"
            tooltip="Probabilidad (0.0 a 1.0) de que una estrategia altere aleatoriamente un parámetro o indicador para descubrir nuevas soluciones y evitar estancarse. Recomendado: 0.1 (10%)."
          />
        </div>
      </div>

      {/* 2. Reinforcement Learning */}
      <div className={styles.configSection}>
        <div className={styles.sectionHeader}>
          <div>
            <div className="flex items-center gap-2">
              <Bot size={20} className="text-cyan" />
              <h3 className={styles.sectionTitle} style={{ margin: 0 }}>Reinforcement Learning (Deep RL)</h3>
            </div>
            <p className="text-xs text-secondary mt-1">Entrena un agente neuronal en un entorno Gymnasium para aprender políticas de trading dinámicas.</p>
          </div>
          <label className={styles.toggleLabel}>
            <input 
              type="checkbox" 
              checked={config.rl.enabled}
              onChange={(e) => updateRL({ enabled: e.target.checked })}
              className={styles.checkbox}
            />
            Enable RL
          </label>
        </div>
        
        {config.rl.enabled && (
          <div className={styles.formGrid}>
            <Select 
              label="Algorithm"
              value={config.rl.algorithm}
              onChange={(e) => updateRL({ algorithm: e.target.value as 'ppo'|'a2c' })}
              options={[
                {label: 'PPO (Proximal Policy Optimization)', value: 'ppo'},
                {label: 'A2C (Advantage Actor Critic)', value: 'a2c'}
              ]}
              tooltipTitle="RL Algorithm"
              tooltip="PPO es el estándar de la industria financiera por su convergencia estable y control de riesgo. A2C es más rápido pero más sensible a volatilidad."
            />
            <Input 
              type="number" 
              label="Timesteps" 
              value={config.rl.timesteps}
              onChange={(e) => updateRL({ timesteps: parseInt(e.target.value) || 50000 })}
              tooltipTitle="Timesteps (Pasos de Entrenamiento)"
              tooltip="Total de velas y estados de mercado en los que el agente practica y optimiza sus decisiones de compra/venta. Recomendado: 50,000 - 150,000."
            />
            <Input 
              type="number" 
              step="0.0001"
              label="Learning Rate" 
              value={config.rl.learningRate}
              onChange={(e) => updateRL({ learningRate: parseFloat(e.target.value) || 0.0003 })}
              tooltipTitle="Learning Rate (Tasa de Aprendizaje)"
              tooltip="Velocidad de ajuste de los pesos de la red neuronal. Valores demasiado altos causan inestabilidad; muy bajos tardan demasiado. Recomendado: 0.0003."
            />
          </div>
        )}
      </div>

      {/* 3. Monte Carlo Validation */}
      <div className={styles.configSection}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Dice5 size={20} className="text-cyan" />
            <h3 className={styles.sectionTitle} style={{ margin: 0 }}>Monte Carlo Validation (Prueba de Robustez)</h3>
          </div>
          <span className="text-xs text-secondary">Simula cientos de futuros posibles para descartar suerte</span>
        </div>

        <div className={styles.formGrid}>
          <Input 
            type="number" 
            label="Simulations" 
            value={config.montecarlo.simulations}
            onChange={(e) => updateMonteCarlo({ simulations: parseInt(e.target.value) || 1000 })}
            tooltipTitle="Monte Carlo Simulations"
            tooltip="Número de trayectorias alternadas simuladas para cada estrategia. Permite calcular el percentil 95% de drawdown y el índice de robustez real. Recomendado: 1000."
          />
          <Select 
            label="Method"
            value={config.montecarlo.method}
            onChange={(e) => updateMonteCarlo({ method: e.target.value as 'permutation'|'bootstrap' })}
            options={[
              {label: 'Permutation (Reordenamiento sin reemplazo)', value: 'permutation'},
              {label: 'Bootstrap (Remuestreo con reemplazo)', value: 'bootstrap'}
            ]}
            tooltipTitle="Simulation Method"
            tooltip="Permutación baraja el orden cronológico de los trades existentes para evaluar rachas negativas. Bootstrap toma muestras aleatorias con reemplazo simulando escenarios de mayor incertidumbre."
          />
          <Input 
            type="number" 
            label="Ruin Threshold (%)" 
            value={config.montecarlo.ruinThreshold}
            onChange={(e) => updateMonteCarlo({ ruinThreshold: parseInt(e.target.value) || 20 })}
            tooltipTitle="Ruin Threshold (Umbral de Ruina)"
            tooltip="Caída porcentual máxima de la cuenta considerada inaceptable o bancarrota (ej. perder el 20% o 50% del capital). AlgoForge medirá la probabilidad exacta de tocar este nivel. Recomendado: 20% - 50%."
          />
        </div>
      </div>
    </div>
  );
};

export default StepAIConfig;
