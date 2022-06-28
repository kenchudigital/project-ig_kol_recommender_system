# Python Script - * -- Scrap IG KOL following list according to the kol_info
# This python script is to scrap ig
# Purpose: find existed KOL list's following list but will not append kol_list
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from gcloud import storage
from datetime import datetime
from random import randint
import random

# section 0: web driver setting
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-popup-blocking")
options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"')
options.add_experimental_option("detach", True)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("disable-infobars")
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
actions = ActionChains(driver=driver)
driver.close()
print("section 0: web driver setting - Finished")

n = 5
# unblock:

cookies_name = "cookies_jar" + str(n) + ".json"
print(cookies_name)
# -------------- Cookies FOR LOGIN ----------------
with open(cookies_name) as f:
    cookies = json.load(f)
driver = webdriver.Chrome(options=options, service=s)
driver.get("https://www.instagram.com/accounts/login/?hl=zh-tw")
# YOU NEED TO DELETE THE "sameSite" Value Pair in JSON file
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()

# -------------- ANTI PREVENT BOT  --------------
time.sleep(1)
try:
    close_pop = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), \'蝔滚���滩牧\')]'))
    )
    close_pop.click()
except:
    pass

# -------------- Login first time --------------
try:
    driver.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys('test_for_code2', Keys.TAB, 'kenchu456', Keys.ENTER)
except Exception as e:
    print(e, 'may already login')

# --------------- Other Function ---------------
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

print("section 1: Go to the webpage - Finished")
# section 2: go to the fan page which selected
# ------------- GET THE Name OF KOL -------------
time.sleep(0.5)
# gcloud setting
client = storage.Client.from_service_account_json('../Step4_machine_learning/alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')
time.sleep(1)
blob = bucket.blob('kol_info.csv')
blob.download_to_filename('kol_info.csv')
# select ig_id from kol_list which kol_info.csv list)

# ****************** need to check ****************

info_df = pd.read_csv('kol_info.csv', index_col=[0])
temp_df = pd.read_csv('kol_list.csv', index_col=[0])

list = info_df['ig_id'].to_list()
temp_df2 = temp_df[temp_df['ig_id'].isin(list)]
temp_df2 = temp_df2[temp_df2['updated_following_list_time'] == min(temp_df2['updated_following_list_time'])]
temp_list = temp_df2['ig_id'].to_list()

count = 0
random.shuffle(temp_list)
for selected_kol in temp_list:
    url = "https://www.instagram.com/"+ selected_kol
    driver.get(url)
    print(f"section 2: Go to {selected_kol} fan page - Finished")
    try:
        time.sleep(3)
        link1 = "a[href='/{}/following/']".format(selected_kol)
        elem_following = driver.find_element(By.CSS_SELECTOR, link1)
    except:
        driver.get("https://www.instagram.com/")
        search_bar = driver.find_element(By.CSS_SELECTOR, "input[placeholder=\"搜尋\"]")
        search_bar.send_keys(selected_kol).sendKeys(Keys.ENTER)
        try:
            kol = "/" + selected_kol + "/"
            kol_in_search = driver.find_element(By.CSS_SELECTOR, "a[href=\"" + kol + "\"]")
            kol_in_search.click()
        except:
            print("something wrong")

# section 3: copy the target following list
    time.sleep(3)
    link1 = "a[href='/{}/following/']".format(selected_kol)
    elem_following = driver.find_element(By.CSS_SELECTOR, link1)
    elem_following.click()
    print("section 3: copy the target following list - finished")

# section 4a: Define the web element
    time.sleep(1)
    link2 = link1 + ' > div > span'
    no_of_following = driver.find_element(By.CSS_SELECTOR, link2).text
    no_of_following = convert_number(no_of_following)
    print(f"There is {no_of_following} items")
    if no_of_following > 1800:
        no_of_following = 1800
    else:
        pass

# section 4b: Click the pop up once time
    try:
        time.sleep(1)
        go_pop = driver.find_element(By.CSS_SELECTOR, "div[class='PZuss']")
        go_pop.click()
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
        go_pop.click()
        print("section 4: Define the web element * other setup - finished")
    except:
        time.sleep(2)
        try:
            go_pop = driver.find_element(By.CSS_SELECTOR, "div[class='PZuss']")
            go_pop.click()
        except:
            print("section4 something wrong")

# section 5: Scrolling Down
    time.sleep(3)

    print("try to click pop up again")
    pop_up_window = WebDriverWait(
        driver, 2).until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@class='isgrP']")))

    print(f"Starting to scroll... it needs about {(no_of_following//5 + 5)} seconds")

    try:
        for x in range(int(no_of_following//5 + 5)):
            driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', pop_up_window)
            time.sleep(1)
            print(x)
    except Exception as e:
        print(e, 'Instagram Scroll Down to bottom')
    print("section 5: Scrolling Down - finished")

# section 6: Copying
    list_for_followed = []
    y = 0
    for y in range(no_of_following):
        # limit max 2000 following people
        if y > 1800:
            print(f'{y}th item is founded, max is 1800 items')
            break
        else:
            pass
        try:
            list_of_element = "div[class=\'PZuss\'] > li:nth-child(" + str((y+1)) + ")"
            a = driver.find_element(By.CSS_SELECTOR, list_of_element).text.split()[:1]
            print(f"a = {a}")
            list_for_followed.append(a[0])
            print(f"y = {y}")
            # print(list_for_followed)
        except Exception as e:
            print(e, f'{y}th item is unfound')
    print(f"There are {len(list_for_followed)} items")
    print("section 6: Copying - finished")

# section 7: Append the following list to table

    index_no = temp_df.loc[temp_df['ig_id'] == selected_kol].index
    temp_df.loc[index_no, 'following_list'] = str(list_for_followed)
    print("append the following list to the table")
    print(temp_df[temp_df['ig_id'] == selected_kol])

# section 8: upload to GCS

# change the file name
    temp_df.loc[temp_df['ig_id'] == selected_kol, ['updated_following_list_time']] = datetime.now().strftime("%Y-%m-%d")
    temp_df.to_csv('kol_list.csv')
    print("updated following list time is update to today")
    time.sleep(randint(1, 5))
    blob = bucket.blob('kol_list.csv')
    blob.upload_from_filename('kol_list.csv')
    print("files uploaded")
    count = count + 1
    print(f"count is {count}, count > 3 will break")
    time.sleep(randint(20, 40))
    if count > 3:
        driver.close()
        time.sleep(1)
        break
    else:
        continue

