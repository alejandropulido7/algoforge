//+------------------------------------------------------------------+
//|                                              Vortex.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library Vortex indicator"
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   2

#property indicator_label1  "+VI"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "-VI"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrOrangeRed
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1

input int InpPeriod = 14;  // Period

double ExtBuffer0[];
double ExtBuffer1[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "Vortex");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "+VI");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "-VI");
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

   double tr[], vmp[], vmm[];
   ArraySetAsSeries(tr,true); ArrayResize(tr,rates_total);
   ArraySetAsSeries(vmp,true); ArrayResize(vmp,rates_total);
   ArraySetAsSeries(vmm,true); ArrayResize(vmm,rates_total);
   for(int i=0;i<rates_total;i++){ tr[i]=EMPTY_VALUE; vmp[i]=EMPTY_VALUE; vmm[i]=EMPTY_VALUE; }
   tr[0]=MathMax(high[0]-low[0],MathMax(MathAbs(high[0]-close[0]),MathAbs(low[0]-close[0])));
   for(int i=1;i<rates_total;i++)
   {
      tr[i]=MathMax(high[i]-low[i],MathMax(MathAbs(high[i]-close[i-1]),MathAbs(low[i]-close[i-1])));
      vmp[i]=MathAbs(high[i]-low[i-1]);
      vmm[i]=MathAbs(low[i]-high[i-1]);
   }
   for(int i=start;i<rates_total && !IsStopped();i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE;
      if(i<InpPeriod-1) continue;
      double str=0.0, svmp=0.0, svmm=0.0;
      for(int k=0;k<InpPeriod;k++){ if(tr[i-k]!=EMPTY_VALUE)str+=tr[i-k]; if(vmp[i-k]!=EMPTY_VALUE)svmp+=vmp[i-k]; if(vmm[i-k]!=EMPTY_VALUE)svmm+=vmm[i-k]; }
      if(str!=0.0){ ExtBuffer0[i]=svmp/str; ExtBuffer1[i]=svmm/str; }
   }
   return(rates_total);
}
