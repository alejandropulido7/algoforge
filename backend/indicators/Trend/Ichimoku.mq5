//+------------------------------------------------------------------+
//|                                              Ichimoku.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library Ichimoku indicator"
#property indicator_chart_window
#property indicator_buffers 4
#property indicator_plots   4

#property indicator_label1  "Tenkan"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1
#property indicator_label2  "Kijun"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrOrangeRed
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1
#property indicator_label3  "Senkou A"
#property indicator_type3  DRAW_LINE
#property indicator_color3 clrLime
#property indicator_style3 STYLE_SOLID
#property indicator_width3 1
#property indicator_label4  "Senkou B"
#property indicator_type4  DRAW_LINE
#property indicator_color4 clrMagenta
#property indicator_style4 STYLE_SOLID
#property indicator_width4 1

input int InpTenkan = 9;  // Tenkan period
input int InpKijun = 26;  // Kijun period
input int InpSenkou = 52;  // Senkou B period

double ExtBuffer0[];
double ExtBuffer1[];
double ExtBuffer2[];
double ExtBuffer3[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   SetIndexBuffer(2, ExtBuffer2, INDICATOR_DATA);
   SetIndexBuffer(3, ExtBuffer3, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "Ichimoku");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "Tenkan");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "Kijun");
   PlotIndexSetInteger(2, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(2, PLOT_LABEL, "Senkou A");
   PlotIndexSetInteger(3, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(3, PLOT_LABEL, "Senkou B");
      PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(2, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(3, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])
{
   if(rates_total < 53)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   double conv=0.0, base=0.0, hh, ll;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE;
      ExtBuffer2[i]=EMPTY_VALUE; ExtBuffer3[i]=EMPTY_VALUE;
      if(i>=InpTenkan-1)
      {
         hh=-DBL_MAX; ll=DBL_MAX;
         for(int k=0;k<InpTenkan;k++){ if(high[i-k]>hh)hh=high[i-k]; if(low[i-k]<ll)ll=low[i-k]; }
         conv=0.5*(hh+ll);
         ExtBuffer0[i]=conv;
      }
      if(i>=InpKijun-1)
      {
         hh=-DBL_MAX; ll=DBL_MAX;
         for(int k=0;k<InpKijun;k++){ if(high[i-k]>hh)hh=high[i-k]; if(low[i-k]<ll)ll=low[i-k]; }
         base=0.5*(hh+ll);
         ExtBuffer1[i]=base;
         if(!(ExtBuffer0[i]==EMPTY_VALUE)) ExtBuffer2[i]=0.5*(conv+base);
      }
      if(i>=InpSenkou-1)
      {
         hh=-DBL_MAX; ll=DBL_MAX;
         for(int k=0;k<InpSenkou;k++){ if(high[i-k]>hh)hh=high[i-k]; if(low[i-k]<ll)ll=low[i-k]; }
         ExtBuffer3[i]=0.5*(hh+ll);
      }
   }
   return(rates_total);
}
