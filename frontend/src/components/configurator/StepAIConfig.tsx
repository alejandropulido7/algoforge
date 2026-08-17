import React from 'react';
import { Dna, Bot, Dice5, Trophy, Clock } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import Select from '../common/Select';
import styles from '../../styles/pages.module.css';

const StepAIConfig: React.FC = () => {
  const { config, updateGenetic, updateRL, updateMonteCarlo } = useJobStore();

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>AI & Backtest Configuration</h2>
      <p className={styles.stepSubtitle}>Configure the core evolutionary engines, neural RL, candidate pool size, and Monte Carlo validation.</p>

      {/* 0. Top Strategies Count Selector */}
      <div className={styles.configSection} style={{ border: '1px solid rgba(0, 212, 255, 0.3)', background: 'rgba(0, 212, 255, 0.02)' }}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Trophy size={20} className="text-cyan" />
            <h3 className={styles.sectionTitle} style={{ margin: 0 }}>Cantidad de Estrategias a Generar</h3>
          </div>
          <span className="text-xs" style={{ color: 'var(--color-accent-amber)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Clock size={13} />
            Mayor cantidad = Más tiempo de análisis
          </span>
        </div>

        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Elige cuántas estrategias finalistas quieres que el algoritmo genético optimice, valide con Monte Carlo y entregue al finalizar el pipeline.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.5rem', marginBottom: '0.75rem' }}>
          {[5, 10, 20, 30, 50].map((count) => {
            const isSelected = (config.genetic.topStrategiesCount || 20) === count;
            return (
              <button
                key={count}
                type="button"
                onClick={() => updateGenetic({ topStrategiesCount: count })}
                style={{
                  padding: '0.625rem 0.5rem',
                  borderRadius: '6px',
                  border: isSelected ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                  background: isSelected ? 'rgba(0, 212, 255, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                  color: isSelected ? 'var(--color-accent-cyan)' : 'var(--color-text-main)',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  textAlign: 'center'
                }}
              >
                <div>{count} Estrategias</div>
                <div style={{ fontSize: '0.6875rem', fontWeight: 400, color: 'var(--color-text-muted)', marginTop: '0.125rem' }}>
                  {count === 5 ? '⚡ Ultrarrápido' : (count === 10 ? '✨ Recomendado' : (count === 20 ? '📊 Estándar' : (count === 30 ? '🔍 Extensivo' : '🔬 Búsqueda Profunda')))}
                </div>
              </button>
            );
          })}
        </div>

        <div style={{
          padding: '0.625rem 0.875rem',
          background: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.2)',
          borderRadius: '6px',
          fontSize: '0.75rem',
          color: 'var(--color-accent-amber)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>💡 <b>Nota:</b> Entre más estrategias elijas generar (ej: 30 o 50), el motor evolutivo y las simulaciones de Monte Carlo procesarán más árboles lógicos, extendiendo la duración del análisis.</span>
        </div>
      </div>

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
