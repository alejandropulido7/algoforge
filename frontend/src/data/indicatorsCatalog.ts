export interface ParamRangeDef {
  key: string;
  name: string;
  defaultMin: number;
  defaultStep: number;
  defaultMax: number;
  labelHelp: string;
  description: string;
}

export interface IndicatorCatalogItem {
  id: string;
  name: string;
  category: 'momentum' | 'trend' | 'volatility' | 'volume' | 'overlap' | 'custom' | 'others';
  desc: string;
  params: ParamRangeDef[];
}

export const INDICATORS_CATALOG: IndicatorCatalogItem[] = [
  // === 1. MOMENTUM ===
  {
    id: 'RSI',
    name: 'RSI',
    category: 'momentum',
    desc: 'Relative Strength Index (Oscilador de Fuerza Relativa)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Velas históricas analizadas para el cálculo del momentum',
        description: 'Cantidad de velas pasadas para promediar ganancias y pérdidas. Periodos cortos (5-9) hacen al oscilador muy rápido y reactivo; periodos largos (21-30) filtran el ruido y confirman la fuerza de la tendencia.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: 20,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Nivel inferior donde el precio se considera devaluado',
        description: 'Umbral en la escala 0-100 para activar compras. Si el RSI cae por debajo de este valor y gira hacia arriba, anticipa un posible rebote alcista.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 65,
        defaultStep: 1,
        defaultMax: 80,
        labelHelp: 'Nivel superior donde el precio se considera sobrecomprado',
        description: 'Umbral en la escala 0-100 para activar ventas. Si el RSI supera este nivel, anticipa agotamiento de los compradores y potencial corrección bajista.'
      },
    ]
  },
  {
    id: 'Stochastic',
    name: 'Estocástico',
    category: 'momentum',
    desc: 'Oscilador Estocástico (Periodo, Sobrecompra y Sobreventa)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 25,
        labelHelp: 'Velas históricas para buscar el máximo y mínimo de precio',
        description: 'Número de velas pasadas (Lookback %K) donde se busca el máximo más alto y el mínimo más bajo para ubicar dónde cerró el precio actual en un rango de 0% a 100%.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: 15,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Umbral inferior para gatillar compras tras giro alcista',
        description: 'Nivel de la escala 0-100 donde el activo se considera sobrevendido (típicamente 20). Si el estocástico cae por debajo y gira al alza, genera señal de compra.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 70,
        defaultStep: 1,
        defaultMax: 85,
        labelHelp: 'Umbral superior para gatillar ventas tras agotamiento',
        description: 'Nivel de la escala 0-100 donde el activo se considera sobrecomprado (típicamente 80). Si el estocástico sube por encima y gira a la baja, genera señal de venta.'
      },
    ]
  },
  {
    id: 'StochRSI',
    name: 'StochRSI',
    category: 'momentum',
    desc: 'Estocástico aplicado sobre el RSI',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 21,
        labelHelp: 'Velas para el cálculo de la serie base',
        description: 'Lookback para el cálculo del oscilador estocástico sobre el RSI.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: 15,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Nivel de sobreventa en StochRSI (típicamente 20)',
        description: 'Nivel inferior de sobreventa para detectar suelos inmediatos.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 70,
        defaultStep: 1,
        defaultMax: 85,
        labelHelp: 'Nivel de sobrecompra en StochRSI (típicamente 80)',
        description: 'Nivel superior de sobrecompra para detectar techos y agotamiento.'
      },
    ]
  },
  {
    id: 'TSI',
    name: 'TSI',
    category: 'momentum',
    desc: 'True Strength Index (Momentum de Doble Suavizado)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Lookback de suavizado de variaciones de precio',
        description: 'Velas de media exponencial aplicadas para eliminar el ruido y captar el momentum suave.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: -35,
        defaultStep: 5,
        defaultMax: -15,
        labelHelp: 'Nivel inferior negativo de sobreventa',
        description: 'Nivel de soporte oscilatorio para gatillar compras tras caídas extremas.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 15,
        defaultStep: 5,
        defaultMax: 35,
        labelHelp: 'Nivel superior positivo de sobrecompra',
        description: 'Nivel de resistencia oscilatoria para gatillar salidas o ventas.'
      },
    ]
  },
  {
    id: 'UltimateOscillator',
    name: 'UO',
    category: 'momentum',
    desc: 'Ultimate Oscillator (Triple Marco Temporal)',
    params: [
      {
        key: 'period',
        name: 'Periodo Base',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 21,
        labelHelp: 'Lookback base para los 3 ciclos temporales (7, 14, 28)',
        description: 'Calcula y pondera la presión de compra a corto, mediano y largo plazo para evitar falsas divergencias.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: 25,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Umbral de sobreventa (típicamente 30)',
        description: 'Nivel de sobreventa en el oscilador combinado.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 65,
        defaultStep: 1,
        defaultMax: 75,
        labelHelp: 'Umbral de sobrecompra (típicamente 70)',
        description: 'Nivel de sobrecompra en el oscilador combinado.'
      },
    ]
  },
  {
    id: 'WilliamsR',
    name: 'WilliamsR',
    category: 'momentum',
    desc: 'Williams %R (Rango Porcentual de Larry Williams)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Número de velas para comparar el cierre vs rango High/Low',
        description: 'Mide la distancia del precio de cierre respecto al máximo del periodo en una escala negativa de 0 a -100.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: -90,
        defaultStep: 5,
        defaultMax: -75,
        labelHelp: 'Nivel inferior de sobreventa (ej. -80)',
        description: 'Lecturas por debajo de este nivel indican precio comprimido en el suelo.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: -25,
        defaultStep: 5,
        defaultMax: -10,
        labelHelp: 'Nivel superior de sobrecompra (ej. -20)',
        description: 'Lecturas por encima de este nivel indican precio pegado al techo.'
      }
    ]
  },
  {
    id: 'AO',
    name: 'AO',
    category: 'momentum',
    desc: 'Awesome Oscillator de Bill Williams',
    params: [
      {
        key: 'period',
        name: 'Periodo Rápido',
        defaultMin: 3,
        defaultStep: 1,
        defaultMax: 10,
        labelHelp: 'Media aritmética corta de precios medianos (típicamente 5)',
        description: 'Promedio rápido del precio medio (High + Low)/2 para detectar aceleración inmediata del mercado.'
      }
    ]
  },
  {
    id: 'KAMA',
    name: 'KAMA',
    category: 'momentum',
    desc: 'Kaufman Adaptive Moving Average',
    params: [
      {
        key: 'period',
        name: 'Periodo Eficiencia',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 25,
        labelHelp: 'Velas para medir la relación entre dirección y volatilidad',
        description: 'Calcula el Ratio de Eficiencia (ER). Si el mercado avanza limpiamente sin ruido, la media acelera; si está en rango lateral, se frena.'
      }
    ]
  },
  {
    id: 'ROC',
    name: 'ROC',
    category: 'momentum',
    desc: 'Rate of Change (Tasa de Cambio Porcentual)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Velas hacia atrás para medir la velocidad de subida/bajada',
        description: 'Mide la velocidad pura del cambio de precio entre la vela actual y la vela de hace N periodos en términos porcentuales.'
      }
    ]
  },
  {
    id: 'PPO',
    name: 'PPO',
    category: 'momentum',
    desc: 'Percentage Price Oscillator (MACD Porcentual)',
    params: [
      {
        key: 'fast',
        name: 'Periodo Rápido',
        defaultMin: 8,
        defaultStep: 1,
        defaultMax: 16,
        labelHelp: 'Periodo EMA corto (típicamente 12)',
        description: 'Media móvil exponencial de corto plazo en porcentaje.'
      },
      {
        key: 'slow',
        name: 'Periodo Lento',
        defaultMin: 20,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Periodo EMA largo (típicamente 26)',
        description: 'Media móvil exponencial de mediano/largo plazo en porcentaje.'
      }
    ]
  },
  {
    id: 'PVO',
    name: 'PVO',
    category: 'momentum',
    desc: 'Percentage Volume Oscillator (Momentum de Volumen)',
    params: [
      {
        key: 'fast',
        name: 'Volumen Rápido',
        defaultMin: 8,
        defaultStep: 1,
        defaultMax: 16,
        labelHelp: 'EMA rápida de volumen negociado',
        description: 'Media móvil exponencial de volumen a corto plazo.'
      },
      {
        key: 'slow',
        name: 'Volumen Lento',
        defaultMin: 20,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'EMA lenta de volumen negociado',
        description: 'Media móvil exponencial de volumen de fondo.'
      }
    ]
  },

  // === 2. TREND & OVERLAP ===
  {
    id: 'MACD',
    name: 'MACD',
    category: 'trend',
    desc: 'Moving Average Convergence Divergence',
    params: [
      {
        key: 'fast',
        name: 'Periodo Rápido',
        defaultMin: 8,
        defaultStep: 1,
        defaultMax: 16,
        labelHelp: 'Media móvil exponencial de corto plazo (típicamente 12)',
        description: 'Sigue los movimientos inmediatos del precio y lidera los giros de tendencia.'
      },
      {
        key: 'slow',
        name: 'Periodo Lento',
        defaultMin: 20,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Media móvil exponencial de fondo (típicamente 26)',
        description: 'Representa la tendencia estructural de mercado sobre la que se compara el impulso rápido.'
      },
      {
        key: 'signal',
        name: 'Periodo Señal',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 15,
        labelHelp: 'Suavizado del diferencial MACD (típicamente 9)',
        description: 'Media exponencial aplicada a la línea MACD. La divergencia o cruce genera el histograma de trading.'
      }
    ]
  },
  {
    id: 'MACross',
    name: 'MA cruce',
    category: 'trend',
    desc: 'Filtro Direccional de Medias Móviles',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 5,
        defaultMax: 200,
        labelHelp: 'Velas de la media móvil para sesgo de tendencia',
        description: 'Define si el bot solo opera a favor de la tendencia macro (ej. solo compras cuando el precio está sobre la media).'
      }
    ]
  },
  {
    id: 'EMA',
    name: 'EMA',
    category: 'trend',
    desc: 'Exponential Moving Average (Media Móvil Exponencial)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 5,
        defaultMax: 200,
        labelHelp: 'Velas promediadas con mayor peso en las más recientes',
        description: 'Otorga mayor ponderación a las velas recientes, reduciendo el retraso respecto a una media simple.'
      }
    ]
  },
  {
    id: 'SMA',
    name: 'SMA',
    category: 'trend',
    desc: 'Simple Moving Average (Media Móvil Simple)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 5,
        defaultMax: 200,
        labelHelp: 'Promedio aritmético exacto de los cierres',
        description: 'Media aritmética estándar utilizada por inversores institucionales como soporte/resistencia dinámico.'
      }
    ]
  },
  {
    id: 'WMA',
    name: 'WMA',
    category: 'trend',
    desc: 'Weighted Moving Average (Media Ponderada Lineal)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 50,
        labelHelp: 'Ponderación lineal progresiva de velas',
        description: 'Multiplica cada barra por su peso cronológico, haciéndola más reactiva que la SMA pero más suave que la EMA.'
      }
    ]
  },
  {
    id: 'HMA',
    name: 'HMA',
    category: 'trend',
    desc: 'Hull Moving Average (Media Hull de Cero Retraso)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 8,
        defaultStep: 2,
        defaultMax: 100,
        labelHelp: 'Algoritmo de Alan Hull que casi elimina el lag',
        description: 'Combina WMAs de periodos fraccionados y raíz cuadrada para responder casi de forma instantánea a los giros del precio.'
      }
    ]
  },
  {
    id: 'ADX',
    name: 'ADX',
    category: 'trend',
    desc: 'Average Directional Index (Fuerza de Tendencia)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Lookback para cuantificar si hay tendencia activa',
        description: 'Mide qué tan fuerte es la tendencia independientemente de si sube o baja.'
      },
      {
        key: 'trend_level',
        name: 'Umbral Tendencia',
        defaultMin: 20,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Nivel mínimo para confirmar tendencia (típicamente 25)',
        description: 'Valores por encima de este umbral indican que el mercado está en tendencia firme y no en rango lateral.'
      }
    ]
  },
  {
    id: 'Aroon',
    name: 'Aroon',
    category: 'trend',
    desc: 'Oscilador Aroon (Aroon Up / Down)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 50,
        labelHelp: 'Velas analizadas desde el último nuevo máximo o mínimo',
        description: 'Mide el tiempo transcurrido desde el último máximo relativo (Aroon Up) y el último mínimo relativo (Aroon Down) para predecir rupturas.'
      }
    ]
  },
  {
    id: 'CCI',
    name: 'CCI',
    category: 'trend',
    desc: 'Commodity Channel Index (Canal de Desviación Cíclica)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 40,
        labelHelp: 'Velas para comparar el precio típico vs su media estadística',
        description: 'Mide la variación del precio típico respecto a su media estadística dividida por la desviación media para detectar extremos cíclicos.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: -150,
        defaultStep: 10,
        defaultMax: -80,
        labelHelp: 'Nivel inferior de sobreventa (típicamente -100)',
        description: 'Lecturas por debajo de este valor señalan compresión bajista excesiva.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 80,
        defaultStep: 10,
        defaultMax: 150,
        labelHelp: 'Nivel superior de sobrecompra (típicamente +100)',
        description: 'Lecturas por encima de este valor señalan extensión alcista extrema.'
      }
    ]
  },
  {
    id: 'ParabolicSAR',
    name: 'ParabolicSAR',
    category: 'trend',
    desc: 'Parabolic Stop and Reverse',
    params: [
      {
        key: 'step',
        name: 'Aceleración (Step)',
        defaultMin: 0.01,
        defaultStep: 0.01,
        defaultMax: 0.05,
        labelHelp: 'Incremento del trailing stop por cada nuevo máximo/mínimo',
        description: 'Factor en el que aumenta la velocidad del punto SAR por cada nueva barra a favor del trade.'
      },
      {
        key: 'max_step',
        name: 'Aceleración Máxima',
        defaultMin: 0.1,
        defaultStep: 0.05,
        defaultMax: 0.3,
        labelHelp: 'Límite de velocidad del Parabolic SAR',
        description: 'Tope máximo de aceleración para evitar que el trailing stop se pegue excesivamente al precio.'
      }
    ]
  },
  {
    id: 'SuperTrend',
    name: 'SuperTrend',
    category: 'trend',
    desc: 'SuperTrend (Envolvente Dinámica Basada en ATR)',
    params: [
      {
        key: 'period',
        name: 'Periodo ATR',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 21,
        labelHelp: 'Ventana de volatilidad promedio',
        description: 'Periodo de cálculo del Average True Range que dicta la holgura del stop de tendencia.'
      },
      {
        key: 'multiplier',
        name: 'Multiplicador',
        defaultMin: 1.5,
        defaultStep: 0.5,
        defaultMax: 4.5,
        labelHelp: 'Distancia en múltiplos ATR desde la media',
        description: 'Múltiplo de volatilidad que separa la línea de soporte/resistencia del precio. Un cruce cambia el color de la tendencia.'
      }
    ]
  },
  {
    id: 'Ichimoku',
    name: 'Ichimoku',
    category: 'trend',
    desc: 'Ichimoku Kinko Hyo (Gráfico de Equilibrio de Nube)',
    params: [
      {
        key: 'tenkan',
        name: 'Tenkan-sen',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 12,
        labelHelp: 'Punto medio de máximos/mínimos rápido (típicamente 9)',
        description: 'Promedio entre el punto más alto y más bajo de las últimas X velas (impulso a corto plazo).'
      },
      {
        key: 'kijun',
        name: 'Kijun-sen',
        defaultMin: 20,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Punto medio de máximos/mínimos intermedio (típicamente 26)',
        description: 'Nivel clave de equilibrio y soporte/resistencia mayor.'
      },
      {
        key: 'senkou',
        name: 'Senkou Span B',
        defaultMin: 45,
        defaultStep: 1,
        defaultMax: 65,
        labelHelp: 'Punto medio de largo plazo proyectado (típicamente 52)',
        description: 'Define el borde grueso de la nube (Kumo) para evaluar la tendencia a largo plazo.'
      }
    ]
  },
  {
    id: 'KST',
    name: 'KST',
    category: 'trend',
    desc: 'Know Sure Thing (Oscilador de 4 Ciclos ROC)',
    params: [
      {
        key: 'period',
        name: 'Periodo Señal',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 15,
        labelHelp: 'Media móvil sobre la fórmula compuesta de 4 ciclos',
        description: 'Suavizado de la fórmula ponderada de 4 tasas de cambio para generar cruces de confirmación.'
      }
    ]
  },
  {
    id: 'DPO',
    name: 'DPO',
    category: 'trend',
    desc: 'Detrended Price Oscillator (Oscilador Des-tendenciado)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Velas para desplazar la media y aislar ciclos puros',
        description: 'Elimina la tendencia a largo plazo del precio para identificar únicamente los ciclos recurrentes de corto plazo.'
      }
    ]
  },
  {
    id: 'TRIX',
    name: 'TRIX',
    category: 'trend',
    desc: 'Triple Smoothed Exponential Average',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 25,
        labelHelp: 'Lookback del triple filtro exponencial',
        description: 'Filtra ciclos menores insignificantes y muestra la dirección de la tendencia primaria a través de su tasa de cambio.'
      }
    ]
  },
  {
    id: 'MassIndex',
    name: 'MassIndex',
    category: 'trend',
    desc: 'Índice de Masa (Detector de Reversión de Rango)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 18,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Suma de la relación de rangos (típicamente 25)',
        description: 'Suma acumulada para identificar ensanchamientos de volatilidad que anticipan reversiones de tendencia.'
      }
    ]
  },
  {
    id: 'Vortex',
    name: 'Vortex',
    category: 'trend',
    desc: 'Vortex Indicator (Flujo de Vórtice VI+ y VI-)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 28,
        labelHelp: 'Velas para medir la distancia entre extremos consecutivos',
        description: 'Conecta los mínimos de hoy con los máximos de ayer (+VI) y los máximos de hoy con los mínimos de ayer (-VI).'
      }
    ]
  },
  {
    id: 'STC',
    name: 'STC',
    category: 'trend',
    desc: 'Schaff Trend Cycle (Ciclo de Tendencia Schaff)',
    params: [
      {
        key: 'period',
        name: 'Periodo Ciclo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 20,
        labelHelp: 'Periodo del oscilador estocástico aplicado',
        description: 'Ventana del suavizado estocástico para anticipar giros antes que el MACD tradicional.'
      }
    ]
  },

  // === 3. VOLATILITY ===
  {
    id: 'Bollinger',
    name: 'Bollinger',
    category: 'volatility',
    desc: 'Bandas de Bollinger (%B y Envolvente de Volatilidad)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 15,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Velas de la media móvil base SMA (típicamente 20)',
        description: 'Media aritmética central alrededor de la cual se calculan las desviaciones de volatilidad.'
      },
      {
        key: 'deviation',
        name: 'Desviación',
        defaultMin: 1.5,
        defaultStep: 0.1,
        defaultMax: 3.0,
        labelHelp: 'Anchura de las bandas en desviaciones típicas (ej. 2.0)',
        description: 'Define la amplitud del canal. Un multiplicador de 2.0 contiene estadísticamente el 95.4% de las fluctuaciones de precio.'
      }
    ]
  },
  {
    id: 'ATR',
    name: 'ATR',
    category: 'volatility',
    desc: 'Average True Range (Rango Verdadero Promedio)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 28,
        labelHelp: 'Velas para promediar la volatilidad en pips/puntos',
        description: 'Mide la distancia promedio entre máximos y mínimos considerando los gaps de apertura para dimensionar Stop Loss y Take Profit.'
      }
    ]
  },
  {
    id: 'Keltner',
    name: 'Keltner',
    category: 'volatility',
    desc: 'Canal de Keltner (Envolvente Basada en ATR)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Velas para el cálculo de la media típica y ATR',
        description: 'Proyecta un canal simétrico basado en la volatilidad real del ATR alrededor de la media de precios.'
      }
    ]
  },
  {
    id: 'Donchian',
    name: 'Donchian',
    category: 'volatility',
    desc: 'Canal de Donchian (Rupturas de Máximos y Mínimos)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 40,
        labelHelp: 'Velas para buscar el máximo y mínimo absoluto',
        description: 'Dibuja el canal entre el precio más alto y el más bajo de las últimas N barras para estrategias de breakout.'
      }
    ]
  },
  {
    id: 'UlcerIndex',
    name: 'UlcerIndex',
    category: 'volatility',
    desc: 'Índice de Úlcera (Métrica de Riesgo de Caída/Drawdown)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 28,
        labelHelp: 'Velas para cuantificar profundidad y duración de caídas',
        description: 'Mide exclusivamente la volatilidad bajista y el estrés financiero causado por retrocesos desde los picos más recientes.'
      }
    ]
  },

  // === 4. VOLUME ===
  {
    id: 'VWAP',
    name: 'VWAP',
    category: 'volume',
    desc: 'Volume Weighted Average Price (Precio Ponderado por Volumen)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Velas de ponderación de volumen institucional',
        description: 'Precio medio negociado en el mercado ponderado por el volumen total de cada barra.'
      }
    ]
  },
  {
    id: 'MFI',
    name: 'MFI',
    category: 'volume',
    desc: 'Money Flow Index (RSI Ponderado por Volumen)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 28,
        labelHelp: 'Velas para evaluar flujo de dinero comprador vs vendedor',
        description: 'Mide la presión compradora y vendedora combinando el movimiento de precios con el volumen transaccionado.'
      },
      {
        key: 'oversold',
        name: 'Sobreventa',
        defaultMin: 15,
        defaultStep: 1,
        defaultMax: 30,
        labelHelp: 'Nivel inferior de sobreventa en MFI',
        description: 'Lecturas por debajo de 20 indican salida extrema de liquidez y potencial rebote.'
      },
      {
        key: 'overbought',
        name: 'Sobrecompra',
        defaultMin: 70,
        defaultStep: 1,
        defaultMax: 85,
        labelHelp: 'Nivel superior de sobrecompra en MFI',
        description: 'Lecturas por encima de 80 indican saturación de liquidez compradora.'
      }
    ]
  },
  {
    id: 'CMF',
    name: 'CMF',
    category: 'volume',
    desc: 'Chaikin Money Flow (Flujo de Dinero de Chaikin)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 10,
        defaultStep: 1,
        defaultMax: 35,
        labelHelp: 'Velas para acumular la presión de acumulación/distribución',
        description: 'Cuantifica el volumen institucional que entra o sale de un activo en un periodo determinado.'
      }
    ]
  },
  {
    id: 'ForceIndex',
    name: 'ForceIndex',
    category: 'volume',
    desc: 'Índice de Fuerza de Alexander Elder',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 5,
        defaultStep: 1,
        defaultMax: 25,
        labelHelp: 'Suavizado exponencial de la fuerza de volumen',
        description: 'Multiplica el cambio de precio por el volumen negociado y lo suaviza para medir la fuerza real detrás del movimiento.'
      }
    ]
  },
  {
    id: 'EoM',
    name: 'EoM',
    category: 'volume',
    desc: 'Ease of Movement (Facilidad de Movimiento)',
    params: [
      {
        key: 'period',
        name: 'Periodo',
        defaultMin: 7,
        defaultStep: 1,
        defaultMax: 28,
        labelHelp: 'Relación entre desplazamiento de precio y volumen requerido',
        description: 'Evalúa con qué facilidad se desplaza el precio en función del volumen (si sube rápido con poco volumen, indica poca resistencia).'
      }
    ]
  },
  {
    id: 'OBV',
    name: 'OBV',
    category: 'volume',
    desc: 'On-Balance Volume (Volumen en Balance Acumulado)',
    params: []
  },
  {
    id: 'ADI',
    name: 'ADI',
    category: 'volume',
    desc: 'Línea de Acumulación / Distribución',
    params: []
  },
  {
    id: 'NVI',
    name: 'NVI',
    category: 'volume',
    desc: 'Índice de Volumen Negativo (Smart Money)',
    params: []
  },
  {
    id: 'VPT',
    name: 'VPT',
    category: 'volume',
    desc: 'Tendencia Volumen-Precio',
    params: []
  }
];

export const getIndicatorCatalogItem = (id: string): IndicatorCatalogItem | undefined => {
  return INDICATORS_CATALOG.find(item => item.id.toLowerCase() === id.toLowerCase() || item.name.toLowerCase() === id.toLowerCase());
};

export const calculateTotalCombinations = (
  selectedIndicatorIds: string[],
  ranges: Record<string, Record<string, { min: number; step: number; max: number }>> = {}
): number => {
  let total = 1;
  let hasAnyParam = false;

  for (const id of selectedIndicatorIds) {
    const item = getIndicatorCatalogItem(id);
    if (!item || item.params.length === 0) continue;

    for (const p of item.params) {
      const userRange = ranges[item.id]?.[p.key] || {
        min: p.defaultMin,
        step: p.defaultStep,
        max: p.defaultMax
      };

      const step = userRange.step > 0 ? userRange.step : 1;
      const count = Math.max(1, Math.floor((userRange.max - userRange.min) / step) + 1);
      total *= count;
      hasAnyParam = true;
    }
  }

  return hasAnyParam ? total : 0;
};
