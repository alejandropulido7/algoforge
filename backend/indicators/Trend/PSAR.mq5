//+------------------------------------------------------------------+
//|                                              PSAR.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library PSAR indicator"
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "PSAR"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input double InpStep = 0.02;  // Step
input double InpMaxStep = 0.2;  // Maximum step

double ExtBuffer0[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "PSAR");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "PSAR");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 3)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   static bool up=true;
   static double af=0.0, up_high=0.0, dn_low=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      if(i==0){ ExtBuffer0[i]=close[0]; up=true; af=InpStep; up_high=high[0]; dn_low=low[0]; continue; }
      if(i==1){ ExtBuffer0[i]=close[1]; continue; }
      bool reversal=false;
      double ps;
      if(up)
      {
         ps = ExtBuffer0[i-1] + af*(up_high-ExtBuffer0[i-1]);
         if(low[i]<ps){ reversal=true; ps=up_high; dn_low=low[i]; af=InpStep; }
         else
         {
            if(high[i]>up_high){ up_high=high[i]; af=MathMin(af+InpStep,InpMaxStep); }
            if(low[i-2]<ps) ps=low[i-2];
            else if(low[i-1]<ps) ps=low[i-1];
         }
      }
      else
      {
         ps = ExtBuffer0[i-1] - af*(ExtBuffer0[i-1]-dn_low);
         if(high[i]>ps){ reversal=true; ps=dn_low; up_high=high[i]; af=InpStep; }
         else
         {
            if(low[i]<dn_low){ dn_low=low[i]; af=MathMin(af+InpStep,InpMaxStep); }
            if(high[i-2]>ps) ps=high[i-2];
            else if(high[i-1]>ps) ps=high[i-1];
         }
      }
      up = up!=reversal;
      ExtBuffer0[i]=ps;
   }
   return(rates_total);
}
