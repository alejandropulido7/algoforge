//+------------------------------------------------------------------+
//|                                              KST.mq5 |
//+------------------------------------------------------------------+
#property copyright "ta -> MT5 port"
#property link      "https://technical-analysis-library-in-python.readthedocs.io/"
#property version   "1.00"
#property description "Port of Python ta library KST indicator"
#property indicator_separate_window
#property indicator_buffers 3
#property indicator_plots   3

#property indicator_label1  "KST"
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

input int InpROC1 = 10;  // ROC 1
input int InpROC2 = 15;  // ROC 2
input int InpROC3 = 20;  // ROC 3
input int InpROC4 = 30;  // ROC 4
input int InpSMA1 = 10;  // SMA 1
input int InpSMA2 = 10;  // SMA 2
input int InpSMA3 = 10;  // SMA 3
input int InpSMA4 = 15;  // SMA 4
input int InpSignal = 9;  // Signal period

double ExtBuffer0[];
double ExtBuffer1[];
double ExtBuffer2[];

int OnInit()
{
   SetIndexBuffer(0, ExtBuffer0, INDICATOR_DATA);
   SetIndexBuffer(1, ExtBuffer1, INDICATOR_DATA);
   SetIndexBuffer(2, ExtBuffer2, INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, "KST");
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_LINE);
   PlotIndexSetString(0, PLOT_LABEL, "KST");
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
   if(rates_total < 45)
      return(0);
   int start = prev_calculated > 1 ? prev_calculated - 1 : 0;

   double rc[4][], sm[4][];
   int rp[4]={InpROC1,InpROC2,InpROC3,InpROC4};
   int wp[4]={InpSMA1,InpSMA2,InpSMA3,InpSMA4};
   for(int j=0;j<4;j++)
   {
      ArraySetAsSeries(rc[j],true); ArrayResize(rc[j],rates_total);
      ArraySetAsSeries(sm[j],true); ArrayResize(sm[j],rates_total);
      for(int i=0;i<rates_total;i++){ rc[j][i]=EMPTY_VALUE; sm[j][i]=EMPTY_VALUE; }
      for(int i=rp[j];i<rates_total;i++) rc[j][i]= close[i-rp[j]]!=0.0 ? (close[i]-close[i-rp[j]])/close[i-rp[j]] : EMPTY_VALUE;
      for(int i=wp[j]-1;i<rates_total;i++)
      {
         double s=0.0; int c=0;
         for(int k=0;k<wp[j];k++) if(rc[j][i-k]!=EMPTY_VALUE){ s+=rc[j][i-k]; c++; }
         if(c==wp[j]) sm[j][i]=s/wp[j];
      }
   }
   for(int i=start; i<rates_total && !IsStopped(); i++)
   {
      ExtBuffer0[i]=EMPTY_VALUE; ExtBuffer1[i]=EMPTY_VALUE; ExtBuffer2[i]=EMPTY_VALUE;
      if(i<InpSMA4-1+InpROC4-1) continue;
      if(sm[3][i]==EMPTY_VALUE) continue;
      double kstv=100.0*(sm[0][i]+2.0*sm[1][i]+3.0*sm[2][i]+4.0*sm[3][i]);
      ExtBuffer0[i]=kstv;
      double s=0.0; int c=0;
      for(int k=0;k<InpSignal;k++) if(ExtBuffer0[i-k]!=EMPTY_VALUE){ s+=ExtBuffer0[i-k]; c++; }
      if(c>0){ double sig=s/c; ExtBuffer1[i]=sig; ExtBuffer2[i]=kstv-sig; }
   }
   return(rates_total);
}
