import pandas as pd
import time
from hexer import mHash
import random
from selenium.webdriver.support.ui import Select
from selenium.webdriver import Firefox
from selenium import webdriver
import requests
import os
from tqdm import tqdm

from bs4 import BeautifulSoup
import time

# 記錄開始時間
start_time = time.time()


def string_process(unprocessed_string):
    if "+" in unprocessed_string:
        # 找到第一個"+"號之前的字串
        unprocessed_string = str(unprocessed_string).split('+')[0]

    if "-" in unprocessed_string:
        # 找到第一個"+"號之前的字串
        unprocessed_string = str(unprocessed_string).split('-')[0]

    # 去掉其中的"+"號和","號
    result = unprocessed_string.replace('$', '').replace(',', '').replace('<', '')

    return result

def total_wallet_information_find(soup):
    
    elements = soup.find(class_="HeaderInfo_totalAssetInner__HyrdC HeaderInfo_curveEnable__HVRYq")
    print("elements", elements.text)
    
    #print("elements", string_process(elements.text))
    
    # 搜尋 class name 為 "TokenWallet_detailLink__goYJR" 的元素
    # 找到包含ETH信息的段落
    eth_paragraph = soup.find('div', class_='TokenWallet_tokenInfo__5PsgW')
    #print(eth_paragraph)
    if eth_paragraph is None:
        eth_usd_value = str(0)
        eth_amount = str(0)
    else:
        # 提取USD Value
        eth_usd_value = eth_paragraph.find_next('div', class_='db-table-cell is-right', style='width: 20%;').text.strip()
        
        # 提取ETH的Amount
        eth_amount = eth_paragraph.find_next('div', class_='db-table-cell', style='width: 25%;').find_next_sibling().text
        #print(f'ETH的Amount：{eth_amount}')
    #print(f'ETH的USD價值：{eth_usd_value}')
    return string_process(elements.text), string_process(eth_amount), string_process(eth_usd_value)

def DeFi_Swap_information_find(soup):
    # 找到id為'lido'的元素
    DeFi_Swap_div = soup.find('div', {'id': 'defiswap'})
    if DeFi_Swap_div == None:
        return 0
    else:
        # print("lido_div", lido_div)

        # 從找到的元素中找到包含金額的元素
        amount_element = DeFi_Swap_div.find('div', {'class': 'projectTitle-number'})

        # 提取金額文本
        amount_text = amount_element.text.strip()
    
    print("DeFi_Swap_div", string_process(amount_text))

def lido_information_find(soup):
    # 找到id為'lido'的元素
    lido_div = soup.find('div', {'id': 'lido'})
    if lido_div == None:
        return 0
    else:
        # print("lido_div", lido_div)

        # 從找到的元素中找到包含金額的元素
        amount_element = lido_div.find('div', {'class': 'projectTitle-number'})

        # 提取金額文本
        amount_text = amount_element.text.strip()
        #print("lido", string_process(amount_text))
        return string_process(amount_text)
        

def wallet_information_find(soup):
    # 找到id為'lido'的元素
    wallet_div = soup.find('div', {'id': 'Wallet'})
    #print("wallet_div", wallet_div)
    if wallet_div == None:
        return 0
    else:
        # print("wallet_div", wallet_div)

        # 從找到的元素中找到包含金額的元素
        amount_element = wallet_div.find('div', {'class': 'projectTitle-number'})

        # 提取金額文本
        amount_text = amount_element.text.strip()
        #print(amount_text)
        return string_process(amount_text)
    print("wallet", string_process(amount_text))

def get_web_information(address):
    web = 'https://debank.com/profile/' + str(address)
    driver.get(web)
    driver.maximize_window()
    sleep_time = random.uniform(1, 10)
    time.sleep(sleep_time)
    # 取得目前頁面的 HTML Code
    current_code = driver.page_source
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(current_code, 'html.parser')

    return soup

def check_load(soup, address):
    if soup.find('div', {'id': 'Wallet'}) == None:
        print("Reload web")
        soup = get_web_information(address)
    return soup

