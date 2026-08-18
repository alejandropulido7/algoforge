//+------------------------------------------------------------------+
//|                                              CumulativeReturn.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library CumulativeReturn indicator"
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "CumulativeReturn"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1



double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "CumulativeReturn");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "CumulativeReturn");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 1)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   static double acc=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      if(i==0){ acc=0.0; ExtBuffer0[i]=0.0; continue; }
      if(close[i-1]!=0.0) acc += (close[i]/close[i-1]-1.0)*100.0;
      ExtBuffer0[i]=acc;
   }
   return(rates_total);
}
