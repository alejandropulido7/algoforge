//+------------------------------------------------------------------+
//|                                              ATR.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library ATR indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "ATR"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 2

input int InpPeriod = 14;  // Period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "ATR");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "ATR");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 15)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   static double prev_atr=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<InpPeriod-1) continue;
      if(i==InpPeriod-1)
      {
         double sum=0.0;
         for(int j=0;j<InpPeriod;j++)
         {
            double tr = (j==0) ? (high[0]-low[0])
                               : MathMax(high[j]-low[j],MathMax(MathAbs(high[j]-close[j-1]),MathAbs(low[j]-close[j-1])));
            sum+=tr;
         }
         prev_atr = sum/InpPeriod;
         ExtBuffer0[i]=prev_atr;
      }
      else
      {
         double tr = MathMax(high[i]-low[i],MathMax(MathAbs(high[i]-close[i-1]),MathAbs(low[i]-close[i-1])));
         prev_atr = (prev_atr*(InpPeriod-1)+tr)/InpPeriod;
         ExtBuffer0[i]=prev_atr;
      }
   }
   return(rates_total);
}