def check_address_volume(address):
    #address = "0x964dc6ce8c35d93f9861e498898e76f27f2a882c"
    
    soup = get_web_information(address)
    soup = check_load(soup, address)
    

    wallet_total_value, eth_amount, eth_value = total_wallet_information_find(soup)
    spot_value = wallet_information_find(soup)
    lido_value = lido_information_find(soup)
    defi_swap_value = DeFi_Swap_information_find(soup)

    return address, wallet_total_value, eth_amount, eth_value, spot_value, lido_value, defi_swap_value

def store_to_csv(address_list, wallet_total_value_list, eth_amount_list, eth_value_list, spot_value_list, lido_value_list, defi_swap_value_list):
    # 轉換為 Pandas DataFrame
    today_date = "2024/02/01"
    data = {'Address': address_list, 'Wallet Total Value': wallet_total_value_list, 'Update Time': today_date, 'ETH Amount': eth_amount_list, 'ETH Value': eth_value_list, 'Spot Value': spot_value_list, 'Lido Value': lido_value_list, 'DeFi Swap Value': defi_swap_value_list}
    df = pd.DataFrame(data)
    # 将 'Age' 列转换为整数类型
    df['Wallet Total Value'] = df['Wallet Total Value'].astype(float)
    df_sorted_by_price = df.sort_values(by='Wallet Total Value', ascending=False)
    # 保存為 CSV 文件
    df_sorted_by_price.to_csv('wallet_information_total_20240201.csv', index=False)
    df_sorted_by_price.head(30).to_csv('wallet_information_top30_20240201.csv', index=False)

    del df
    del df_sorted_by_price
    del data
        

#web = 'https://debank.com/profile/0x08d93188c4c439651993f0c6656ed1253238e450'

webdriver.Firefox(executable_path="./geckodriver.exe")
driver = webdriver.Firefox()
 

# 指定txt檔案的路徑
file_path = './solid_wallet_address.txt'  # 請替換成實際的檔案路徑

check_address_number = 0

if os.path.exists('./wallet_information_total_20240201.csv'):
    # 读取CSV文件
    df = pd.read_csv('./wallet_information_total_20240201.csv')

    # 提取 'Address' 列并转换为列表
    wallet_address_list = df['Address'].tolist()

    if len(wallet_address_list) != 0:
        
        # 提取 'Address' 列并转换为列表
        address_list= df['Address'].tolist()
        wallet_total_value_list = df['Wallet Total Value'].tolist()
        eth_amount_list = df['ETH Amount'].tolist()
        eth_value_list = df['ETH Value'].tolist()
        spot_value_list = df['Spot Value'].tolist()
        lido_value_list = df['Lido Value'].tolist()
        defi_swap_value_list = df['DeFi Swap Value'].tolist()

else:
    address_list = []
    wallet_total_value_list = []
    eth_amount_list = []
    eth_value_list = []
    spot_value_list = []
    lido_value_list = []
    defi_swap_value_list = []

# 開啟檔案並讀取內容
with open(file_path, 'r', encoding='utf-8') as file:
    # 逐行讀取並輸出內容
    for line in file:
        if line.strip() in address_list:
            continue
        else:
            result = check_address_volume(line.strip())
            address_list.append(result[0])
            wallet_total_value_list.append(result[1])
            eth_amount_list.append(result[2])
            eth_value_list.append(result[3])
            spot_value_list.append(result[4])
            lido_value_list.append(result[5])
            defi_swap_value_list.append(result[6])
            check_address_number = check_address_number + 1
            #break
            if (check_address_number % 5) == 0:
                store_to_csv(address_list, wallet_total_value_list, eth_amount_list, eth_value_list, spot_value_list, lido_value_list, defi_swap_value_list)
                
        

driver.quit()

store_to_csv(address_list, wallet_total_value_list, eth_amount_list, eth_value_list, spot_value_list, lido_value_list, defi_swap_value_list)

# 記錄結束時間
end_time = time.time()

# 計算經過的時間
elapsed_time = end_time - start_time

print(f"程式執行時間：{elapsed_time} 秒")