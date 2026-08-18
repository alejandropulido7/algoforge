//+------------------------------------------------------------------+
//|                                              AO.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library AO indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "AO"
#property indicator_type1  DRAW_HISTOGRAM
#property indicator_color1 clrSilver
#property indicator_style1 STYLE_SOLID
#property indicator_width1 2

input int InpFast = 5;  // Fast period
input int InpSlow = 34;  // Slow period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "AO");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_HISTOGRAM);
   PlotIndexSetString(0, PLOT_LABEL, "AO");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 34)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i] = EMPTY_VALUE;
      if(i < InpSlow-1) continue;
      double s5=0.0, s34=0.0;
      for(int k=0;k<InpFast;k++) s5  += (high[i-k]+low[i-k])*0.5;
      for(int k=0;k<InpSlow;k++) s34 += (high[i-k]+low[i-k])*0.5;
      ExtBuffer0[i] = s5/InpFast - s34/InpSlow;
   }
   return(rates_total);
}
