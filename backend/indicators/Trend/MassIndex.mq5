//+------------------------------------------------------------------+
//|                                              MassIndex.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library MassIndex indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "MassIndex"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpFast = 9;  // Fast EMA period
input int InpSlow = 25;  // Sum period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "MassIndex");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "MassIndex");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 41)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   double massArr[];
   ArraySetAsSeries(massArr,true); ArrayResize(massArr,rates_total);
   for(int i=0;i<rates_total;i++) massArr[i]=EMPTY_VALUE;
   double e1=0.0, e2=0.0;
   for(int i=0;i<rates_total && !IsStopped();i++)
   {
      double amp=high[i]-low[i];
      if(i==0) e1=amp;
      else e1 += (2.0/(InpFast+1))*(amp-e1);
      if(i<InpFast-1) continue;
      if(i==InpFast-1) e2=e1;
      else e2 += (2.0/(InpFast+1))*(e1-e2);
      if(i>=InpFast-1+InpFast-1 && e2!=0.0) massArr[i]=e1/e2;
   }
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<InpFast-1+InpFast-1+InpSlow-1) continue;
      double s=0.0; int c=0;
      for(int k=0;k<InpSlow;k++) if(massArr[i-k]!=EMPTY_VALUE){ s+=massArr[i-k]; c++; }
      if(c==InpSlow) ExtBuffer0[i]=s;   // rolling SUM como ta
   }
   return(rates_total);
}
