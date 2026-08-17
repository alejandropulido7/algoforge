# AlgoForge — Estado Completo del Proyecto & Contexto Global

> **Fecha de Actualización**: Agosto 2026  
> **Ubicación del Repositorio**: `/Users/alejandropulido/Documents/software-projects/trading/algoforge`  
> **Supabase Project**: `https://pzxowgozyojwruglsiam.supabase.co`  

---

## 1. Resumen Ejecutivo del Proyecto
**AlgoForge** es una plataforma web completa de descubrimiento, optimización y validación automatizada de estrategias cuantitativas de trading inspirada en herramientas como StrategyQuant, impulsada por:
- **Catálogo Integral de 40+ Indicadores Técnicos**: 100% de la librería oficial `ta` (bukosabino/ta) en Momentum, Tendencia, Volatilidad, Volumen y Retornos con paridad matemática total entre Python y MQL5.
- **Programación Genética (DEAP)**: Evolución simbólica de árboles lógicos y reglas de trading (White-Box).
- **Aprendizaje por Refuerzo (Stable-Baselines3 / Gymnasium / PyTorch)**: Agentes de trading basados en PPO/A2C exportados automáticamente a **ONNX** para inferencia nativa en MT5 o trading en vivo desde Python.
- **Simulación Avanzada MetaTrader 5**: Motor vela a vela con simulación intra-barra de Stop Loss y Take Profit (por pips o por ATR), cálculo dinámico de lotes o riesgo porcentual de cuenta.
- **Validación de Robustez Monte Carlo**: Simulaciones de permutación y bootstrap para cálculo de probabilidad de ruina y drawdown al 95% de confianza.
- **Exportadores Dinámicos de Código**:
  1. **MQL5 EA Clásico**: Para estrategias de reglas genéticas simbólicas con control de posición estricto y fórmulas de osciladores/retornos directas.
  2. **MQL5 EA con ONNX Nativo (`OnnxRun`)**: Para agentes Deep RL que corren sin necesidad de Python.
  3. **TradingView Pine Script v5**: Para graficación y backtesting en TradingView.
  4. **Python Live Trader (`live_trader.py`)**: Script puente para operar en vivo conectándose a MetaTrader 5 mediante la API de Python y `onnxruntime`.

---

## 2. Correcciones Críticas de MQL5 y Cierre de Operaciones

1. **Paridad Matemática de Indicadores Estadísticos y Osciladores**:
   - Indicadores como `Daily_Log_Return`, `Daily_Return`, `Donchian_Channel`, `Vortex`, `PPO`, `ROC` se calculan ahora con fórmulas exactas inline en MQL5 (`MathLog(iClose(1)/iClose(2))`, `iHighest/iLowest`, etc.) en lugar de medias móviles `iMA` genéricas.
   - Esto permite que cuando el precio cae en una vela, `Daily_Log_Return` se vuelva negativo en MQL5 (e.g. `-0.002`), provocando que `buy_condition` cambie a falso y activando el cierre inmediato de la posición.

2. **Control Estricto de Posiciones (Two-Pass Loop)**:
   - Recorrido de posiciones con `ticket > 0` y `PositionSelectByTicket(ticket)`.
   - Cierre forzoso de compras cuando `!buy_condition` es verdadero.
   - Apertura de órdenes condicionada a que la cuenta esté totalmente plana (`!has_position`).

---

## 3. Guía de Ejecución y Comandos

### Iniciar Redis (Docker):
```bash
cd /Users/alejandropulido/Documents/software-projects/trading/algoforge
docker compose up -d
```

### Iniciar Backend (FastAPI):
```bash
cd /Users/alejandropulido/Documents/software-projects/trading/algoforge/backend
source venv/bin/activate
uvicorn algoforge.main:app --reload --port 8000
```

### Iniciar Celery Worker (macOS):
```bash
cd /Users/alejandropulido/Documents/software-projects/trading/algoforge/backend
source venv/bin/activate
celery -A workers.celery_app worker --pool=threads --loglevel=info
```

### Iniciar Frontend (Vite React):
```bash
cd /Users/alejandropulido/Documents/software-projects/trading/algoforge/frontend
npm run dev
```

### Ejecutar Tests:
```bash
cd /Users/alejandropulido/Documents/software-projects/trading/algoforge/backend
./venv/bin/pytest tests/ -v
```
