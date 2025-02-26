//+------------------------------------------------------------------+
//|                                                  script_test.mq5 |
//|                                  Copyright 2025, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
//---
    datetime dt_now=TimeCurrent();
    datetime date_from=dt_now;              // take all events from now
    int pd_sec=3600;                        // one hour
    datetime date_to=date_from+pd_sec;      // take all events in next one hour

    MqlCalendarValue values[];
    string country="US";     //country code=US
    int values_count=CalendarValueHistory(values,date_from,date_to);
//--- move along the detected event values
    string evts_nm[];
    datetime evts_dt[];
    printf("values_count=%d",values_count);
    if(values_count>0) {
        ArrayResize(evts_nm,values_count);
        ArrayResize(evts_dt,values_count);
        for(int j=0;j<ArraySize(values);j++) {
            MqlCalendarValue value=values[j];
            MqlCalendarEvent event;
            CalendarEventById(value.event_id,event);
            
            //debug
            //--- prepare a event description
            string descr="event_id = "+IntegerToString(event.id)+"\n";
            descr+=("name = " + event.name+"\n");
            descr+=("importance = " + EnumToString(event.importance)+"\n");
            //--- prepare a event description
            //--- prepare a event value description
            descr+=("value_id = " + IntegerToString(value.id)+"\n");
            descr+=("time = " + TimeToString(value.time)+"\n");
            //--- display a event value description
            Print(descr);
        }
    }
}
//+------------------------------------------------------------------+
