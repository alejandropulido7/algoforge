//+------------------------------------------------------------------+
//|                                              PPO.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library PPO indicator"
#property indicator_separate_window
#property indicator_buffers 3
#property indicator_plots   3

#property indicator_label1  "PPO"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "Signal"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrOrangeRed
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1
#property indicator_label3  "Histogram"
#property indicator_type3  DRAW_HISTOGRAM
#property indicator_color3 clrSilver
#property indicator_style3 STYLE_SOLID
#property indicator_width3 1

input int InpFast = 12;  // Fast EMA period
input int InpSlow = 26;  // Slow EMA period
input int InpSignal = 9;  // Signal period

double ExtBuffer0[];
double ExtBuffer1[];
double ExtBuffer2[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   SetIndexBuffer(2, ExtBuffer2, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "PPO");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "PPO");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "Signal");
   PlotIndexSetInteger(2, PLOT_DRAW_TYPE, DRAW_HISTOGRAM);
   PlotIndexSetString(2, PLOT_LABEL, "Histogram");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(2, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 27)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   static double ef=0.0, es=0.0, sig=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      if(i==0){ ef=close[0]; es=close[0]; }
      else { ef += (2.0/(InpFast+1))*(close[i]-ef); es += (2.0/(InpSlow+1))*(close[i]-es); }
      ExtBuffer1[i] = EMPTY_VALUE; ExtBuffer2[i] = EMPTY_VALUE;
      if(i < InpSlow-1){ ExtBuffer0[i]=EMPTY_VALUE; continue; }
      double p = es!=0.0 ? (ef-es)/es*100.0 : EMPTY_VALUE;
      ExtBuffer0[i] = p;
      if(p!=EMPTY_VALUE)
      {
         if(i==InpSlow-1) sig=p;
         else sig += (2.0/(InpSignal+1))*(p-sig);
         if(i >= InpSlow-1+InpSignal-1) { ExtBuffer1[i]=sig; ExtBuffer2[i]=p-sig; }
      }
   }
   return(rates_total);
}
