//+------------------------------------------------------------------+
//|                                              Aroon.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library Aroon indicator"
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   2

#property indicator_label1  "Aroon Up"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "Aroon Down"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrOrangeRed
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1

input int InpPeriod = 25;  // Period

double ExtBuffer0[];
double ExtBuffer1[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "Aroon");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "Aroon Up");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "Aroon Down");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 26)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE;
      if(i<InpPeriod-1) continue;
      int imax=0, imin=0;
      double hh=high[i-InpPeriod+1], ll=low[i-InpPeriod+1];
      for(int k=0;k<InpPeriod;k++)
      {
         if(high[i-InpPeriod+1+k]>hh){ hh=high[i-InpPeriod+1+k]; imax=k; }
         if(low[i-InpPeriod+1+k]<ll){ ll=low[i-InpPeriod+1+k]; imin=k; }
      }
      ExtBuffer0[i]=100.0*(imax+1)/InpPeriod;
      ExtBuffer1[i]=100.0*(imin+1)/InpPeriod;
   }
   return(rates_total);
}
