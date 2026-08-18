//+------------------------------------------------------------------+
//|                                              Stochastic.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library Stochastic indicator"
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   2

#property indicator_label1  "K"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "D"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrOrangeRed
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1

input int InpKPeriod = 14;  // K period
input int InpDPeriod = 3;  // D period
input int InpSlow = 3;  // Slow period

double ExtBuffer0[];
double ExtBuffer1[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "Stochastic");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "K");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "D");
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

   double kBuf[], dBuf[];
   ArraySetAsSeries(kBuf,true); ArrayResize(kBuf,rates_total);
   ArraySetAsSeries(dBuf,true); ArrayResize(dBuf,rates_total);
   for(int i=0;i<rates_total;i++){ kBuf[i]=EMPTY_VALUE; dBuf[i]=EMPTY_VALUE; }
   for(int i=InpKPeriod-1;i<rates_total && !IsStopped();i++)
   {
      double hh=-DBL_MAX, ll=DBL_MAX;
      for(int k=0;k<InpKPeriod;k++){ if(high[i-k]>hh)hh=high[i-k]; if(low[i-k]<ll)ll=low[i-k]; }
      kBuf[i]= hh!=ll ? (close[i]-ll)/(hh-ll)*100.0 : EMPTY_VALUE;
   }
   for(int i=InpKPeriod-1+InpDPeriod-1;i<rates_total && !IsStopped();i++)
   {
      double s=0.0; int c=0;
      for(int k=0;k<InpDPeriod;k++) if(kBuf[i-k]!=EMPTY_VALUE){ s+=kBuf[i-k]; c++; }
      dBuf[i]= c==InpDPeriod ? s/InpDPeriod : EMPTY_VALUE;
   }
   for(int i=start;i<rates_total && !IsStopped();i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE;
      if(i<InpKPeriod-1+InpDPeriod-1+InpSlow-1) continue;
      // ta: K final = sma(kBuf, slow); D = sma(D, slow)
      double sk=0.0, sd=0.0; int ck=0, cd=0;
      for(int s=0;s<InpSlow;s++){ if(kBuf[i-s]!=EMPTY_VALUE){sk+=kBuf[i-s];ck++;} if(dBuf[i-s]!=EMPTY_VALUE){sd+=dBuf[i-s];cd++;} }
      if(ck==InpSlow) ExtBuffer0[i]=sk/InpSlow;
      if(cd==InpSlow) ExtBuffer1[i]=sd/InpSlow;
   }
   return(rates_total);
}
