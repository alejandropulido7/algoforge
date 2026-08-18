//+------------------------------------------------------------------+
//|                                              Keltner.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library Keltner indicator"
#property indicator_chart_window
#property indicator_buffers 3
#property indicator_plots   3

#property indicator_label1  "Middle"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "Upper"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrSilver
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1
#property indicator_label3  "Lower"
#property indicator_type3  DRAW_LINE
#property indicator_color3 clrSilver
#property indicator_style3 STYLE_SOLID
#property indicator_width3 1

input int InpPeriod = 20;  // SMA period
input bool InpOriginal = True;  // Use original (SMA) version

double ExtBuffer0[];
double ExtBuffer1[];
double ExtBuffer2[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   SetIndexBuffer(2, ExtBuffer2, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "Keltner");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "Middle");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "Upper");
   PlotIndexSetInteger(2, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(2, PLOT_LABEL, "Lower");
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
   if(rates_total < 20)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   if(!InpOriginal){ ExtBuffer0[0]=EMPTY_VALUE; ExtBuffer1[0]=EMPTY_VALUE; ExtBuffer2[0]=EMPTY_VALUE; return(rates_total); }
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE; ExtBuffer2[i]=EMPTY_VALUE;
      if(i<InpPeriod-1) continue;
      double tp=0.0, tph=0.0, tpl=0.0;
      for(int k=0;k<InpPeriod;k++)
      {
         double h=high[i-k], l=low[i-k], c=close[i-k];
         tp  += (h+l+c)/3.0;
         tph += (4.0*h-2.0*l+c)/3.0;
         tpl += (-2.0*h+4.0*l+c)/3.0;
      }
      tp/=InpPeriod; tph/=InpPeriod; tpl/=InpPeriod;
      ExtBuffer0[i]=tp;
      ExtBuffer1[i]=tph;
      ExtBuffer2[i]=tpl;
   }
   return(rates_total);
}
