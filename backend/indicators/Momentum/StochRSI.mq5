//+------------------------------------------------------------------+
//|                                              StochRSI.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library StochRSI indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "StochRSI"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpRSIPeriod = 14;  // RSI period
input int InpPeriod = 14;  // Stochastic period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "StochRSI");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "StochRSI");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 28)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   // RSI (ta: ewm alpha=1/period, siembra en 0) en buffer auxiliar
   static double avg_g=0.0, avg_l=0.0;
   double rsiArr[];
   ArraySetAsSeries(rsiArr,true); ArrayResize(rsiArr, rates_total);
   for(int i=0;i<rates_total;i++) rsiArr[i]=EMPTY_VALUE;
   for(int i=0;i<rates_total && !IsStopped();i++)
   {
      double up=0.0, dn=0.0;
      if(i>0){ double d=close[i]-close[i-1]; if(d>0)up=d; else if(d<0)dn=-d; }
      if(i==0){ avg_g=up; avg_l=dn; }
      else { avg_g += (1.0/InpRSIPeriod)*(up-avg_g); avg_l += (1.0/InpRSIPeriod)*(dn-avg_l); }
      if(i>=InpRSIPeriod-1) rsiArr[i]= avg_l==0.0?100.0:100.0-100.0/(1.0+avg_g/avg_l);
   }
   // StochRSI = estocastico del RSI (sin suavizado)
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<InpRSIPeriod-1+InpPeriod-1) continue;
      double mn=DBL_MAX, mx=-DBL_MAX; int c=0;
      for(int k=0;k<InpPeriod;k++){ double r=rsiArr[i-k]; if(r!=EMPTY_VALUE){ if(r<mn)mn=r; if(r>mx)mx=r; c++; } }
      if(c<InpPeriod || mx==mn){ ExtBuffer0[i]=EMPTY_VALUE; continue; }
      ExtBuffer0[i]=(rsiArr[i]-mn)/(mx-mn);
   }
   return(rates_total);
}
