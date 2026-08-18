//+------------------------------------------------------------------+
//|                                              UltimateOscillator.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library UltimateOscillator indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "UO"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpPeriod1 = 7;  // Period 1
input int InpPeriod2 = 14;  // Period 2
input int InpPeriod3 = 28;  // Period 3

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "UltimateOscillator");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "UO");
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

   double bp[], tr[];
   ArraySetAsSeries(bp,true); ArrayResize(bp,rates_total);
   ArraySetAsSeries(tr,true); ArrayResize(tr,rates_total);
   for(int i=0;i<rates_total;i++){ bp[i]=EMPTY_VALUE; tr[i]=EMPTY_VALUE; }
   for(int i=1;i<rates_total && !IsStopped();i++)
   {
      double pc=close[i-1];
      tr[i]=MathMax(high[i]-low[i],MathMax(MathAbs(high[i]-pc),MathAbs(low[i]-pc)));
      double tl=MathMin(low[i],pc);
      bp[i]=close[i]-tl;
   }
   double w1[3]={InpPeriod1,InpPeriod2,InpPeriod3};
   for(int i=start;i<rates_total && !IsStopped();i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<InpPeriod3-1) continue;
      double avgb[3], avgtr[3];
      for(int j=0;j<3;j++)
      {
         double sb=0.0, st=0.0; int cb=0, ct=0;
         for(int k=0;k<w1[j];k++){ if(bp[i-k]!=EMPTY_VALUE){sb+=bp[i-k];cb++;} if(tr[i-k]!=EMPTY_VALUE){st+=tr[i-k];ct++;} }
         avgb[j]= cb==w1[j] ? sb/w1[j] : EMPTY_VALUE;
         avgtr[j]= ct==w1[j] ? st/w1[j] : EMPTY_VALUE;
      }
      if(avgtr[0]!=EMPTY_VALUE && avgtr[1]!=EMPTY_VALUE && avgtr[2]!=EMPTY_VALUE)
         ExtBuffer0[i]=100.0*(4.0*avgb[0]/avgtr[0]+2.0*avgb[1]/avgtr[1]+1.0*avgb[2]/avgtr[2])/(4.0+2.0+1.0);
   }
   return(rates_total);
}
