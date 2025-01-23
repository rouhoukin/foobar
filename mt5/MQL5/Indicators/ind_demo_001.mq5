//+------------------------------------------------------------------+
//|                                                 ind_demo_001.mq5 |
//|                                  Copyright 2021, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property indicator_separate_window

#property indicator_minimum -1
#property indicator_maximum 1

#property indicator_buffers 3
#property indicator_plots   1
#property indicator_type1   DRAW_HISTOGRAM
#property indicator_color1  clrRed
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1

//--- input parameters
input int   i_slow_sma=600;
input int   i_fast_sma=120;

//--- indicator buffers
double  ExtBuffer[];
double  ExtWorkBuffer_sma_fast[];
double  ExtWorkBuffer_sma_slow[];

//--- global
int     g_sma_fast_handle;
int     g_sma_slow_handle;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
//--- indicator buffers mapping
    SetIndexBuffer(0,ExtBuffer,INDICATOR_DATA);
    SetIndexBuffer(1,ExtWorkBuffer_sma_fast,INDICATOR_CALCULATIONS);
    SetIndexBuffer(2,ExtWorkBuffer_sma_slow,INDICATOR_CALCULATIONS);

    IndicatorSetInteger(INDICATOR_DIGITS,0);

//--- sets first bar from what index will be drawn
    PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,150);

    string nm=StringFormat("sma_fast-slow(%d/%d)",i_fast_sma,i_slow_sma);
    string short_name[1];
    short_name[0]=StringFormat("sma_fast-slow(%d/%d)",i_fast_sma,i_slow_sma);
    IndicatorSetString(INDICATOR_SHORTNAME,nm);
    PlotIndexSetString(0,PLOT_LABEL,short_name[0]);
    
    g_sma_fast_handle=iMA(NULL,PERIOD_CURRENT,i_fast_sma,0,MODE_SMA,PRICE_CLOSE);
    g_sma_slow_handle=iMA(NULL,PERIOD_CURRENT,i_slow_sma,0,MODE_SMA,PRICE_CLOSE);
    
//---
    return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
//---
    int uncal_bars=rates_total-prev_calculated;
    if (uncal_bars==0) return rates_total;

    if(BarsCalculated(g_sma_fast_handle)<rates_total) return(0);
    if(BarsCalculated(g_sma_slow_handle)<rates_total) return(0);

    if(prev_calculated==0) {
        InitializeAll();
    }

    int to_copy;
    if(prev_calculated>rates_total || prev_calculated<=0) to_copy=rates_total;
    else {
        to_copy=rates_total-prev_calculated;
        //--- last value is always copied
        to_copy++;
    }
//--- try to copy
    if(CopyBuffer(g_sma_fast_handle,0,0,to_copy,ExtWorkBuffer_sma_fast)<=0) return(0);
    if(CopyBuffer(g_sma_slow_handle,0,0,to_copy,ExtWorkBuffer_sma_slow)<=0) return(0);

    if(prev_calculated==0) {
        ArraySetAsSeries(ExtBuffer,true);
        ArraySetAsSeries(ExtWorkBuffer_sma_fast,true);
        ArraySetAsSeries(ExtWorkBuffer_sma_slow,true);
    }

    setSystemReturnArrayAsSeries(time,open,high,low,close,tick_volume,volume,spread);

    int limit=Bars(NULL,PERIOD_CURRENT)-1;
    
    int skip_first_bars=150;
    limit=limit-skip_first_bars;
    int st=uncal_bars;
    if (st>limit) st=limit;

    double firstValue=0;
    for(int i=st+1;i>0 && !IsStopped();i--) {
        double sma_st=ExtWorkBuffer_sma_fast[i]-ExtWorkBuffer_sma_slow[i];
        if (sma_st>0) {
            ExtBuffer[i]=1;
        } else 
        if (sma_st<0) {
            ExtBuffer[i]=-1;
        }
        /*
        //debug
        datetime t=time[i];
        datetime t1=StringToTime("2023.04.27 12:00");
        if (t==t1 && Symbol()=="EURUSD" && Period()==PERIOD_H1) {
            Print("time=[",i,"]=",t);
            printf("macd_st=%g",macd_st);
            printf("ExtBuffer[%d]=%g",i,ExtBuffer[i]);
            printf("ExtWorkBuffer_sma_fast[%d]=%g",i,ExtWorkBuffer_macd_fast[i]);
            printf("ExtWorkBuffer_slow_slow[%d]=%g",i,ExtWorkBuffer_macd_slow[i]);
        }
        */
    }

    ExtBuffer[0]=EMPTY_VALUE;
    
//--- return value of prev_calculated for next call
    return(rates_total);
}
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
//---
   
}
//+------------------------------------------------------------------+
//| ChartEvent function                                              |
//+------------------------------------------------------------------+
void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
{
//---
   
}
//+------------------------------------------------------------------+
void InitializeAll()
{
    ArrayInitialize(ExtBuffer,EMPTY_VALUE);
    ArrayInitialize(ExtWorkBuffer_sma_fast,EMPTY_VALUE);
    ArrayInitialize(ExtWorkBuffer_sma_slow,EMPTY_VALUE);
}
//+------------------------------------------------------------------+
void setSystemReturnArrayAsSeries(
                                  const datetime &time[],
                                  const double &open[],
                                  const double &high[],
                                  const double &low[],
                                  const double &close[],
                                  const long &tick_volume[],
                                  const long &volume[],
                                  const int &spread[])
{
    ArraySetAsSeries(time,true);
    ArraySetAsSeries(open,true);
    ArraySetAsSeries(high,true);
    ArraySetAsSeries(low,true);
    ArraySetAsSeries(close,true);
    ArraySetAsSeries(tick_volume,true);
    ArraySetAsSeries(volume,true);
    ArraySetAsSeries(spread,true);
}
