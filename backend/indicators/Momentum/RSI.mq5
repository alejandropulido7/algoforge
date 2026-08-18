//+------------------------------------------------------------------+
//|                                              RSI.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library RSI indicator"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "RSI"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 2

input int InpPeriod = 14;  // Period

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "RSI");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "RSI");
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

   // ta: ewm(alpha=1/period, adjust=False) -> siembra en 0, NO Wilder
   static double eup=0.0, edn=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE;
      double up=0.0, dn=0.0;
      if(i>0){ double d=close[i]-close[i-1]; if(d>0)up=d; else if(d<0)dn=-d; }
      if(i==0){ eup=up; edn=dn; }
      else { eup += (1.0/InpPeriod)*(up-eup); edn += (1.0/InpPeriod)*(dn-edn); }
      if(i>=InpPeriod-1)
      {
         if(edn==0.0) ExtBuffer0[i]=100.0;
         else ExtBuffer0[i]=100.0-100.0/(1.0+eup/edn);
      }
   }
   return(rates_total);
}
