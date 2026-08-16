export type IndicatorCategory = 'momentum' | 'trend' | 'volatility' | 'volume' | 'overlap'

export interface Indicator {
  name: string
  category: IndicatorCategory
  funcName: string
  defaultParams: Record<string, number>
  paramRanges: Record<string, [number, number]>
  description: string
}

export interface SelectedIndicator extends Indicator {
  selected: boolean
  params: Record<string, number>
}
