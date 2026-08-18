//+------------------------------------------------------------------+
//|                                              STC.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library STC indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "STC"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpSlow = 50;  // Slow EMA period
input int InpFast = 23;  // Fast EMA period
input int InpCycle = 10;  // Cycle
input int InpD1 = 3;  // Smooth 1
input int InpD2 = 3;  // Smooth 2

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "STC");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "STC");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 80)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   double m[], d1[], k2[];
   ArraySetAsSeries(m,true);  ArrayResize(m,rates_total);
   ArraySetAsSeries(d1,true); ArrayResize(d1,rates_total);
   ArraySetAsSeries(k2,true); ArrayResize(k2,rates_total);
   for(int i=0;i<rates_total;i++){ m[i]=EMPTY_VALUE; d1[i]=EMPTY_VALUE; k2[i]=EMPTY_VALUE; }
   double ef=0.0, es=0.0;
   for(int i=0;i<rates_total;i++)
   {
      if(i==0){ ef=close[0]; es=close[0]; }
      else { ef+=(2.0/(InpFast+1))*(close[i]-ef); es+=(2.0/(InpSlow+1))*(close[i]-es); }
      if(i>=InpSlow-1) m[i]=ef-es;
   }
   for(int i=InpCycle-1;i<rates_total && !IsStopped();i++)
   {
      if(m[i]==EMPTY_VALUE) continue;
      double mn=DBL_MAX, mx=-DBL_MAX; int c=0;
      for(int k=0;k<InpCycle;k++) if(m[i-k]!=EMPTY_VALUE){ if(m[i-k]<mn)mn=m[i-k]; if(m[i-k]>mx)mx=m[i-k]; c++; }
      if(c==InpCycle && mx!=mn) d1[i]=100.0*(m[i]-mn)/(mx-mn);
   }
   // d1 = ema(k1, InpD1) — aplica suavizado ema a la serie k1 (guardada en d1)
   double e1=0.0;
   for(int i=0;i<rates_total;i++)
   {
      if(i==0) e1 = (d1[i]!=EMPTY_VALUE)?d1[i]:0.0;
      else if(d1[i]!=EMPTY_VALUE) e1 += (2.0/(InpD1+1))*(d1[i]-e1);
      if(i>=InpD1-1) d1[i]=e1; else d1[i]=EMPTY_VALUE;
   }
   for(int i=InpCycle-1;i<rates_total && !IsStopped();i++)
   {
      if(d1[i]==EMPTY_VALUE) continue;
      double mn=DBL_MAX, mx=-DBL_MAX; int c=0;
      for(int k=0;k<InpCycle;k++) if(d1[i-k]!=EMPTY_VALUE){ if(d1[i-k]<mn)mn=d1[i-k]; if(d1[i-k]>mx)mx=d1[i-k]; c++; }
      if(c==InpCycle && mx!=mn) k2[i]=100.0*(d1[i]-mn)/(mx-mn);
   }
   double e2=0.0;
   for(int i=0;i<rates_total;i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i==0) e2 = (k2[i]!=EMPTY_VALUE)?k2[i]:0.0;
      else if(k2[i]!=EMPTY_VALUE) e2 += (2.0/(InpD2+1))*(k2[i]-e2);
      if(i>=InpD2-1) ExtBuffer0[i]=e2;
   }
   return(rates_total);
}
