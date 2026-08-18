//+------------------------------------------------------------------+
//|                                              TRIX.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library TRIX indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "TRIX"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpPeriod = 15;  // Period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "TRIX");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "TRIX");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 46)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   double e1[], e2[], e3[];
   ArraySetAsSeries(e1,true); ArrayResize(e1,rates_total);
   ArraySetAsSeries(e2,true); ArrayResize(e2,rates_total);
   ArraySetAsSeries(e3,true); ArrayResize(e3,rates_total);
   for(int i=0;i<rates_total;i++){ e1[i]=EMPTY_VALUE; e2[i]=EMPTY_VALUE; e3[i]=EMPTY_VALUE; }
   double v=0.0;
   for(int i=0;i<rates_total;i++){ if(i==0)v=close[0]; else v+=(2.0/(InpPeriod+1))*(close[i]-v); if(i>=InpPeriod-1)e1[i]=v; }
   v=0.0;
   for(int i=0;i<rates_total;i++){ if(i==0)v=(e1[i]!=EMPTY_VALUE)?e1[i]:0.0; else if(e1[i]!=EMPTY_VALUE)v+=(2.0/(InpPeriod+1))*(e1[i]-v); if(i>=InpPeriod-1)e2[i]=v; }
   v=0.0;
   for(int i=0;i<rates_total;i++){ if(i==0)v=(e2[i]!=EMPTY_VALUE)?e2[i]:0.0; else if(e2[i]!=EMPTY_VALUE)v+=(2.0/(InpPeriod+1))*(e2[i]-v); if(i>=InpPeriod-1)e3[i]=v; }
   for(int i=start;i<rates_total && !IsStopped();i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<1) continue;
      if(e3[i]!=EMPTY_VALUE && e3[i-1]!=EMPTY_VALUE && e3[i-1]!=0.0)
         ExtBuffer0[i]=(e3[i]-e3[i-1])/e3[i-1]*100.0;
   }
   return(rates_total);
}
