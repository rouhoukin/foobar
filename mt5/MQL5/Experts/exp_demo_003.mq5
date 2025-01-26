//+------------------------------------------------------------------+
//|                                                 exp_demo_003.mq5 |
//|                                  Copyright 2025, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"

//--- input
input string    i_sig_ind="ind_demo_001";   //i_sig_ind:for in and out signal
input string    i_lvl_ind="ind_demo_002";   //i_sta_ind:for stop loss level
input double    i_lots=0.01;                //i_lots:
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
ulong       g_order_tic=0;
bool        g_has_buy_order=false;
bool        g_has_sell_order=false;

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
    //update order status
    g_has_buy_order=false;
    g_has_sell_order=false;
    if (g_order_tic>0) {
        if (PositionSelectByTicket(g_order_tic)) {
            ENUM_ORDER_TYPE tp=(ENUM_ORDER_TYPE)PositionGetInteger(POSITION_TYPE);
            if (tp==ORDER_TYPE_BUY) {
                g_has_buy_order=true;
            }
            if (tp==ORDER_TYPE_SELL) {
                g_has_sell_order=true;
            }
        } else
            g_order_tic=0;
    }
    
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
    double Bid = SymbolInfoDouble(Symbol(),SYMBOL_BID);
    double Ask = SymbolInfoDouble(Symbol(),SYMBOL_ASK);
    //update buy stop loss level status
    lst_sl=sec_lst_sl=0;
    if (g_lvl_handle>0) {
        if(CopyBuffer(g_lvl_handle,0,1,2,buffer)<=0) return;
        if (buffer[0]!=EMPTY_VALUE) sec_lst_sl=buffer[0];
        if (buffer[1]!=EMPTY_VALUE) lst_sl=buffer[1];
    }    
    g_buy_ls=lst_sl;
    if (g_buy_ls==0) {
        g_buy_ls=Bid-100*Point();
    }
    if (i_debug) {
        printf("update buy ls:g_buy_ls=%g",g_buy_ls);
    }
    //update sell stop loss level status
    lst_sl=sec_lst_sl=0;
    if (g_lvl_handle>0) {
        if(CopyBuffer(g_lvl_handle,1,1,2,buffer)<=0) return;
        if (buffer[0]!=EMPTY_VALUE) sec_lst_sl=buffer[0];
        if (buffer[1]!=EMPTY_VALUE) lst_sl=buffer[1];
    }
    g_sell_ls=lst_sl;
    if (g_sell_ls==0) {
        g_sell_ls=Ask+100*Point();
    }
    if (i_debug) {
        printf("update sell ls:g_sell_ls=%g",g_sell_ls);
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
        ifClose();
        open_order();
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
void open_order()
{
    if (g_sig_in>0) {
        if (g_has_buy_order) {
            printf("Already has buy order(%I64u), do nothing.",g_order_tic);
            return;
        }
        if (g_has_sell_order) {
            printf("Already has opposit order(%I64u), do nothing.",g_order_tic);
            return;
        }
        if (g_sig_out<0) {
            printf("out signal is opposit, do nothing.");
            return;
        }
        ulong tic=0;
        if (OrderBuy(g_buy_ls,0,0,"",tic,i_lots)) {
            printf("buy order opened, tic=%I64u.",tic);
            g_order_tic=tic;
            g_has_buy_order=true;
        }
    }
    if (g_sig_in<0) {
        if (g_has_sell_order) {
            printf("Already has sell order(%I64u), do nothing.",g_order_tic);
            return;
        }
        if (g_has_buy_order) {
            printf("Already has opposit order(%I64u), do nothing.",g_order_tic);
            return;
        }
        if (g_sig_out>0) {
            printf("out signal is opposit, do nothing.");
            return;
        }
        ulong tic=0;
        if (OrderSell(g_sell_ls,0,0,"",tic,i_lots)) {
            printf("sell order opened, tic=%I64u.",tic);
            g_order_tic=tic;
            g_has_sell_order=true;
        }
    }
}
//+------------------------------------------------------------------+
// OrderBuy
// argLsPrice: Loss Stop Value (0 for not set, use LossStopPt)
// argPsPrice: Profit Stop Value (0 for not set)
// argCom: Comment
// argMag: Magic
//+------------------------------------------------------------------+
bool OrderBuy(double argLsPrice, double argPsPrice, int argMag, string argCom, ulong& argTic, double argLots=0)
{
    double price = SymbolInfoDouble(Symbol(),SYMBOL_ASK);
    
    ENUM_TRADE_REQUEST_ACTIONS act = TRADE_ACTION_DEAL;
    ENUM_ORDER_TYPE cmd = ORDER_TYPE_BUY;

    double ls_price;
    double ls_pt;
    double pt = Point();
    if (argLsPrice == 0) {
        ls_price = NormalizeDouble(price - 100 * pt, Digits());
	    ls_pt = 100;
    } else {
        ls_price = argLsPrice;
        ls_pt = NormalizeDouble((price - ls_price) / pt, 0);
    }
   
    double risk_vol=argLots;
    if (risk_vol<0.01) {
        Print("Not enough lots to open ",risk_vol);
        return false;
    }
   
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    request.action = act;
    request.type = cmd;
    request.type_filling = ORDER_FILLING_IOC;   //depend on broker
    request.symbol = Symbol();
    request.price = price;
    request.deviation = 5;
    request.volume = risk_vol;
    request.sl = ls_price;
    request.tp = 0;
    request.magic = argMag;
    request.comment = argCom;

    if (i_debug)
        printf("cmd=%d;vol=%g;pt=%g;pc=%g;ls=%g;lspt=%g;",cmd,risk_vol,pt,price,ls_price,ls_pt);

    bool ret = false;
    ResetLastError();
    ret = OrderSend(request,result);
    
    if (!ret) {
        int check = GetLastError();
        // if unable to send the request, output the error code
        Print(__FUNCTION__,": ",result.comment," reply code ",result.retcode); 
    }
    
    if (ret) {
        argTic = result.order;
        return true;
    }
    else return false;
}
//+------------------------------------------------------------------+
// OrderSell
// argLsPrice: Loss Stop Value (0 for not set, use LossStopPt)
// argPsPrice: Profit Stop Value (0 not set profit stop)
// argCom: Comment
// argMag: Magic
//+------------------------------------------------------------------+
bool OrderSell(double argLsPrice, double argPsPrice, int argMag, string argCom, ulong& argTic, double argLots=0)
{
    double price = SymbolInfoDouble(Symbol(),SYMBOL_BID);
    
    ENUM_TRADE_REQUEST_ACTIONS act = TRADE_ACTION_DEAL;
    ENUM_ORDER_TYPE cmd = ORDER_TYPE_SELL;
    
    double ls_price;
    double ls_pt;
    double pt = Point();
    if (argLsPrice == 0) {
        ls_price = NormalizeDouble(price + 100 * pt, Digits());
	    ls_pt = 100;
    } else {
        ls_price = argLsPrice;
        ls_pt = NormalizeDouble((ls_price - price) / pt, 0);
    }
    
    double risk_vol=argLots;
    if (risk_vol<0.01) {
        Print("Not enough lots to open ",risk_vol);
        return false;
    }
   
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    request.action = act;
    request.type = cmd;
    request.type_filling = ORDER_FILLING_IOC;   //depend on broker
    request.symbol = Symbol();
    request.price = price;
    request.deviation = 5;
    request.volume = risk_vol;
    request.sl = ls_price;
    request.tp = 0;
    request.magic = argMag;
    request.comment = argCom;

    if (i_debug)
        printf("cmd=%d;vol=%g;pt=%g;pc=%g;ls=%g;lspt=%g;",cmd,risk_vol,pt,price,ls_price,ls_pt);

    bool ret = false;
    ResetLastError();
    ret = OrderSend(request,result);
    
    if (!ret) {
        int check = GetLastError();
        // if unable to send the request, output the error code
        Print(__FUNCTION__,": ",result.comment," reply code ",result.retcode); 
    }
    
    if (ret) {
        argTic = result.order;
        return true;
    }
    else return false;
}
bool OrderClose(ulong argTic)
{
    if (PositionSelectByTicket(argTic)) {
        string  ord_symbol = PositionGetString(POSITION_SYMBOL);    // symbol
        double  ord_volume = PositionGetDouble(POSITION_VOLUME);    // volume of the position
        ENUM_POSITION_TYPE ord_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);    // type of the position

        MqlTradeRequest request={};
        MqlTradeResult  result={};
        //--- zeroing the request and result values
        ZeroMemory(request);
        ZeroMemory(result);
        //--- setting the operation parameters
        request.action      = TRADE_ACTION_DEAL;    // type of trade operation
        request.position    = argTic;               // ticket of the position
        request.symbol      = ord_symbol;           // symbol
        request.volume      = ord_volume;           // volume of the position
        request.deviation   = 5;                    // allowed deviation from the price
        request.comment     = "close";              // comment
        request.type_filling = ORDER_FILLING_IOC;
        //--- set the price and order type depending on the position type
        if(ord_type==POSITION_TYPE_BUY) {
            request.price=SymbolInfoDouble(ord_symbol,SYMBOL_BID);
            request.type =ORDER_TYPE_SELL;
        } else {
            request.price=SymbolInfoDouble(ord_symbol,SYMBOL_ASK);
            request.type =ORDER_TYPE_BUY;
        }
        //--- output information about the closure
        //PrintFormat("Close #%I64d %s %s",ord_ticket,ord_symbol,EnumToString(ENUM_POSITION_TYPE(ord_type)));
        //--- send the request
        if(!OrderSend(request,result)) {
            PrintFormat("OrderSend error %d",GetLastError());  // if unable to send the request, output the error code
            //--- information about the operation   
            PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);
            return false;
        } else {
            //--- information about the operation   
            //PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);
            return true;
        }
    }
    return false;
}
void ifClose()
{
    if (g_sig_out<0 && g_has_buy_order) {
        printf("Opposit signal out, close buy order(%I64u).",g_order_tic);    
        if (OrderClose(g_order_tic)) {
            g_has_buy_order=false;
        }
    }
    if (g_sig_out>0 && g_has_sell_order) {
        printf("Opposit signal out, close sell order(%I64u).",g_order_tic);    
        if (OrderClose(g_order_tic)) {
            g_has_sell_order=false;
        }
    }
}