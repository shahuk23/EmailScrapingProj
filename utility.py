from datetime import datetime as datetimenow
import os
import csv
import logging
today_str = datetimenow.now().strftime("%Y-%m-%d")

def getDateAndTimeIn12HrFormat():
    dtLiveDateTime = datetimenow.now()
    dtLivedate = dtLiveDateTime.date().strftime('%d-%m-%Y')
    dtLiveTime12Hr = dtLiveDateTime.strftime("%I:%M %p")

    return dtLivedate,dtLiveTime12Hr


def get_csv_paths():
    folder = "Scapper_stocks_daily"

    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"📁 Created folder: {folder}")

    filename = os.path.join(folder, f"stocks_{today_str}.csv")
    backup_filename = os.path.join(folder, f"stocks_backup_{today_str}.csv")

    return filename, backup_filename


def load_stocks_from_csv():
    filename, _ = get_csv_paths()
    stocks = []
    if os.path.exists(filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row = dict(row)  # Ensure it's a mutable dict
                    row['close'] = float(row['close'])
                    row['per_chg'] = float(row['per_chg'])
                    row['sl'] = float(row['sl'])
                    row['sr'] = int(row['sr'])
                    row['target'] = float(row['target'])
                    row['volume'] = int(row['volume'])
                    stocks.append(row)
                except Exception as e:
                    print(f"⚠️ Skipping row due to error: {e}")
        print(f"[OK] Loaded {len(stocks)} stocks from {filename}")
        logging.info(f"[OK] Loaded {len(stocks)} stocks from {filename}")
    else:
        print(f"ℹ️ No existing stock file found for today ({filename})")
    return stocks

def save_stock_to_csv(stock):
    filename, backup_filename = get_csv_paths()
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=stock.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(stock)

    # Also backup
    with open(backup_filename, mode='a', newline='', encoding='utf-8') as bf:
        writer = csv.DictWriter(bf, fieldnames=stock.keys())
        if not os.path.exists(backup_filename):
            writer.writeheader()