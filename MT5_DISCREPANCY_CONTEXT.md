# Contexto de Depuración: AlgoForge Python Simulator vs MetaTrader 5 MQL5 EA

## 1. Descripción del Sistema
**AlgoForge** es un motor de generación de estrategias de trading impulsado por Inteligencia Artificial (Genetic Programming). 
- El backend evalúa árboles lógicos (ej. `gt(mul(Bollinger_Bands, Stochastic), c_80)`) contra datos históricos usando la librería de análisis técnico `ta` en Python.
- Utiliza un simulador vectorizado (`MT5TradeSimulator` en `mt5_simulator.py`) que imita el comportamiento de MT5 evaluando señales intrabarra y generando métricas de rendimiento (Sharpe, Profit Factor, Win Rate).
- Exporta la mejor estrategia a un Expert Advisor (EA) en MQL5 (`mt5_exporter.py`).

## 2. El Problema
Las estrategias generadas muestran resultados **impresionantes** (grandes ganancias, alto ratio Sharpe) en el simulador de AlgoForge usando Python. Sin embargo, al compilar el código MQL5 generado y correr el backtest en la plataforma **MetaTrader 5 (Strategy Tester)** sobre el mismo activo y temporalidad, la estrategia **arroja pérdidas severas**, bajo Profit Factor (< 1.0) y cientos de operaciones perdedoras.

Incluso cuando el usuario programó manualmente la regla `(BB * Stoch > 80)` en MQL5, obtuvo exactamente el mismo resultado pésimo que el EA autogenerado por AlgoForge.

## 3. Investigaciones Realizadas y Parches Aplicados (Lo que ya se resolvió)
Durante las sesiones anteriores, se descubrieron y corrigieron las siguientes inconsistencias en cómo el exportador de MQL5 mapeaba los indicadores de Python (`ta`):

1. **Bollinger Bands (%B vs MA Line):** 
   - *Python (`ta`):* Calculaba `%B` (un valor normalizado entre 0 y 1).
   - *MQL5:* El exportador estaba llamando al buffer 0 de `iBands` (la línea de media móvil), devolviendo el precio del activo (ej. `1.1000`). Esto hacía que `Precio * Stoch > 80` fuera siempre verdadero, inundando el bot de señales falsas.
   - *Fix:* Se inyectó código *custom* en `mt5_exporter.py` para calcular el `%B` idéntico a Python `(Close - Lower) / (Upper - Lower)`.
2. **Stochastic (Raw %K vs Smoothed):**
   - *Python (`ta`):* La función `stoch()` devuelve la línea %K cruda (sin suavizado).
   - *MQL5:* `iStochastic` usa un parámetro `slowing` por defecto de 3, suavizando la señal.
   - *Fix:* Se forzó `InpStochSlowing = 1` en el generador MQL5.
3. **Keltner / Donchian Channels y MACD:**
   - Se aplicaron parches similares para exportar `%KC`, `%DC` y el Histograma de MACD (MACD_Diff) en lugar de las líneas base.
4. **Verificación de Lookahead Bias (Sesgo de Futuro):**
   - Se validó el bucle de `mt5_simulator.py`. Las señales generadas con la vela cerrada `i` (`Close[i]`) se guardan en `deferred_entries` y se ejecutan estrictamente en el precio de apertura de la siguiente vela `i+1` (`Open[i+1]`). **No hay lookahead bias en la lógica de entrada del simulador Python.**

## 4. Hipótesis Restantes y Puntos de Acción para la IA Analista
Dado que, a pesar de los parches de indicadores, MT5 sigue reportando pérdidas, la IA especializada debe investigar los siguientes vectores:

### A. Ejecución de Backtest y Costos (Spread / Deslizamiento)
El simulador de Python (`MT5TradeSimulator`) asume ejecuciones perfectas al precio de apertura (`Open`) y solo descuenta una comisión por lote. 
- **En MT5:** Las compras se ejecutan al **Ask** y las ventas al **Bid**. 
- **Verificar:** Si la estrategia hace casi 1000 operaciones en pocos meses, el spread bid/ask de MT5 está destruyendo el edge (rentabilidad) que el simulador Python ignora. El simulador Python debe ser ajustado para castigar el spread o incluir simulación de Bid/Ask.

### B. Diferencia en los Datos Base (Data Mismatch)
- **Verificar:** ¿Los datos CSV/YFinance descargados en el Data Manager de AlgoForge coinciden vela a vela (Open/High/Low/Close) con los datos del broker de MetaTrader 5? Una diferencia en el huso horario (GMT+2 vs UTC) provoca que las velas de H1 no coincidan, alterando todos los valores de los indicadores.

### C. Evaluación Intrabarra (Intrabar SL/TP)
En `mt5_simulator.py`, durante la evaluación (Fase 3), se verifica si el `Low` toca el Stop Loss y el `High` toca el Take Profit:
```python
if pos["sl"] > 0.0 and curr_low <= pos["sl"]:
    exit_price = pos["sl"]
    exit_reason = "sl"
    closed = True
```
- **Problema Potencial:** El simulador asume que la orden se cierra exactamente en el precio del Stop Loss, lo cual ignora "gaps" (huecos) de mercado. Adicionalmente, si el SL y el TP se tocan en la misma vela (por volatilidad extrema), el simulador Python asume estáticamente que el SL se tocó primero. En MT5 en modo "Every Tick", la secuencia real del tick determinará el resultado, generando gran diferencia.

### D. Valores Cero o NaN en los Indicadores al Inicio (Burn-in Period)
- Los indicadores en Python usan `bfill()` (Backfill) para rellenar los primeros valores (NaN) generados por el período de ventana (ej. los primeros 20 periodos de una media móvil). 
- MT5 simplemente devuelve `0` o rechaza el buffer en esas velas. Si el simulador toma decisiones en las primeras barras basado en datos retro-proyectados (`bfill`), esto es un lookahead bias temporal al principio del set de datos.

### E. Lógica "Signal Exit" Mismatch
En `mt5_simulator.py` (Fase 5), un trade Long se cierra ("deferred_exit") si aparece una señal de venta (`sell_signals[i]`). 
- **Verificar:** Asegurarse de que el MQL5 exportado implemente correctamente esta inversión/cierre de posiciones basado en señales opuestas (Signal Exits) exactamente en el mismo tick.

**Misión para la IA Especializada:** Revisa el código de `backend/engine/backtester/mt5_simulator.py`, examina la lógica en el exportador MQL5, analiza las diferencias descritas, y reestructura el simulador Python o el generador de MT5 para que los PnL sean idénticos, garantizando que AlgoForge genere simulaciones ultra realistas.
