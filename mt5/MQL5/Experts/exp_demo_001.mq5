//+------------------------------------------------------------------+
//|                                                 exp_demo_001.mq5 |
//|                                  Copyright 2021, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"

//--- input
input bool  i_debug=true;

//--- global
datetime g_CurrentTimeStamp;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//--- create timer
    EventSetTimer(5);
   
//---
    return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//--- destroy timer
    EventKillTimer();
   
}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    if (isNewBar()) {
        if (i_debug) printf("[%s]%s-%s (isNewBar) is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
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
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| Trade function                                                   |
//+------------------------------------------------------------------+
void OnTrade()
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| TradeTransaction function                                        |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| Tester function                                                  |
//+------------------------------------------------------------------+
double OnTester()
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
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
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| TesterPass function                                              |
//+------------------------------------------------------------------+
void OnTesterPass()
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| TesterDeinit function                                            |
//+------------------------------------------------------------------+
void OnTesterDeinit()
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
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
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
//---
   
}
//+------------------------------------------------------------------+
//| BookEvent function                                               |
//+------------------------------------------------------------------+
void OnBookEvent(const string &symbol)
{
    if (i_debug) printf("[%s]%s-%s is called",TimeToString(g_CurrentTimeStamp,TIME_SECONDS),__FILE__,__FUNCTION__);
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
