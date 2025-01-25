//+------------------------------------------------------------------+
//|                                                 exp_demo_002.mq5 |
//|                                  Copyright 2025, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"

//--- input
input string    i_sig_ind="ind_demo_001";   //i_sig_ind:for in and out signal
input string    i_lvl_ind="ind_demo_002";   //i_lvl_ind:for stop loss level
input bool      i_debug=true;

//--- global
datetime    g_CurrentTimeStamp;

int         g_sig_in_handle;
int         g_sig_out_handle;
int         g_lvl_handle;
int         g_sig_in;
int         g_sig_out;
double      g_buy_ls;
double      g_sell_ls;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//--- create timer
    //EventSetTimer(5);

    g_sig_in_handle=iCustom(NULL,PERIOD_CURRENT,i_sig_ind,600,120);
    g_sig_out_handle=iCustom(NULL,PERIOD_CURRENT,i_sig_ind,600,120);
    g_lvl_handle=iCustom(NULL,PERIOD_CURRENT,i_lvl_ind);
   
    updateStatus();
    
//---
    return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//--- destroy timer
    //EventKillTimer();
   
}
//+------------------------------------------------------------------+
//| update status function                                 |
//+------------------------------------------------------------------+
void updateStatus()
{
    double  buffer[2];
    
    int     lst_sig,sec_lst_sig;
    lst_sig=sec_lst_sig=0;

    //update signal in status
    if (g_sig_in_handle>0) {
        if(CopyBuffer(g_sig_in_handle,0,1,2,buffer)<=0) return;
        if (buffer[0]!=EMPTY_VALUE) sec_lst_sig=(int)buffer[0];
        if (buffer[1]!=EMPTY_VALUE) lst_sig=(int)buffer[1];
        g_sig_in=lst_sig;
        if (i_debug) {
            printf("update signal in:g_sig_in=%d",g_sig_in);
        }
    }

    //update signal out status
    if (g_sig_out_handle>0) {
        if(CopyBuffer(g_sig_out_handle,0,1,2,buffer)<=0) return;
        if (buffer[0]!=EMPTY_VALUE) sec_lst_sig=(int)buffer[0];
        if (buffer[1]!=EMPTY_VALUE) lst_sig=(int)buffer[1];
        g_sig_out=lst_sig;
        if (i_debug) {
            printf("update signal out:g_sig_out=%d",g_sig_out);
        }
    }

    double  lst_sl,sec_lst_sl;
    lst_sl=sec_lst_sl=0;

    //update buy and sell stop loss level status
    if (g_lvl_handle>0) {
        if(CopyBuffer(g_lvl_handle,0,1,2,buffer)<=0) return;
        if (buffer[0]!=EMPTY_VALUE) sec_lst_sl=buffer[0];
        if (buffer[1]!=EMPTY_VALUE) lst_sl=buffer[1];
        g_buy_ls=lst_sl;
        if (i_debug) {
            printf("update buy ls:g_buy_ls=%g",g_buy_ls);
        }
        
        if(CopyBuffer(g_lvl_handle,1,1,2,buffer)<=0) return;
        if (buffer[0]!=EMPTY_VALUE) sec_lst_sl=buffer[0];
        if (buffer[1]!=EMPTY_VALUE) lst_sl=buffer[1];
        g_sell_ls=lst_sl;
        if (i_debug) {
            printf("update sell ls:g_sell_ls=%g",g_sell_ls);
        }
    }

}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    if (isNewBar()) {
        //if (i_debug) printf("[%s]%s-%s (isNewBar) is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
        updateStatus();
    } else {
        //if (i_debug) printf("%s is called and not new bar",__FUNCTION__);
    }
//---
   
}
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| Trade function                                                   |
//+------------------------------------------------------------------+
void OnTrade()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| TradeTransaction function                                        |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| Tester function                                                  |
//+------------------------------------------------------------------+
double OnTester()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
    double ret=0.0;
//---

//---
    return(ret);
}
//+------------------------------------------------------------------+
//| TesterInit function                                              |
//+------------------------------------------------------------------+
void OnTesterInit()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| TesterPass function                                              |
//+------------------------------------------------------------------+
void OnTesterPass()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| TesterDeinit function                                            |
//+------------------------------------------------------------------+
void OnTesterDeinit()
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
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
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| BookEvent function                                               |
//+------------------------------------------------------------------+
void OnBookEvent(const string &symbol)
{
    //if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
// isNewBar: check new bar
// ret:  0, no new bar
//       1, new bar, barshift=1
//+------------------------------------------------------------------+
bool isNewBar()
{
    if (g_CurrentTimeStamp != iTime(NULL,PERIOD_CURRENT,0)) {
        g_CurrentTimeStamp = iTime(NULL,PERIOD_CURRENT,0);
        return true;
    } else {
        return false;
    }
}
