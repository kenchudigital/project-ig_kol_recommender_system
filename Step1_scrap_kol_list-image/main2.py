# Python Script - B -- Scrap Search Engine
# This python script is to check ig followers > 1000 using search engine
# Purpose: decrease to scrap ig to avoid blocking
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from gcloud import storage
from datetime import datetime
from random import randint

client = storage.Client.from_service_account_json('../Step4_machine_learning/alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('pending_list.csv')
blob.download_to_filename('pending_list.csv')
pending_list = pd.read_csv('pending_list.csv', index_col=[0])
time.sleep(1)
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')
temp_df = pd.read_csv("kol_list.csv", index_col=[0])

if pending_list.empty:
    print("dataframe is empty - > stop")
    exit()
else:
    pass

def convert_number(numb):
    try:
        numb = numb
        if 'k' in numb:
            return int(float(numb.replace('k', '')) * 1000)
        elif 'k' in numb:
            return int(float(numb.replace('K', '')) * 1000)
        elif 'm' in numb:
            return int(float(numb.replace('m', '')) * 1000000)
        elif 'M' in numb:
            return int(float(numb.replace('M', '')) * 1000000)
        elif ',' in numb:
            return int(float(numb.replace(',', '')))
        elif '萬' in numb:
            return int(float(numb.replace('萬', '')) * 10000)
        elif '千' in numb:
            return int(float(numb.replace('千', '')) * 1000)
        else:
            return int(numb)
    except:
        print(f' convert_number error when convert {numb}')

# section 0: web driver setting
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--no-sandbox')
options.add_experimental_option("detach", True)
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
actions = ActionChains(driver=driver)
print("section 0: web driver setting - Finished")

# Section A duckduckgo loop
print("go to duck duck go loop")
list = pending_list['ig_id'].to_list()
count_number = len(list)

for ig_id in list:
    print(f"there remains {count_number} items in pending list ")
    count_number = count_number - 1
    time.sleep(randint(0,1))
    url_a = "https://duckduckgo.com/?q=instagram.com/" + ig_id
    driver.get(url_a)
    try:
        basic_details = driver.find_element(By.CSS_SELECTOR, "div[class=\"result__snippet js-result-snippet\"]").text
        print("get element success")
    except:
        try:
            basic_details = driver.find_element(By.CSS_SELECTOR, "div[class=\"OgdwYG6KE2qthn9XQWFC\" > span]").text
            print("try to other element")
        except:
            print("element not found")
            basic_details = ["abcdefg hijk"]

    basic_details = str(basic_details).split(" ")
    print(basic_details)
    if basic_details[-1].count(ig_id) == 1 and basic_details[1] == "Followers,":
        print("scraping is correct")
        no_of_followers = convert_number(basic_details[0])
        # no_of_following = convert_number(basic_details[2])
        # no_of_posts = convert_number(basic_details[5])
        print(f"{ig_id} has {no_of_followers}")
        if no_of_followers > 999:
            print(f'{ig_id} is over 1000 followers, it has {no_of_followers} - continue!!!')
            new_row = [ig_id, "Check Yet", datetime(2020, 1, 1).strftime("%Y-%m-%d"), datetime(2020, 1, 1).strftime("%Y-%m-%d"), 'yet']
            cols = ['ig_id', 'is_HK', 'updated_following_list_time' ,'details_updated_time', 'following_list']
            new_df = pd.DataFrame([new_row], columns=cols)
            temp_df = pd.concat([temp_df, new_df])
            temp_df = temp_df.reset_index(drop=True)
            print(f"{ig_id} appended to kol_list")
            index_pending = pending_list[pending_list['ig_id'] == ig_id].index
            pending_list = pending_list.drop(index_pending)
            pending_list = pending_list.reset_index(drop=True)
            print(f"drop {ig_id} in pending list")
        else:
            print("no of follower < 1000, drop in pending list")
            index_pending = pending_list[pending_list['ig_id'] == ig_id].index
            pending_list = pending_list.drop(index_pending)
            pending_list = pending_list.reset_index(drop=True)
            print(f"drop {ig_id} in pending list")
    else:
        print("scraping is wrong, pass")
        pass
print("the loop is finished !!!")

temp_df.to_csv('kol_list.csv')
pending_list.to_csv('pending_list.csv')
# upload file which file name is ...
blob = bucket.blob('kol_list.csv')
blob.upload_from_filename('kol_list.csv')
# upload file which file name is ...
blob = bucket.blob('pending_list.csv')
blob.upload_from_filename('pending_list.csv')
# also can use bing & yahoo
# url_b = "https://www2.bing.com/search?q=" + ig_id
# url_c = "https://hk.search.yahoo.com/search?p=" + ig_id
print("to_csv & uploaded the csv files to GCS finished")