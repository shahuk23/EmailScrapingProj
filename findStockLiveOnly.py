import NotificationEmail
import applicationStartupMail
import os
import datetime as datetime
from datetime import datetime as datetimenow, timedelta
import logging
import sys
import progressbar
import time
import utility


testOffTime = True
isEmailRequired = True
isMarketCloseCheckRequired = True
isDevOrProdEnvironment = 'DEV'

# Step 1: Get today's date string (e.g., 2025-06-16)
today_str = datetimenow.now().strftime("%Y-%m-%d")

# Step 2: Create the log filename
log_filename = f"console_log_{today_str}.txt"

# Step 3: Ensure the directory exists (optional)
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, log_filename)


# Create and configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a'),  # 'a' ensures appending if file exists
        logging.StreamHandler(sys.stdout)
    ]
)

maintain_unique_stocks = []
maintain_unique_stocksList_for_email = []
def timeSleepWithBarUpdate(sleep):
    with open(os.devnull, 'w') as f:  # Null output stream
        bar = progressbar.ProgressBar(maxval=sleep, fd=f)  # Redirect output
        bar.start()
        i = 0
        while i < sleep:
            i += 1
            bar.update(i)
            time.sleep(0.5)
        bar.finish()

def checkMarketOffTime():
    utc_now = datetimenow.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)

    # Check if time is 3:30 PM or later
    if ist_now.hour > 15 or (ist_now.hour == 15 and ist_now.minute >= 30):
        logging.info(f"Time is 3:30 PM IST or later. Quitting application.")
        print("Time is 3:30 PM IST or later. Quitting application.")
        if maintain_unique_stocks:
            NotificationEmail.sendEmailAtEOD(maintain_unique_stocks)

        quit()  # or use sys.exit() for clarity
    #else:
    #print("Continue running... current IST time is", ist_now.strftime("%H:%M:%S"))

def main():
    logging.info(f"********* Welcome to SK Trading App *********")
    logging.info(f"********* prop. Shahu Kshirsagar *********\n")
    print("********* Welcome to SK Trading App *********")
    print("********* prop. Shahu Kshirsagar *********\n")



def get_target_sl(ltp, target_per, sl_per):
    ltp = float(ltp)
    target = round(ltp * (1 + target_per / 100), 2)
    sl = round(ltp * (1 - sl_per / 100), 2)
    return target, sl

def get_target_sl_new(ltp):
    ltp = float(ltp)

    if 0 <= ltp <= 1000:
        target_per = 3
        sl_per = 2
    elif 1001 <= ltp <= 2000:
        target_per = sl_per = 2
    elif ltp >= 2001:
        target_per = 1
        sl_per = 3
    else:
        raise ValueError("Invalid LTP: must be >= 0")

    target = round(ltp * (1 + target_per / 100), 2)
    sl = round(ltp * (1 - sl_per / 100), 2)
    return target, sl


def process_buy_signals(stocks_list, isEmailRequired, maintain_unique_stocks, maintain_unique_stocksList_for_email, source):
    email_body_lines = []
    stockTriggerDate, stockTriggerTime = utility.getDateAndTimeIn12HrFormat()
    for stock in stocks_list:
        if stock:  # Skip if None or empty dict
            nsecode = ''
            if isinstance(stock, dict):
                nsecode = str(stock.get('nsecode', 'N/A'))  # safe access with default
            elif isinstance(stock, str):
                nsecode = stock  # assume stock itself is the nsecode

            logging.info(f"Buy signal detected for {nsecode} on {stockTriggerDate} {stockTriggerTime}")
            stock['date'] = stockTriggerDate
            stock['time'] = stockTriggerTime
            target, sl = get_target_sl_new(stock['close'])  # or get_target_sl(stock['close'], 3, 2)
            stock['target'] = target
            stock['sl'] = sl

            maintain_unique_stocks.append(stock)
            utility.save_stock_to_csv(stock)

            if isEmailRequired:
                if nsecode in maintain_unique_stocksList_for_email:
                    logging.info(f"Email already sent for {nsecode}")
                    print(f"Email already sent for {nsecode}")
                else:
                    maintain_unique_stocksList_for_email.append(nsecode)
                    #target, sl = get_target_sl_new(stock['close'])  # or get_target_sl(stock['close'], 3, 2)
                    email_body_lines.append({
                        "nsecode": str(stock['nsecode']),
                        "close": str(stock['close']),
                        "target": target,
                        "sl": sl
                    })
        else:
            logging.info("Finding Stock For Trade...")
            print(maintain_unique_stocks)

    # Send batch email if needed
    if isEmailRequired and email_body_lines:
        NotificationEmail.sendEmailAlert(email_body_lines, stockTriggerDate, stockTriggerTime, source)
        #NotificationEmail.sendEmail("shahuk23@gmail.com", "Stock Buy Signal Report", email_html, is_html=True)


def get_stock_by_nsecode(nsecode, stock_list):
    matches = []
    for stock in stock_list:
        if stock.get('nsecode') in nsecode:
            matches.append(stock)
    return matches


def process_buy_signals_from_email_scrap(stockTobuy):
    process_buy_signals(stockTobuy,isEmailRequired, maintain_unique_stocks, maintain_unique_stocksList_for_email, "SCRP")

# Run main only if this file is executed directly
#if __name__ == "__main__":
 #   main()