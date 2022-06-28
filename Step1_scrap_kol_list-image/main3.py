# Python Script - C -- Scrap IG to final confirm ig follower > 1000
# This python script is to check ig followers > 1000 using IG
# Purpose: final confirm to add to table or drop
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from gcloud import storage
from datetime import datetime
import random

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--no-sandbox')
# options.add_argument('--incognito')
options.add_experimental_option("detach", True)
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
actions = ActionChains(driver=driver)
driver.close()
print("section 0: web driver setting - Finished")

client = storage.Client.from_service_account_json('../Step4_machine_learning/alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('pending_list.csv')
blob.download_to_filename('pending_list.csv')
pending_list = pd.read_csv('pending_list.csv', index_col=[0])
list = pending_list['ig_id'].to_list()
time.sleep(1)
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')
temp_df = pd.read_csv("kol_list.csv", index_col=[0])

def convert_number(x):
    try:
        x = x
        if 'k' in x:
            return int(float(x.replace('k', '')) * 1000)
        elif 'k' in x:
            return int(float(x.replace('K', '')) * 1000)
        elif 'm' in x:
            return int(float(x.replace('m', '')) * 1000000)
        elif 'M' in x:
            return int(float(x.replace('M', '')) * 1000000)
        elif ',' in x:
            return int(float(x.replace(',', '')))
        elif '萬' in x:
            return int(float(x.replace('萬', '')) * 10000)
        elif '千' in x:
            return int(float(x.replace('千', '')) * 1000)
        else:
            return int(x)
    except Exception as e:
        print(e, ' convert_number error')

# -------------- Cookies FOR LOGIN ----------------
with open('cookies_jar2.json') as f:
    cookies = json.load(f)
driver = webdriver.Chrome(options=options, service=s)
driver.get("https://www.instagram.com/accounts/login/?hl=zh-tw")

# YOU NEED TO DELETE THE "sameSite" Value Pair in JSON file
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()

time.sleep(3)

refresh_times = -2
for x in list:
    refresh_times = refresh_times + 1
    print(f"refresh times: {refresh_times} ,over 100 will stop")
    if refresh_times > 100:
        print("the list is over 100 items, we need to scrap it seperately")
        break
    elif x == "instagram":
        pass
    else:
        driver.get("https://www.instagram.com/{}".format(x))
        print(f"go to {x} ig fan page")
        time.sleep(random.randint(1, 2))
        try:
            link1 = "a[href='/{}/followers/']".format(x)
            link2 = link1 + ' > div > span'
            no_of_followers = driver.find_element(By.CSS_SELECTOR, link2).text
            no_of_followers = convert_number(no_of_followers)
            print(f"number of follower: {no_of_followers}")
            if int(no_of_followers) < 1000:
                print(f'{x} is less than 1000 followers - go to next!!!')
                index_pending = pending_list[pending_list['ig_id'] == x].index
                pending_list = pending_list.drop(index_pending)
                pending_list = pending_list.reset_index(drop=True)
                print(f"drop {x} in pending list")
            else:
                new_row = [x, "Check Yet", datetime(2020, 1, 1).strftime("%Y-%m-%d"),
                           datetime(2020, 1, 1).strftime("%Y-%m-%d"), 'yet']
                cols = ['ig_id', 'is_HK', 'updated_following_list_time', 'details_updated_time', 'following_list']
                new_df = pd.DataFrame([new_row], columns=cols)
                temp_df = pd.concat([temp_df, new_df])
                temp_df = temp_df.reset_index(drop=True)
                print(f"{x} appended to kol_list")
                index_pending = pending_list[pending_list['ig_id'] == x].index
                pending_list = pending_list.drop(index_pending)
                pending_list = pending_list.reset_index(drop=True)
                print(f"drop {x} in pending list")
        except:
            print("Something Wrong or it may be private account")
            try:
                index_pending = pending_list[pending_list['ig_id'] == x].index
                pending_list = pending_list.drop(index_pending)
                pending_list = pending_list.reset_index(drop=True)
                print(f"drop {x} in pending list")
            except:
                print(f"append list not exist {x}, may delete before")
print("finished")

# update 'updated_following_list_time' of selected_kol
temp_df.to_csv('kol_list.csv')
pending_list.to_csv('pending_list.csv')
# upload file which file name is ...
blob = bucket.blob('kol_list.csv')
blob.upload_from_filename('kol_list.csv')
# upload file which file name is ...
blob = bucket.blob('pending_list.csv')
blob.upload_from_filename('pending_list.csv')
print("Copying to csv file - finished")