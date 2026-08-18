//+------------------------------------------------------------------+
//|                                              EoM.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library EoM indicator"
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   2

#property indicator_label1  "EoM"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "SMA"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrOrangeRed
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1

input int InpPeriod = 14;  // SMA period

double ExtBuffer0[];
double ExtBuffer1[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "EoM");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "EoM");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "SMA");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
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

   double emArr[];
   ArraySetAsSeries(emArr,true); ArrayResize(emArr,rates_total);
   for(int i=0;i<rates_total;i++) emArr[i]=EMPTY_VALUE;
   for(int i=1;i<rates_total;i++)
   {
      if(tick_volume[i]!=0.0)
         emArr[i] = ((high[i]-high[i-1])+(low[i]-low[i-1]))*(high[i]-low[i])/(2.0*tick_volume[i])*100000000.0;
   }
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE;
      if(i<1) continue;
      ExtBuffer0[i]=emArr[i];
      if(i<InpPeriod-1) continue;
      double s=0.0; int c=0;
      for(int k=0;k<InpPeriod;k++) if(emArr[i-k]!=EMPTY_VALUE){ s+=emArr[i-k]; c++; }
      if(c==InpPeriod) ExtBuffer1[i]=s/InpPeriod;
   }
   return(rates_total);
}
