# Contexto de Depuración: AlgoForge Python Simulator vs MetaTrader 5 MQL5 EA

## 1. Descripción del Sistema
**AlgoForge** es un motor de generación de estrategias de trading impulsado por Inteligencia Artificial (Genetic Programming).
- El backend evalúa árboles lógicos (ej. `gt(mul(Bollinger_Bands, Stochastic), c_80)`) contra datos históricos usando la librería de análisis técnico `ta` en Python.
- Utiliza un simulador vectorizado (`MT5TradeSimulator` en `mt5_simulator.py`) que imita el comportamiento de MT5 evaluando señales intrabarra y generando métricas de rendimiento (Sharpe, Profit Factor, Win Rate).
- Exporta la mejor estrategia a un Expert Advisor (EA) en MQL5 (`mt5_exporter.py`).

## 2. El Problema
Las estrategias generadas muestran resultados **impresionantes** (grandes ganancias, alto ratio Sharpe) en el simulador de AlgoForge usando Python. Sin embargo, al compilar el código MQL5 generado y correr el backtest en la plataforma **MetaTrader 5 (Strategy Tester)** sobre el mismo activo y temporalidad, la estrategia **arroja pérdidas severas**, bajo Profit Factor (< 1.0) y cientos de operaciones perdedoras.

Incluso cuando el usuario programó manualmente la regla `(BB * Stoch > 80)` en MQL5, obtuvo exactamente el mismo resultado pésimo que el EA autogenerado por AlgoForge.

## 3. CAUSA RAÍZ ENCONTRADA (Resuelto en esta sesión)

El problema NO era un único bug: era la **combinación de (A) un simulador sin costos de mercado y (B) varios sesgos/paridades rotas** que inflaban el PnL del lado Python. Los arreglos aplicados:

### A. El simulador Python ignoraba los costos que MT5 cobra SIEMPRE (driver principal)

| Costo | Simulador (antes) | MetaTrader 5 (real) | Fix aplicado |
|---|---|---|---|
| **Spread Bid/Ask** | Entra y sale al precio medio `Open` (gratis) | Compra al **Ask**, vende al **Bid** → ~1 spread completo por round-trip | Nuevo config `spreadPips` (default 1.0). Entradas: `Open ± spread/2`. Salidas por señal: `Open ∓ spread/2`. SL/TP siguen llenando al nivel exacto (como el broker). |
| **Comisión** | 1 cargo por round-trip (`lots × commissionPerLot`) | Cobrada **por deal** (entrada Y salida) → el doble | `commissionPerSide` (default `true`) → cargo en entrada + salida. `false` conserva el comportamiento legacy (1 cargo). |
| **Swap overnight** | No modelado | Cobrado por cada noche que la posición cruza 00:00 | Nuevo config `swapPerLotPerDay` (default 0). Se descuenta `días retenidos × swap × lots` al cerrar. |

Con ~600-1000 operaciones (lo que la GP tiende a generar), solo el spread + comisión doble + swap representan miles de dólares de arrastre que el simulador regalaba. Un edge de 2-3 pips por trade (que luce "impresionante" sin costos) se convierte en pérdida neta en MT5.

**Configuración requerida por el usuario:** el simulador ahora tiene defaults realistas, pero se recomienda pasar en `risk_config` los valores del broker:
```json
{
  "spreadPips": 1.2,
  "commissionPerLot": 7.0,
  "commissionPerSide": true,
  "swapPerLotPerDay": 1.5
}
```
(ajustar por símbolo; estos parámetros fluyen automáticamente por `risk_config`, no requieren cambios de schema.)

### B. Sesgos que inflaban el edge en Python

1. **Lookahead por `bfill()` en el calculador de indicadores** (`calculator.py`): los primeros `window` valores NaN se rellenaban con **datos futuros** (¡lookahead real!), fabricando señales en las primeras velas del dataset. MT5 no tiene esos valores. **Fix:** `fillna(0)` (buffer "vacío", como MT5 devuelve `EMPTY_VALUE`). Ya no se opera con datos del futuro.
2. **ATR off-by-one en el SL/TP de entrada** (`mt5_simulator.py`): el simulador calculaba SL/TP con la ATR de la vela **en curso** (aún sin cerrar); MT5 usa la ATR de la **última vela cerrada**. **Fix:** las entradas market usan `atr_array[i-1]`.
3. **Sizing con balance realizado en vez de equity** (`mt5_simulator.py`): MT5 dimensiona con `ACCOUNT_EQUITY` (balance + flotante); Python usaba solo balance, sobre-dimensionando en drawdowns. **Fix:** `_calc_lots` recibe `balance + unrealized_pnl`.

