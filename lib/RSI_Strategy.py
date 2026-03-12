

import inspect
import logging


def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    
    message_str = '[RSI_LG] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
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
        self.quantity = None


    def update_indicators(self, rsi_15min, rsi_1hr):
        """
        Update RSI values from indicator engine
        """
        self.rsi_15min = rsi_15min.get("RSI")
        self.rsi_1hr = rsi_1hr.get("RSI")
        self.rsi_ma_1hr = rsi_1hr.get("RSI_MA")
        print_log("data --> ", self.rsi_15min,self.rsi_1hr,self.rsi_1hr)


    def check_entry(self):
        """
        Entry logic
        """

        if self.status == "inactive":

            if self.rsi_15min > 52 and self.rsi_1hr > self.rsi_ma_1hr:
                self.place_order("LONG", "ENTRY")
                self.position = "LONG"
                self.status = "active"

            elif self.rsi_15min < 48 and self.rsi_1hr < self.rsi_ma_1hr:
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
        print_log("Run_Strategy")
        self.check_entry()
        self.check_exit()


    def place_order(self, side, action):
        """
        Order execution placeholder
        Replace with broker API call
        """

        print(f"{action} ORDER -> {side}")