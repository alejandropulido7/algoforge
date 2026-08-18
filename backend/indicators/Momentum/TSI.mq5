//+------------------------------------------------------------------+
//|                                              TSI.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library TSI indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "TSI"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int InpSlow = 25;  // Slow period
input int InpFast = 13;  // Fast period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "TSI");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "TSI");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
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

   static double ema1p=0.0, ema2p=0.0, ema1a=0.0, ema2a=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      double mom=0.0;
      if(i>0) mom=close[i]-close[i-1];
      if(i==1){ ema1p=mom; ema1a=MathAbs(mom); }
      else if(i>1){ ema1p += (2.0/(InpSlow+1))*(mom-ema1p); ema1a += (2.0/(InpSlow+1))*(MathAbs(mom)-ema1a); }
      if(i==InpSlow){ ema2p=ema1p; ema2a=ema1a; }
      else if(i>InpSlow){ ema2p += (2.0/(InpFast+1))*(ema1p-ema2p); ema2a += (2.0/(InpFast+1))*(ema1a-ema2a); }
      if(i>=InpSlow+InpFast-1 && ema2a!=0.0) ExtBuffer0[i]=100.0*ema2p/ema2a;
   }
   return(rates_total);
}
