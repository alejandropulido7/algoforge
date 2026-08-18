//+------------------------------------------------------------------+
//|                                              MFI.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library MFI indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "MFI"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpPeriod = 14;  // Period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "MFI");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "MFI");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
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

   double mfrArr[];
   ArraySetAsSeries(mfrArr,true); ArrayResize(mfrArr,rates_total);
   for(int i=0;i<rates_total;i++) mfrArr[i]=0.0;
   for(int i=1;i<rates_total;i++)
   {
      double tp=(high[i]+low[i]+close[i])/3.0;
      double tpl=(high[i-1]+low[i-1]+close[i-1])/3.0;
      int ud = (tp>tpl)?1:((tp<tpl)?-1:0);
      mfrArr[i]=tp*tick_volume[i]*ud;
   }
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      if(i<InpPeriod-1) continue;
      double ps=0.0, ng=0.0;
      for(int k=0;k<InpPeriod;k++)
      {
         if(mfrArr[i-k]>=0.0) ps+=mfrArr[i-k];
         else ng+=-mfrArr[i-k];
      }
      if(ng!=0.0) ExtBuffer0[i]=100.0-100.0/(1.0+ps/ng);
      else if(ps!=0.0) ExtBuffer0[i]=100.0;
   }
   return(rates_total);
}
