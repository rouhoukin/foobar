//+------------------------------------------------------------------+
//|                                                 ind_demo_002.mq5 |
//|                                  Copyright 2021, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property indicator_chart_window

#property indicator_buffers 3
#property indicator_plots   2

#property indicator_label1  "buy_ls"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrRed
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1
#property indicator_label2  "sell_ls"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrBlue
#property indicator_style2  STYLE_SOLID
#property indicator_width2  1

//--- indicator buffers
double  ExtBuffer_buy_ls[];
double  ExtBuffer_sell_ls[];
double  ExtWorkBuffer_atr[];

//--- global
int     g_atr_handle;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
//--- indicator buffers mapping
    SetIndexBuffer(0,ExtBuffer_buy_ls,INDICATOR_DATA);
    SetIndexBuffer(1,ExtBuffer_sell_ls,INDICATOR_DATA);
    SetIndexBuffer(2,ExtWorkBuffer_atr,INDICATOR_CALCULATIONS);

    IndicatorSetInteger(INDICATOR_DIGITS,Digits());

//--- sets first bar from what index will be drawn
    PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,10);
    PlotIndexSetInteger(1,PLOT_DRAW_BEGIN,10);

    string nm=StringFormat("buy_sell_ls(%d)",10);
    IndicatorSetString(INDICATOR_SHORTNAME,nm);

    g_atr_handle=iATR(NULL,PERIOD_CURRENT,10);
    
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

    if(BarsCalculated(g_atr_handle)<rates_total) return(0);

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
    if(CopyBuffer(g_atr_handle,0,0,to_copy,ExtWorkBuffer_atr)<=0) return(0);

    if(prev_calculated==0) {
       ArraySetAsSeries(ExtBuffer_buy_ls,true);
       ArraySetAsSeries(ExtBuffer_sell_ls,true);
       ArraySetAsSeries(ExtWorkBuffer_atr,true);
    }

    setSystemReturnArrayAsSeries(time,open,high,low,close,tick_volume,volume,spread);

    int limit=Bars(NULL,PERIOD_CURRENT)-1;
    int skip_first_bars=10;
    limit=limit-skip_first_bars;
    int st=uncal_bars;
    if (st>limit) st=limit;

    double firstValue=0;
    for(int i=st+1;i>0 && !IsStopped();i--) {
        double lst_atr=ExtWorkBuffer_atr[i+1];
        double lst_high=high[i+1];
        double lst_low=low[i+1];
        ExtBuffer_buy_ls[i]=lst_low-lst_atr;
        ExtBuffer_sell_ls[i]=lst_high+lst_atr;
        /*
        //debug
        datetime t=time[i];
        datetime t1=StringToTime("2023.04.27 12:00");
        if (t==t1 && Symbol()=="EURUSD" && Period()==PERIOD_H1) {
            Print("time=[",i,"]=",t);
            printf("ExtBuffer_buy_ls[%d]=%g",i,ExtBuffer_buy_ls[i]);
            printf("ExtBuffer_sell_ls[%d]=%g",i,ExtBuffer_sell_ls[i]);
            printf("ExtWorkBuffer_atr[%d]=%g",i,ExtWorkBuffer_atr[i]);
        }
        */
    }

    ExtBuffer_buy_ls[0]=EMPTY_VALUE;
    ExtBuffer_sell_ls[0]=EMPTY_VALUE;
    ExtWorkBuffer_atr[0]=EMPTY_VALUE;
    
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
    ArrayInitialize(ExtBuffer_buy_ls,EMPTY_VALUE);
    ArrayInitialize(ExtBuffer_sell_ls,EMPTY_VALUE);
    ArrayInitialize(ExtWorkBuffer_atr,EMPTY_VALUE);
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
