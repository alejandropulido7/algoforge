//+------------------------------------------------------------------+
//|                                              CMF.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library CMF indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "CMF"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpPeriod = 20;  // Period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "CMF");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "CMF");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 21)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<InpPeriod-1) continue;
      double sm=0.0, sv=0.0;
      for(int k=0;k<InpPeriod;k++)
      {
         double clv = (high[i-k]!=low[i-k]) ? ((close[i-k]-low[i-k])-(high[i-k]-close[i-k]))/(high[i-k]-low[i-k]) : 0.0;
         sm += clv*tick_volume[i-k];
         sv += tick_volume[i-k];
      }
      ExtBuffer0[i]= sv!=0.0 ? sm/sv : EMPTY_VALUE;
   }
   return(rates_total);
}
