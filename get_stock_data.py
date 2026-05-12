import time
import re
from playwright.sync_api import sync_playwright,Page
import csv
import os
import datetime
# 修改：改用新版支援的導入方式
#from playwright_stealth import stealth

def clean_numeric(text:str)->str:
    """
    底層邏輯：
    1. strip(): 去除前後空白 (類比 Excel TRIM)
    2. replace(',', ''): 移除千分位 (類比 Excel 儲存格格式設定)
    3. re.sub: 若有非數字字元則移除（可選）
    """
    if not text:
        return "0"
    cleaned=text.replace(',','').strip()
    return cleaned if cleaned.replace('.', '', 1).isdigit() else "0"

def get_stock_data(page: Page,stock_id: str):
    print("正在開啟網頁...")
    page.goto(f"https://tw.stock.yahoo.com/quote/{stock_id}.TW", wait_until="domcontentloaded", timeout=60000)
    target_heading=page.locator('[id*="QuoteHeader"] h1')
    target_heading.wait_for(state="visible",timeout=1000)
    stock_name = target_heading.inner_text()
    print(f"--- 成功擷取資料 ---")
    print(f"個股名稱: {stock_name}")
#       print(f"個股名稱: {stock_name_01}")
                # 抓取股價 (使用 Yahoo 的類別特徵)
    raw_price=page.get_by_text("成交",exact=True).locator('+span').filter(has_text=re.compile(r".+")).inner_text()
    price = clean_numeric(raw_price)
    print(f"目前股價: {price}")
    yesterday_close = page.get_by_text("昨收",exact=True).locator('+span').filter(has_text=re.compile(r".+")).inner_text()
    print(f"昨收價: {yesterday_close}")
    high = page.get_by_text("最高",exact=True).locator('+span').filter(has_text=re.compile(r".+")).inner_text()
    print(f"最高股價: {high}")
    low = page.get_by_text("最低",exact=True).locator('+span').filter(has_text=re.compile(r".+")).inner_text()
    print(f"最低股價: {low}")
                #page.pause() # 讓視窗停住，方便你觀察
    date_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')           
    data = [date_time,stock_id,stock_name, price, high, low]
    return data


def save_To_csv(data):
    file_time=datetime.datetime.now().strftime('%Y%m%d')
    file_name=f'{file_time}_stock_data.csv'
    
    file_exists= os.path.isfile(file_name)

    with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['時間','代碼','名稱','股價','最高','最低'])
        writer.writerow(data)

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=False,args=["--star-maximized"])
        context=browser.new_context(offline=False,http_credentials=None)
        page = context.new_page()
        target_stocks = ["2300"]
        target_stocks += [str(i) for i in range(2301,2310)]
                    
        for stock_id in target_stocks:
            start_time = time.perf_counter()
            try:
                data=get_stock_data(page,stock_id)
                if data:
                    save_To_csv(data)
            except Exception as e:
                print(f"{stock_id}執行出錯: {e}")
                continue
            finally:
                end_time = time.perf_counter()
                print(f"自動化耗時: {end_time - start_time:.4f}秒")
                time.sleep(2)
        browser.close()

if __name__ == "__main__":
    run()
