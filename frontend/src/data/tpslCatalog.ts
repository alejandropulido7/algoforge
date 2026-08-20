export interface TPSLParamDef {
  key: string;
  name: string;
  defaultMin: number;
  defaultStep: number;
  defaultMax: number;
  labelHelp: string;
  description: string;
}

export interface TPSLModeItem {
  id: string;
  name: string;
  desc: string;
  badge: string;
  params: TPSLParamDef[];
}

export const TPSL_CATALOG: TPSLModeItem[] = [
  {
    id: 'atr_classic',
    name: 'ATR (clásico)',
    badge: 'Volatilidad',
    desc: 'Stop Loss y Take Profit dinámicos basados en la volatilidad real del ATR (14 periodos).',
    params: [
      {
        key: 'sl_atr',
        name: 'Stop Loss (×ATR)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 3.0,
        labelHelp: 'Distancia de SL en múltiplos del ATR de 14 periodos',
        description: 'Coloca el Stop Loss a X veces la volatilidad media del mercado. Un valor mayor permite que la operación respire ante el ruido del precio.'
      },
      {
        key: 'tp_atr',
        name: 'Take Profit (×ATR)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 6.0,
        labelHelp: 'Distancia de TP en múltiplos del ATR de 14 periodos',
        description: 'Objetivo de ganancias proporcional a la volatilidad del activo para capturar extensiones de tendencia.'
      }
    ]
  },
  {
    id: 'trailing_stop',
    name: 'Trailing Stop',
    badge: 'Dinámico',
    desc: 'Arrastra el Stop Loss detrás del precio a medida que avanza a favor de la posición.',
    params: [
      {
        key: 'trail_atr',
        name: 'Distancia trail (×ATR)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 2.5,
        labelHelp: 'Holgura del trailing stop respecto al precio máximo/mínimo alcanzado',
        description: 'Mueve el SL protegiendo las ganancias a una distancia de X ATR del punto más alto (en compras) o más bajo (en ventas) alcanzado durante el trade.'
      }
    ]
  },
  {
    id: 'swing_structure',
    name: 'Estructura (Swing)',
    badge: 'Price Action',
    desc: 'Fija el SL en el último mínimo (compras) o máximo (ventas) relevante de mercado.',
    params: [
      {
        key: 'lookback',
        name: 'Velas de lookback',
        defaultMin: 10,
        defaultStep: 5,
        defaultMax: 50,
        labelHelp: 'Número de velas hacia atrás para buscar el soporte/resistencia swing',
        description: 'Para compras, coloca el Stop Loss por debajo del precio mínimo de las últimas N velas. Para ventas, por encima del precio máximo.'
      }
    ]
  },
  {
    id: 'time_exit',
    name: 'Salida por tiempo',
    badge: 'Temporal',
    desc: 'Cierra obligatoriamente la posición si transcurre un número determinado de velas.',
    params: [
      {
        key: 'max_bars',
        name: 'Máx. velas en trade',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 12,
        labelHelp: 'Velas máximas que puede durar la posición antes de forzar el cierre',
        description: 'Evita quedar atrapado en consolidaciones laterales cerrando la posición al cumplirse N velas desde la entrada.'
      }
    ]
  },
  {
    id: 'percentage',
    name: 'Porcentaje',
    badge: 'Proporcional',
    desc: 'Stop Loss y Take Profit fijos porcentuales sobre el precio de apertura.',
    params: [
      {
        key: 'sl_pct',
        name: 'Stop Loss (%)',
        defaultMin: 0.2,
        defaultStep: 0.1,
        defaultMax: 2.0,
        labelHelp: 'Pérdida máxima porcentual permitida respecto al precio de entrada',
        description: 'Fija el Stop Loss a una distancia fija de X% respecto al precio al que se abrió la posición.'
      },
      {
        key: 'tp_pct',
        name: 'Take Profit (%)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 4.0,
        labelHelp: 'Ganancia porcentual objetivo sobre el precio de entrada',
        description: 'Fija el Take Profit a una distancia fija de X% respecto al precio al que se abrió la posición.'
      }
    ]
  },
  {
    id: 'partial_tp',
    name: 'TP Parcial',
    badge: 'Escalado',
    desc: 'Toma beneficios parciales cerrando una fracción de la posición y deja correr el resto.',
    params: [
      {
        key: 'tp1_atr',
        name: 'Primer TP (×ATR)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 2.0,
        labelHelp: 'Distancia para el primer objetivo de beneficio',
        description: 'Nivel donde se asegura la primera parte de las ganancias.'
      },
      {
        key: 'tp2_atr',
        name: 'Segundo TP (×ATR)',
        defaultMin: 2.0,
        defaultStep: 0.1,
        defaultMax: 6.0,
        labelHelp: 'Distancia para el objetivo final de beneficio',
        description: 'Nivel donde se liquida el remanente de la posición.'
      },
      {
        key: 'close_pct',
        name: '% cerrado en TP1',
        defaultMin: 30,
        defaultStep: 10,
        defaultMax: 70,
        labelHelp: 'Porcentaje del volumen total que se cierra al tocar TP1',
        description: 'Porción del lotaje a monetizar en TP1 (ej: 50% cierra la mitad y deja el 50% restante correr a TP2).'
      }
    ]
  },
  {
    id: 'breakeven',
    name: 'Breakeven',
    badge: 'Protección',
    desc: 'Mueve el Stop Loss al precio de entrada tan pronto la posición alcanza cierto beneficio.',
    params: [
      {
        key: 'be_atr',
        name: 'Activación (×ATR profit)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 2.0,
        labelHelp: 'Beneficio flotante requerido para mover el SL al precio de apertura',
        description: 'Cuando la ganancia flotante supera X veces el ATR, el Stop Loss se traslada al precio de entrada garantizando un trade libre de riesgo.'
      }
    ]
  },
  {
    id: 'fixed_pips',
    name: 'Pips fijos',
    badge: 'Absoluto',
    desc: 'Stop Loss y Take Profit fijos en distancia de pips/puntos.',
    params: [
      {
        key: 'sl_pips',
        name: 'Stop Loss (pips)',
        defaultMin: 10,
        defaultStep: 5,
        defaultMax: 50,
        labelHelp: 'Distancia fija en pips para el Stop Loss',
        description: 'Puntos absolutos de protección respecto al precio de entrada.'
      },
      {
        key: 'tp_pips',
        name: 'Take Profit (pips)',
        defaultMin: 20,
        defaultStep: 5,
        defaultMax: 100,
        labelHelp: 'Distancia fija en pips para el Take Profit',
        description: 'Puntos absolutos de toma de beneficios.'
      }
    ]
  },
  {
    id: 'smoothed_atr',
    name: 'ATR suavizado',
    badge: 'Macro Volatilidad',
    desc: 'Stop Loss y Take Profit calculados sobre un ATR de largo plazo (50 periodos).',
    params: [
      {
        key: 'sl_atr_smooth',
        name: 'Stop Loss (×ATR_50)',
        defaultMin: 0.5,
        defaultStep: 0.1,
        defaultMax: 3.0,
        labelHelp: 'Distancia de SL multiplicada por el ATR de 50 periodos',
        description: 'Filtra la volatilidad estacional usando un promedio amplio de 50 barras para stops más estables.'
      },
      {
        key: 'tp_atr_smooth',
        name: 'Take Profit (×ATR_50)',
        defaultMin: 1.0,
        defaultStep: 0.1,
        defaultMax: 6.0,
        labelHelp: 'Distancia de TP multiplicada por el ATR de 50 periodos',
        description: 'Objetivo de ganancias proporcional a la tendencia amplia de volatilidad.'
      }
    ]
  }
];

export const getTPSLModeItem = (id: string): TPSLModeItem | undefined => {
  return TPSL_CATALOG.find(item => item.id.toLowerCase() === id.toLowerCase());
};

export const calculateTotalTPSLCombinations = (
  selectedModeIds: string[],
  ranges: Record<string, Record<string, { min: number; step: number; max: number }>> = {}
): string => {
  let total = BigInt(1);
  let hasAnyParam = false;

  for (const id of selectedModeIds) {
    const item = getTPSLModeItem(id);
    if (!item || item.params.length === 0) continue;

    for (const p of item.params) {
      const userRange = ranges[item.id]?.[p.key] || {
        min: p.defaultMin,
        step: p.defaultStep,
        max: p.defaultMax
      };

      const step = userRange.step > 0 ? userRange.step : 1;
      const count = Math.max(1, Math.floor(Math.round(((userRange.max - userRange.min) / step) * 1000) / 1000) + 1);
      total *= BigInt(count);
      hasAnyParam = true;
    }
  }

  if (!hasAnyParam) return '0';
  return total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};
