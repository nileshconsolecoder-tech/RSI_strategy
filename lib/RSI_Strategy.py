

import inspect
import logging


def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    
    message_str = '[RSI_STG] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    full_message = f'{message_str}'
    
    print(full_message)
    logging.info(full_message)



class RSIStrategy:

    def __init__(self):
        

        self.rsi_15min = None
        self.rsi_1hr = None
        self.rsi_ma_1hr = None

        self.status = "inactive"   # inactive / active
        self.position = None       # LONG / SHORT
        self.quantity = 0
        self.ltp = 0.00
        self.INSTRUMENT_TOKEN = None
        self.rsi_strategy_status = "OFF"
        self.Manual_EXIT = False
        self.AVG = 0.00
        self.rsi_15min_upper = 52
        self.rsi_15min_lower = 48


    def update_ltp(self,ltp_dict):
        if(self.INSTRUMENT_TOKEN != None):
            self.ltp = ltp_dict.get(self.INSTRUMENT_TOKEN, 0.00)
            # print_log("self.ltp -->>> ",self.ltp)
        

    def update_indicators(self, rsi_15min, rsi_1hr):
        """
        Update RSI values from indicator engine
        """
        self.rsi_15min = rsi_15min.get("RSI")
        self.rsi_1hr = rsi_1hr.get("RSI")
        self.rsi_ma_1hr = rsi_1hr.get("RSI_MA")
        # print_log("data --> ", self.rsi_15min,self.rsi_1hr,self.rsi_ma_1hr)

    def check_entry(self):
        """
        Entry logic
        """
        # print_log("rsi range : ", self.rsi_15min_lower,self.rsi_15min_upper)

        if self.status == "inactive":

            if self.rsi_15min > self.rsi_15min_upper and self.rsi_1hr > self.rsi_ma_1hr:
                self.AVG = self.ltp
                self.place_order("LONG", "ENTRY")
                self.position = "LONG"
                self.status = "active"

            elif self.rsi_15min < self.rsi_15min_lower and self.rsi_1hr < self.rsi_ma_1hr:
                self.AVG = self.ltp
                self.place_order("SHORT", "ENTRY")
                self.position = "SHORT"
                self.status = "active"


    def check_exit(self):
        """
        Exit logic
        """

        if self.status == "active":

            # Exit LONG
            if self.position == "LONG":

                if self.rsi_1hr < self.rsi_ma_1hr:
                    self.place_order("LONG", "EXIT")
                    self.position = None
                    self.status = "inactive"

            # Exit SHORT
            elif self.position == "SHORT":
                
                if self.rsi_1hr > self.rsi_ma_1hr:
                    self.place_order("SHORT", "EXIT")
                    self.position = None
                    self.status = "inactive"


    def run_strategy(self):
        """
        Strategy loop
        """
        # print_log("Run_Strategy")

        
        if(self.rsi_strategy_status == "ON"):
            print_log("RSI_strategy status : ",self.rsi_strategy_status)
            self.check_entry()
            self.check_exit()
        if(self.Manual_EXIT == True):
            print_log("Manual_exit : ", self.Manual_EXIT)
            self.check_manual_exit()
            self.Manual_EXIT = False
            

    
    def check_manual_exit(self):
        if(self.status == "active"):
            self.place_order(side=self.position,action="EXIT_MANUALLY")
            print_log("SELF EXIT TRIGGER")
            self.position = None
            self.status = "inactive"
            self.AVG = 0.00
            self.rsi_strategy_status = "OFF"
            self.Manual_EXIT = False

    def place_order(self, side, action):
        """
        Order execution placeholder
        Replace with broker API call
        """
        self.order = side 
        print(f"{action} ORDER -> {side} at LTP  : {self.ltp}")