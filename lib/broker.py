import sourcedefender
# =========================
# Standard Library Imports
# =========================
import asyncio
import gzip
import hashlib
import json
import logging
import os
import random
import struct
import threading
import time as tk
import urllib
import webbrowser
import zlib
from datetime import datetime, timedelta
from datetime import datetime, time
from io import StringIO
from typing import Dict, List
from urllib import parse
import requests
import time as timetk
import random

# =========================
# Third-Party Imports
# =========================
import httpx
import numpy as np
import orjson
import pandas as pd
import pyotp
import requests
import websocket
from kiteconnect import KiteConnect, KiteTicker

# =========================
# Internal / Project Imports
# =========================



# def print_log(*args):
# 	message_str = '[BR] ' + ' '.join(map(str, args))
# 	print(message_str)
# 	logging.info(message_str)

import inspect

def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    
    message_str = '[BR] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    full_message = f'{message_str}'
    
    print(full_message)
    logging.info(full_message)


class brokerSession:
    
    def __init__(self, config_dict):
        
        self.config_dict = config_dict
        
        self.api_key = self.config_dict.get("api_key")
        self.api_secret = self.config_dict.get("api_secret")
        self.totp_key  = self.config_dict.get('totp_key')
        self.client_id = self.config_dict.get("client_id")
        
        self.access_token = None
        self.password = self.config_dict.get("password")
        
        self.index_hub		    = {} 
        self.oc_hub 			= {}
        self.instrument_token_dict = {}
        self.contract_hub = {}
        self.ltp_dict = {}
        self.hist_data = {}
        self.tradingsymbol= {}

        self.index_futures_record = {}
        self.orderbook_details = {}
        
        self.bid_ask_dict = {}
        self.instrument_token = {}
        self.m2m = 0
        self.positions = {}
        self.order_details = {} #all Orders Details as per ORder ID

        self.freeze_lotsize_dict = self.fetch_freeze_limit_data()

        self.do_login(self.api_key, self.api_secret)
        self.get_profile()
        self.load_india_holidays()
        # self.get_funds()
        self.process_index_instrument_tokens()
        # self.download_instrument_tokens()
        # self.get_positions()
        # print_log("core part is done ")
        # self.start_websocket()

    def do_login(self, api_key, api_secret):
        self.kite = KiteConnect(api_key=api_key)
        # print_log(self.kite.__dict__)
        json_path = 'etc/token.json'
        current_date = datetime.today().date()
        try:
            with open(json_path) as json_file:
                data = json.load(json_file)
                access_token = data.get("access_token")
                access_token_date = data.get("date")
            
            try:
                self.kite.set_access_token(access_token)
                # print_log("try",self.kite.__dict__)
                self.kite.profile()
                # print_log("profile : ", self.kite.profile().keys())
                # print_log("Login Successful")
            except Exception as e:
                print_log("Access token is missing or expired. Starting re-authentication...")
                access_token = self.fetch_access_token()
                
                with open(json_path, 'w') as f:
                    json.dump({
                        'access_token': access_token,
                        'date': str(current_date)
                    }, f)
               
                # print_log("New access token generated and saved.")
            self.kite.set_access_token(access_token)
            # print_log("out try 1 : ",self.kite.__dict__ )
            self.access_token = access_token
            self.kws = KiteTicker(api_key, access_token)
            # print_log("final self.kws : ", self.kws.__dict__.keys())
        
        except Exception as e:
            print_log(f"Error loading or generating access token: {e}")
    
    def fetch_access_token(self):
        print_log(" hhh ")
        try:
            KITE_HOME_URL = "https://kite.zerodha.com"
            AUTH_LOGIN_URL = f"{KITE_HOME_URL}/api/login"
            AUTH_2FA_URL = f"{KITE_HOME_URL}/api/twofa"
            AUTH_REDIRECT_URL = f"{KITE_HOME_URL}/connect/login"
            KITE_API_URL = "https://api.kite.trade/session/token"

            with httpx.Client(timeout=20) as client:
                # Establish base session
                client.get(KITE_HOME_URL)

                # ---- Primary Authentication ----
                auth_payload = {
                    "user_id": self.client_id,
                    "password": self.password,
                    "type": "user_id"
                }

                auth_response = client.post(AUTH_LOGIN_URL, data=auth_payload).json()
                # print_log("auth_responce : ",auth_response)
                if auth_response.get("status") != "success":
                    raise Exception("Primary authentication failed")

                auth_data = auth_response["data"]

                # ---- TOTP Verification ----
                otp_code = pyotp.TOTP(self.totp_key).now()
                otp_payload = {
                    "user_id": auth_data["user_id"],
                    "request_id": auth_data["request_id"],
                    "twofa_value": otp_code,
                    "twofa_type": "totp",
                    "skip_session": ""
                }

                tk.sleep(random.uniform(0.1, 1.0))

                otp_response = client.post(AUTH_2FA_URL, data=otp_payload).json()

                if otp_response.get("status") != "success":
                    raise Exception("TOTP verification failed")

                # ---- Request Token Extraction ----
                login_params = {
                    "v": "3",
                    "api_key": self.api_key
                }

                redirect_response = client.get(
                    AUTH_REDIRECT_URL,
                    params=login_params,
                    follow_redirects=True
                )

                redirect_location = str(redirect_response.url)

                if "request_token=" not in redirect_location:
                    raise Exception("Missing request_token in redirect URL")

                from urllib.parse import urlparse, parse_qs

                token_query = parse_qs(urlparse(redirect_location).query)
                req_token = token_query.get("request_token", [None])[0]

                if not req_token:
                    raise Exception("Invalid request_token")

                # ---- Access Token Generation ----
                token_checksum = hashlib.sha256(
                    f"{self.api_key}{req_token}{self.api_secret}".encode()
                ).hexdigest()

                session_response = client.post(
                    KITE_API_URL,
                    data={
                        "api_key": self.api_key,
                        "request_token": req_token,
                        "checksum": token_checksum
                    }
                ).json()

                if session_response.get("status") != "success":
                    raise Exception("Access token creation failed")

                return session_response["data"]["access_token"]

        except Exception as err:
            raise RuntimeError("Zerodha authentication workflow failed") from err


    def get_profile(self):
        try:
            profile_data = self.kite.profile()
            # print_log("Profile_data : ", profile_data.keys())
            self.client_id = profile_data['user_id']
            # print_log("client_id : ", self.client_id)
            # print_log(f"final Welcome {profile_data['user_name']}")
            self.user_name = profile_data['user_name']
            
        except Exception as e:
            print_log(f"Error fetching user profile: {e}")

    def get_funds(self):
        try:
            api_response = self.kite.margins()['equity']
            # print_log("api responce : ",api_response)
            # self.total_funds = data['']
            # print_log(api_response)
            self.total_funds = int(api_response['available']['opening_balance'] + api_response['available']['collateral']+ api_response['available']['intraday_payin'])
            # print_log(" final self.Total_funds : ", self.total_funds)

        except Exception as e:
            print_log("Error in get_funds", e)
    
    def get_positions(self):
        try:
            positions_response = self.kite.positions()
            # positions_response = self.positions or {}
            # print_log(positions_response)
            response = self.filter_positions(positions_response)
            # print_log("[+] positions_responce log --> ",response)
            return response

        except Exception as e:
            print_log("Error in get_positions", e)
            return []
        
    def get_pnl(self):
        self.m2m = random.randint(-1000, 1000)
        # print_log("m2m = " , self.m2m)
    
    def trading_symbol_formater(self, instrument_token):
        try:
            value = self.instrument_token.get(instrument_token)
            
            name = value["name"]                    # "NIFTY"
            expiry_str = value["expiry"]            # "2025-09-02"
            strike = int(value["strike"])           # 24450
            opt_type = value["instrument_type"]     # "CE"

            # === Format expiry (DD MON) ===
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            day = expiry_date.strftime("%d")        # "02"
            month = expiry_date.strftime("%b").upper()  # "SEP"
            expiry = f"{day} {month}"

            # === Final formatted trading symbol ===
            trading_symbol = f"{name} {expiry} {strike}{opt_type}"
            return trading_symbol

        except Exception as e:
            print_log("Error in trading_symbol_formater", e)
            return None

    def filter_positions(self, positions):
        try:

            # print_log("[filter_postioons] postions : ",positions)
            self.m2m = 0
            positions_hub = {}

            for idx, pos in enumerate(positions):

                ltp = self.get_ltp(pos['instrument_token'])
                if ltp is None or pos['exchange'] not in ['NFO', 'BFO']:
                    continue

                pos['pnl'] = (pos['sell_value'] - pos['buy_value']) + (pos['quantity'] * ltp * pos['multiplier'])
                
                totalpnl = pos['pnl']
                
                positions_hub[idx] = {
                    'timestamp' :  datetime.now(),
                    'pnl': totalpnl,
                    'quantity': pos['quantity'],
                    'average_price': pos['average_price'],
                    'lots': self.quantity_to_lot2(pos['quantity'], pos['instrument_token']),
                    'ltp': ltp,
                    'modifiedTradingsymbol': self.trading_symbol_formater(pos['instrument_token']),
                    'index': idx,
                    'tradingSymbol': pos['tradingsymbol'],
                    'instrument_token': pos['instrument_token'],
                }

                self.m2m +=  positions_hub[idx]['pnl']
                # print_log("[filter_positions] positionals_hub : ", positions_hub)
                # print_log("[filter_positions] len of self.m2m : ", len(self.m2m))

            return positions_hub
        except Exception as e:
            print_log("Error in filter_positions", e)
        
        return positions_hub 

    def get_orderbook(self):
        try:
            response = self.kite.orders()
            filtered_orderbook = self.filter_orderbook(response)	
            return filtered_orderbook
        except Exception as e:
            print_log("Error in get_orderbook", e)
            return []
        
    def filter_orderbook(self, orders):
        try:
            open_orders = []
            closed_orders = []

            if not isinstance(orders, list):
                return []

            for order in orders:
                if not isinstance(order, dict):
                    continue

                normalized_order = order.copy()
                timestamp = normalized_order.get("order_timestamp")
                if timestamp is not None:
                    timestamp_text = str(timestamp).strip()
                    if " " in timestamp_text:
                        timestamp_text = timestamp_text.split(" ")[-1]
                    elif "T" in timestamp_text:
                        timestamp_text = timestamp_text.split("T")[-1]
                    if "." in timestamp_text:
                        timestamp_text = timestamp_text.split(".")[0]
                    if "+" in timestamp_text:
                        timestamp_text = timestamp_text.split("+")[0]
                    normalized_order["order_timestamp"] = timestamp_text

                status = str(normalized_order.get("status", "")).upper()
                if status in ("OPEN", "TRIGGER PENDING"):
                    open_orders.append(normalized_order)
                else:
                    closed_orders.append(normalized_order)

            return open_orders + closed_orders
        except Exception as e:
            print_log("Error in filter_orderbook", e)
            return []

    def download_instrument_tokens(self):
        print_log("\n \t[+] Loading instrument token file... Please wait. (Zerodha may take 4-5 minutes to download the instruments.)")	

        url = requests.get("https://api.kite.trade/instruments")
        url.raise_for_status()
        self.df      = pd.read_csv(StringIO(url.text))
        self.df.to_csv("output.csv", index=False) 
        self.pre_process_instrument_tokens()
        print_log("final call self.pre_process_instrument_tokens()")
        # self.pre_process_futures_instrument_tokens()

    def process_index_instrument_tokens(self):
            
        self.index_hub['NIFTY']            = 256265
        self.index_hub['BANKNIFTY']        = 260105
        self.index_hub['FINNIFTY']         = 257801
        self.index_hub['MIDCPNIFTY']       = 288009
        self.index_hub['BANKEX']           = 274441
        self.index_hub['SENSEX']           = 265
        # print_log("updated the self.index hub : ", self.index_hub )
        

    def fetch_freeze_limit_data(self):

        try:
            # 1️⃣ Fetch NSE index data from API
            response = requests.get(
                'https://9mbqrxwx53.execute-api.ap-south-1.amazonaws.com/default/lotsize_freeze_limits',
                timeout=5
            )
            print_log("responce_status :",response)
            response.raise_for_status()
            index_data = response.json() or {}
            # print_log("index_data : ", index_data)


            # 2️⃣ Fetch MCX commodity config
            commodity_data = self.fetch_freeze_limit_data_commodities()
            # print_log("[hardcoded] commodity_data", commodity_data)

            # 3️⃣ Merge both into ONE dict
            # Commodity data will not overwrite index data unless same key exists
            unified_data = {**index_data, **commodity_data}
            # print_log("unified_data : ",unified_data)
            print_log(f"final log len of index_data :{len(index_data)} , len of commodity_data : {len(commodity_data)} , len of Unified_data :{len(unified_data)}")
            return unified_data

        except Exception as e:
            print_log("Error in fetch_freeze_limit_data", e)
            # fallback to commodities only (system should still run)
            return self.fetch_freeze_limit_data_commodities()
        


    def fetch_freeze_limit_data_commodities(self):
        try:
            return {
                "ALUMINIUM": {"lot_size": 150, "freeze_limit": 150, "strike_mul": 1},
                "COPPER": {"lot_size": 1, "freeze_limit": 70000, "strike_mul": 1},
                "COTTON": {"lot_size": 1200, "freeze_limit": 1200, "strike_mul": 1},
                "CRUDEOIL": {"lot_size": 100, "freeze_limit": 10000, "strike_mul": 1},
                "GOLD": {"lot_size": 100, "freeze_limit": 100, "strike_mul": 1},
                "GOLDGUINEA": {"lot_size": 1, "freeze_limit": 10000, "strike_mul": 1},
                "GOLDM": {"lot_size": 100, "freeze_limit": 10000, "strike_mul": 1},
                "GOLDPETAL": {"lot_size": 1, "freeze_limit": 10000, "strike_mul": 1},
                "KAPAS": {"lot_size": 200, "freeze_limit": 200, "strike_mul": 1},
                "LEAD": {"lot_size": 1, "freeze_limit": 100, "strike_mul": 1},
                "MCXBULDEX": {"lot_size": 1, "freeze_limit": 4000, "strike_mul": 1},
                "MCXENRGDEX": {"lot_size": 1, "freeze_limit": 10000, "strike_mul": 1},
                "MCXMETLDEX": {"lot_size": 1, "freeze_limit": 4000, "strike_mul": 1},
                "MENTHAOIL": {"lot_size": 1, "freeze_limit": 18000, "strike_mul": 1},
                "NATURALGAS": {"lot_size": 1250, "freeze_limit": 60000, "strike_mul": 1},
                "NICKEL": {"lot_size": 1, "freeze_limit": 24000, "strike_mul": 1},
                "RUBBER": {"lot_size": 50, "freeze_limit": 50, "strike_mul": 1},
                "SILVER": {"lot_size": 30, "freeze_limit": 600, "strike_mul": 1},
                "SILVERM": {"lot_size": 5, "freeze_limit": 600, "strike_mul": 1},
                "SILVERMIC": {"lot_size": 1, "freeze_limit": 600, "strike_mul": 1},
                "ZINC": {"lot_size": 1, "freeze_limit": 100, "strike_mul": 1}
                }

        except Exception as e:
            pass
    

    def load_india_holidays(self):
        """
        Loads Indian holidays from Sensibull API once at startup.
        Stores inside self.india_holidays as a Python set of dates.
        """
    

        url = "https://oxide.sensibull.com/v1/compute/get_holiday_calendar"
        india_holidays = set()

        try:
            resp = requests.get(url, headers={"Accept": "application/json"}).json()
            data = resp.get("payload", {}).get("data", [])

            for h in data:
                if h.get("country") == "India":     # only Indian market holidays
                    india_holidays.add(h["date"])   # YYYY-MM-DD string

        except Exception as e:
            print("Error loading holidays:", e)

        self.india_holidays = india_holidays
        # print_log(self.india_holidays)
        # print("Loaded India holidays:")

    def get_last_trading_day(self):
        """
        Returns last trading day considering:
        - Saturday, Sunday
        - India holidays stored in self.india_holidays
        """
        today = datetime.today().date()
        check_date = today - timedelta(days=1)

        while True:
            # weekend
            if check_date.weekday() >= 5:  # Sat=5, Sun=6
                check_date -= timedelta(days=1)
                continue

            # holiday
            if check_date.strftime("%Y-%m-%d") in self.india_holidays:
                check_date -= timedelta(days=1)
                continue

            return check_date
    
    def get_last_closed_time(self, timeframe):
        now = datetime.now().time()

        minute = (now.minute // timeframe) * timeframe
        floored_time = time(hour=now.hour, minute=minute)

        # subtract one candle
        last_closed_minute = minute - timeframe
        last_hour = now.hour

        if last_closed_minute < 0:
            last_closed_minute += 60
            last_hour -= 1

        return time(hour=last_hour, minute=last_closed_minute)

    
    def pre_process_instrument_tokens(self):
        try:
            print_log("Pre-processing instrument tokens...")
            # self.index_to_trade = ['SENSEX', 'NIFTY', 'BANKNIFTY', 'MIDCPNIFTY', 'BANKEX', 'FINNIFTY']

            self.instrument_token = {}
            self.tradingsymbol = {}
            print_log("self.df shape :", self.df.shape)
            for _, data in self.df.iterrows():
                value = data.to_dict()
                instrument_token = value.get('instrument_token')
                trading_symbol = value.get('tradingsymbol')

                if instrument_token is not None:
                    self.instrument_token[instrument_token] = value

                if trading_symbol:
                    self.tradingsymbol[trading_symbol] = value

            print_log(f"final Loaded {len(self.instrument_token)} instrument tokens and {len(self.tradingsymbol)} trading symbols")

        except Exception as e:
            print_log("Error in pre_process_instrument_tokens", e)



    def expiry_dates(self, index):
        dates = sorted(self.contract_hub[index].keys())
        return dates
        
    def _ensure_position(self, token, symbol, exchange):
        if token not in self.positions:
            self.positions[token] = {
                "tradingsymbol": symbol,
                "exchange": exchange,
                "BQ": 0,
                "SQ": 0,
                "BA": 0.0,
                "SA": 0.0,
        }

    # def place_order(self, record):
    
    #     try:
            
    #         print_log(f"Placing order: {record}")
    #         order_id = self.kite.place_order(
    #             variety="regular",
    #             exchange=record['exchange'],
    #             tradingsymbol=record['tradingsymbol'],
    #             transaction_type=record['transaction_type'],
    #             quantity=record['quantity'],
    #             product=record['product'],
    #             order_type= record['order_type'],
    #             price= 0 if record['order_type'].upper() == "MARKET" else record['limit_price']
    #         )


    #         if int(order_id):
    #             print_log(f"Order placed successfully. Order ID: {order_id}")

    #         return order_id
    #     except Exception as e:
    #         print_log(f"Error in place_order: {e}")
    #         return None




    # def get_order_history(self, order_id):
    # 	try:
    # 		order_details = self.kite.order_history(str(order_id))
    # 		last_order = order_details[-1]

    # 		avg_price = last_order['average_price']
    # 		instrument_token = last_order['instrument_token']

    # 		if avg_price == 0:
    # 			ltp = self.get_ltp(instrument_token)

    # 			while ltp == 0:
    # 				tk.sleep(2)
    # 				ltp = self.get_ltp(instrument_token)

    # 			avg_price = ltp   # ✅ only here

    # 		return avg_price

    # 	except Exception as e:
    # 		print_log("Error in getting get_order_history", e)
    # 		return 0


    def cancel_orders(self, order_id):
        try:
            response = self.kite.cancel_order(order_id= order_id, variety= "regular")
            return response
        except Exception as e:
            print_log(f"Error in Cancel Order: {e}")   

    def get_ltp(self, token):
        """ if token not subscribed, subscribe and get ltp """
        ltp = 0
        try:
            ltp = self.ltp_dict[token]
        except:
            self.kws.subscribe([token])
            self.kws.set_mode(self.kws.MODE_FULL, [token])

        return ltp
    


    def start_websocket(self):
        
        ####### WebSocket sample code #######
        # print_log("Assign callbacks next ")
        # Assign the callbacks.
        self.kws.on_connect = self.on_open
        # print_log("Assign callback on_open ")
        self.kws.on_ticks = self.on_data
        # print_log("Assign callback on_data ")
        self.kws.on_close = self.on_close
        # print_log("Assign callback on_close ")
        # print_log("ws init done")
        self.kws.connect(threaded=True)
        # print_log("ws connedction is sent ")
        # self.kws.connect()

    def on_data(self, ws, ticks):
        
        for tick in ticks:
            print_log(tick)
            # print_log("\n")
            token = tick["instrument_token"]
            self.ltp_dict[token] = tick["last_price"]
            try:
                if "depth" in tick:
                    buy_depth = tick["depth"].get("buy", [])
                    sell_depth = tick["depth"].get("sell", [])

                    best_bid = buy_depth[0] if buy_depth else {"price": None, "quantity": None}
                    best_ask = sell_depth[0] if sell_depth else {"price": None, "quantity": None}

                    self.bid_ask_dict[token] = {
                        "bid_price": best_bid["price"],
                        "bid_qty": best_bid["quantity"] / self.freeze_lotsize_dict.get("NIFTY", {}).get("lot_size", 1),
                        "ask_price": best_ask["price"],
                        "ask_qty": best_ask["quantity"] / self.freeze_lotsize_dict.get("NIFTY", {}).get("lot_size", 1),
                    }
                    print_log("ws self.bid_ask_dict : ", self.bid_ask_dict)
            except Exception as e:
                print_log("Error in on_data depth processing:", e)

    def on_open(self, ws, response):
        print_log("next is subscribe ..")
        ws.subscribe([256265]) 
        ws.set_mode(ws.MODE_LTP, [256265])
        print_log("--- WEBSOCKET CONNECTED ---")

    def on_close(self, ws, code, reason):
        print_log(f"WebSocket closed. Code: {code}, Reason: {reason}")
        print_log("Reconnecting in 2s.................")
        tk.sleep(2)
        self.kws.connect(threaded=True)

    def close_connection(self):
        print_log("Reconnecting in 2s.................")
        tk.sleep(2)
        self.kws.connect(threaded=True)

    def get_historical_data(self,instrument_token,from_date,to_date,interval):
        try:
            result = {}

            # Fetch historical data (replace INSTRUMENT_TOKEN with your token)
            response = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            # print_log("Responce -->>  ",response)
            # for candle in response:
            #     time_key = candle['date'].strftime("%H:%M") 
            #     result[time_key] = {k: v for k, v in candle.items() if k != 'date'}

            # self.hist_data = result
            # print_log(self.hist_data)
            # self.RSI_data = {time: values["close"] for time, values in self.hist_data.items()}
            # print_log(self.RSI_data)
            # last_second_key = list(self.hist_data.keys())[-2]
            return response
            # return self.hist_data[-1]
        except Exception as e:
            print_log("Error in getting Nifty data", e)


    