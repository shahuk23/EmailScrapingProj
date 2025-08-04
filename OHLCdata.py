import yfinance as yf
import pandas as pd
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
stockTobuy = []

def add_stock_to_buy(nsecode, close):
    stockList = {
        'nsecode': nsecode,
        'name': '',         # You can fill this later if needed
        'bsecode': '',      # Optional if you have the mapping
        'per_chg': 0,
        'close': close,
        'volume': 0         # Default to 0 if unknown
    }
    stockTobuy.append(stockList)
def fetch_ohlc_close_by_email_time(stock_name, email_date, email_time):
    try:
        # Combine date and time into a datetime object (IST timezone)
        ist_dt = datetime.combine(email_date, email_time)

        # Convert IST to UTC for yfinance query
        utc_dt = ist_dt - timedelta(hours=5, minutes=30)

        # Fetch intraday data for the date (full day)
        start = utc_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        ticker = yf.Ticker(stock_name + ".NS")
        df = ticker.history(interval="5m", start=start, end=end)

        if df.empty:
            print(f"No data found for {stock_name} on {email_date}")
            return None

        ist = ZoneInfo("Asia/Kolkata")
        rounded_time = datetime.combine(email_date, email_time)
        rounded_time = rounded_time.replace(minute=(rounded_time.minute // 5) * 5, second=0, microsecond=0)
        rounded_time = rounded_time.replace(tzinfo=ist)

        # Make sure df.index is also in IST
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC").tz_convert(ist)
        else:
            df.index = df.index.tz_convert(ist)

        # Now you can safely look up
        if rounded_time in df.index:
            ohlc_row = df.loc[rounded_time]
            print(f"{stock_name} | {rounded_time.strftime('%Y-%m-%d %I:%M %p')} IST | Close: {ohlc_row['Close']:.2f}")
            add_stock_to_buy(stock_name,str(round(ohlc_row['Close'])))
        else:
            print(f"No OHLC data for {stock_name} at {rounded_time.strftime('%Y-%m-%d %I:%M %p')} IST")



        return stockTobuy

    except Exception as e:
        print(f"Error fetching OHLC for {stock_name}: {e}")
        return None