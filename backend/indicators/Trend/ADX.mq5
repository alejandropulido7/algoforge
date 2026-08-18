//+------------------------------------------------------------------+
//|                                              ADX.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library ADX indicator"
#property indicator_separate_window
#property indicator_buffers 3
#property indicator_plots   3

#property indicator_label1  "ADX"
#property indicator_type1  DRAW_LINE
#property indicator_color1 clrDodgerBlue
#property indicator_style1 STYLE_SOLID
#property indicator_width1 2
#property indicator_label2  "+DI"
#property indicator_type2  DRAW_LINE
#property indicator_color2 clrLime
#property indicator_style2 STYLE_SOLID
#property indicator_width2 1
#property indicator_label3  "-DI"
#property indicator_type3  DRAW_LINE
#property indicator_color3 clrOrangeRed
#property indicator_style3 STYLE_SOLID
#property indicator_width3 1

input int InpPeriod = 14;  // Period

double ExtBuffer0[];
double ExtBuffer1[];
double ExtBuffer2[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   SetIndexBuffer(2, ExtBuffer2, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "ADX");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "ADX");
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(1, PLOT_LABEL, "+DI");
   PlotIndexSetInteger(2, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(2, PLOT_LABEL, "-DI");
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
   if(rates_total < 29)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   static double trs=0.0, dps=0.0, dns=0.0, adx=0.0, dirmSum=0.0;
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE; ExtBuffer2[i]=EMPTY_VALUE;
      if(i<InpPeriod) continue;
      double dm=MathMax(high[i],close[i-1])-MathMin(low[i],close[i-1]);
      double du=high[i]-high[i-1], dd=low[i-1]-low[i];
      double pos=(du>dd && du>0.0)?du:0.0;
      double neg=(dd>du && dd>0.0)?dd:0.0;
      if(i==InpPeriod)
      {
         trs=0.0; dps=0.0; dns=0.0; dirmSum=0.0;
         for(int j=1;j<=InpPeriod;j++)
         {
            trs += MathMax(high[j],close[j-1])-MathMin(low[j],close[j-1]);
            double duj=high[j]-high[j-1], ddj=low[j-1]-low[j];
            dps += (duj>ddj && duj>0.0)?duj:0.0;
            dns += (ddj>duj && ddj>0.0)?ddj:0.0;
         }
      }
      else
      {
         trs = trs*(InpPeriod-1)/InpPeriod + dm;
         dps = dps*(InpPeriod-1)/InpPeriod + pos;
         dns = dns*(InpPeriod-1)/InpPeriod + neg;
      }
      double dseed = trs!=0.0 ? 100.0*dps/trs : 0.0;
      double nseed = trs!=0.0 ? 100.0*dns/trs : 0.0;
      double dirm = (dseed+nseed)!=0.0 ? 100.0*MathAbs(dseed-nseed)/(dseed+nseed) : 0.0;
      if(i>InpPeriod){ ExtBuffer1[i]=dseed; ExtBuffer2[i]=nseed; }
      if(i<2*InpPeriod-1)
      {
         if(i>=InpPeriod) dirmSum+=dirm;
      }
      else if(i==2*InpPeriod-1)
      {
         adx = (dirmSum+dirm)/InpPeriod;
         ExtBuffer0[i]=adx;
      }
      else
      {
         adx = (adx*(InpPeriod-1)+dirm)/InpPeriod;
         ExtBuffer0[i]=adx;
      }
   }
   return(rates_total);
}
