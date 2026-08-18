//+------------------------------------------------------------------+
//|                                                         HMA.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library HMA (Hull Moving Average) indicator"
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "HMA"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 2

input int InpPeriod = 20;  // Period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "HMA");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "HMA");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

double CalcWMA(const double &arr[], int period, int pos)
{
   if(pos < period - 1) return 0.0;
   double sum = 0.0;
   double weight_sum = 0.0;
   for(int i = 0; i < period; i++)
   {
      double w = period - i;
      sum += arr[pos - i] * w;
      weight_sum += w;
   }
   return (weight_sum > 0) ? (sum / weight_sum) : 0.0;
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < InpPeriod + 5)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   int half_period = MathMax(1, InpPeriod / 2);
   int sqrt_period = MathMax(1, (int)MathSqrt(InpPeriod));

   double raw_diff[];
   ArrayResize(raw_diff, rates_total);

   for(int i = 0; i < rates_total; i++)
   {
      if(i < InpPeriod - 1)
      {
         raw_diff[i] = 0.0;
         continue;
      }
      double wma_half = CalcWMA(close, half_period, i);
      double wma_full = CalcWMA(close, InpPeriod, i);
      raw_diff[i] = 2.0 * wma_half - wma_full;
   }

   for(int i = start; i < rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i] = EMPTY_VALUE;
      if(i < InpPeriod + sqrt_period - 2) continue;
      ExtBuffer0[i] = CalcWMA(raw_diff, sqrt_period, i);
   }
   return(rates_total);
}
