import logging
import inspect
from datetime import datetime, timedelta, time 



def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    message_str = '[DM] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    full_message = f'{message_str}'
    print(full_message)
    logging.info(full_message)


class DataManager:

    def __init__(self, broker):
        self.INSTRUMENT_TOKEN = 256265
        self.broker = broker
        self._get_from_date()
        self.to_date = datetime.now()

    def _is_trading_day(self, date: datetime) -> bool:
        if date.weekday() in (5, 6):
            return False
        if date.strftime("%Y-%m-%d") in self.broker.india_holidays:
            return False
        return True
    
    def _fetch(self, interval: str , from_date) -> dict:
        to_date   = self.to_date.date()
        from_date = from_date
        result = {}
        print_log(f"Fetching interval={interval} from={from_date} to={to_date}")

        try:
            raw = self.broker.get_historical_data(
                instrument_token=self.INSTRUMENT_TOKEN,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
            )
            # print_log("raw ----> " , raw)
            result = {item["date"].strftime("%Y-%m-%d %H:%M"): {"close": round(item["close"], 2)} for item in raw }

        except Exception as e:
            print_log(f"Fetch failed for {interval}:", e)
            return {}

        print_log(f"{interval} fetch complete. Candles:", len(result))
        return result

    def _get_from_date(self):
        candidate = datetime.now() - timedelta(days=1)

        count = 0
        last_trading_day = None
        fifth_trading_day = None

        while count < 16:
            if self._is_trading_day(candidate):
                count += 1

                if count == 14 :
                    last_trading_day = candidate

                if count == 14:
                    fifth_trading_day = candidate

            candidate -= timedelta(days=1)

        self.from_date_1hour = fifth_trading_day.strftime("%Y-%m-%d")
        self.from_date_15minute = last_trading_day.strftime("%Y-%m-%d")
        self.from_date_5min = fifth_trading_day.strftime("%Y-%m-%d")
        return (
            last_trading_day.strftime("%Y-%m-%d"),
            fifth_trading_day.strftime("%Y-%m-%d")
        )

    
    def fetch_15min_data(self) -> dict:
        return self._fetch("15minute",self.from_date_15minute)

    def fetch_1hr_data(self) -> dict:
        return self._fetch("hour" , self.from_date_1hour)
    
    def fetch_5min_data(self)->dict:
        return self._fetch("5minute" , self.from_date_5min)

    def fetch_all(self) -> dict:
        print_log("Fetching all timeframes...")
        return {
            # "15min": self.fetch_15min_data(),
            "1hr":   self.fetch_1hr_data(),
        }