### C. Paridad matemática rota en el MQL5 exportado (`mt5_exporter.py`)

1. **Conversión de pips**: `InpX * 10.0 * point` solo es correcto en símbolos de 5/3 dígitos; en símbolos de 4 dígitos el SL/TP era 10× más grande. **Fix:** helper `pip_size = (_Digits == 3 || _Digits == 5) ? point * 10.0 : point`.
2. **PPO**: el código inline NO era PPO (era un ROC de 11 velas: `(close[1]-close[12])/close[12]`). **Fix:** `((EMA_fast - EMA_slow) / EMA_slow) * 100` con `iMA(..., shift=1)` (la llamada `iMA()` sin shift usaba la vela en formación = lookahead).
3. **Vortex**: era un ratio de 1 vela; `ta` suma `|high - low.shift(1)|` y el True Range sobre la ventana. **Fix:** loop inline idéntico a `ta.trend.VortexIndicator`.
4. **Cumulative Return**: era un retorno de 20 velas; `ta` lo define como `(close / close.iloc[0] - 1) * 100` (serie completa). **Fix:** inline contra el primer close de la historia.
5. **HMA / KAMA / VWAP**: eran `iMA` aproximados que NO coinciden con `ta`. **Fix:** implementaciones inline que replican exactamente el cálculo de `ta`/`IndicatorCalculator` (SMA-diff-smoothed para HMA, recursión de eficiencia para KAMA, suma ponderada por volumen para VWAP).
6. **Exit por señal con `= 0`**: el simulador cierra long con `raw <= 0` (y abre short con `<= 0`); el EA solo reaccionaba con `< 0`. **Fix:** `sell_condition = (signal_val <= 0.0)` en el EA.
7. **Off-by-one en `Bars()`**: `Bars()` cuenta ambas velas límite (inclusivo), así que `maxHoldingBars` y el timeout de pendientes se disparaban 1 vela antes que el simulador. **Fix:** `Bars(...) - 1` en ambos casos.

## 4. Lo que ya se había resuelto en sesiones anteriores (se mantiene)
1. **Bollinger Bands (%B)**: `iBands` buffer 0 es la línea MA (precio), no `%B`. Se inyecta `%B = (Close - Lower) / (Upper - Lower)` idéntico a Python.
2. **Stochastic**: `InpStochSlowing = 1` para %K crudo sin suavizado (paridad con `ta`).
3. **Keltner / Donchian / MACD**: exportan `%KC`, `%DC` y `MACD_Diff` en lugar de las líneas base.
4. **Sin lookahead en la entrada**: las señales de la vela `i` se ejecutan al `Open[i+1]` (verificado).

## 5. Recomendaciones restantes para el usuario (no son bugs de AlgoForge)

1. **Modo del Strategy Tester**: para paridad exacta usa **"Open prices only"** (llena al open de vela, como el simulador). En "Every tick" la primera ejecución del EA ocurre al primer tick real, que puede diferir unos pips del open — el simulador no puede replicar el tick-by-tick del broker.
2. **Configura el simulador con los costos de TU broker** (`spreadPips`, `commissionPerLot`, `commissionPerSide`, `swapPerLotPerDay`) ANTES de dejar que la GP optimice; así la evolución ya descarta estrategias que solo viven del spread gratis.
3. **Datos idénticos**: verifica que el CSV descargado (huso horario GMT+2 vs UTC) coincida vela a vela con el broker; un shift de velas cambia todos los indicadores. Descarga con historial de calentamiento (warmup) previo al rango de test.
4. **Evaluación intrabarra SL/TP**: si SL y TP se tocan en la misma vela, el simulador asume SL primero (conservador); MT5 decide por orden de ticks. La diferencia es marginal y no favorece al simulador.
5. **Margen**: MT5 rechaza órdenes sin margen; el simulador no modela margen. Con `risk_pct` moderado y sin over-leverage esto no debería divergir.

## 6. Verificación
- `backend/tests/`: 17 tests pasan, incluidos los nuevos `test_mt5_simulator_spread_commission_swap_costs` y `test_mt5_simulator_atr_uses_last_closed_bar`.
- Demostración empírica en EURUSD 5m (1 mes, regla `BB*Stoch>80`): con 614 operaciones el spread + comisión + swap suman ~$1,900 de drag que el simulador anterior regalaba.
- Exportación MQL5 generada para la regla reportada (`gt(mul(Bollinger_Bands, Stochastic), c_80)`) con `%B`, `%K` crudo, `pip_size`, `sell_condition <= 0` y `Bars()-1`: estructuralmente válida.