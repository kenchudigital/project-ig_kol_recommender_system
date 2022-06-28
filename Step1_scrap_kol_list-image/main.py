# Python Script - A -- Scrap IG KOL following list
# This python script is to scrap ig
# Purpose: find which account that HK KOL followed, it should also be a KOL and popular in HK
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
driver.close()
print("section 0: web driver setting - Finished")

# -------------- Cookies FOR LOGIN ----------------
with open('cookies_jar2.json') as f:
    cookies = json.load(f)
driver = webdriver.Chrome(options=options, service=s)
driver.get("https://www.instagram.com/accounts/login/?hl=zh-tw")
# YOU NEED TO DELETE THE "sameSite" Value Pair in JSON file
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()

# -------------- ANTI PREVENT BOT  --------------
time.sleep(5)
# close_pop = WebDriverWait(driver, 5).until(
#     EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), \'蝔滚���滩牧\')]'))
# )
# close_pop.click()

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
time.sleep(5)
# gcloud setting
client = storage.Client.from_service_account_json('../Step4_machine_learning/alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')
time.sleep(3)
blob = bucket.blob('pending_list.csv')
blob.download_to_filename('pending_list.csv')

# randomly select kol_list
temp_df = pd.read_csv('kol_list.csv', index_col=[0])
temp_df = temp_df[temp_df['updated_following_list_time'] == min(temp_df['updated_following_list_time'])]
temp_df = temp_df[temp_df['is_HK'] == "Hong Kong"]
temp_df = temp_df.reset_index()
selected_kol = temp_df['ig_id'].sample().item()
driver.get("https://www.instagram.com/{}".format(selected_kol))
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

# section 4b: Click the pop up once time
time.sleep(1)
go_pop = driver.find_element(By.CSS_SELECTOR, "div[class='PZuss']")
go_pop.click()
print("section 4: Define the web element * other setup - finished")

# section 5: Scrolling Down
time.sleep(3)
pop_up_window = WebDriverWait(
    driver, 2).until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@class='isgrP']")))
print(f"Starting to scroll... it needs about {(no_of_following//4 + 20)} seconds")

try:
    for x in range(no_of_following//4 + 20):
        driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', pop_up_window)
        time.sleep(0.85)
        print(x)
except Exception as e:
    print(e, 'Instagram Scroll Down to bottom')
print("section 5: Scrolling Down - finished")

# section 6: Copying
list_for_followed = []
y = 0
for y in range(no_of_following):
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
driver.close()

# section 7: Append the following list to table

index_no = temp_df.loc[temp_df['ig_id'] == selected_kol].index
temp_df.loc[index_no, 'following_list'] = str(list_for_followed)
print("append the following list to the table")
print(temp_df[temp_df['ig_id'] == selected_kol])

# section 8: Is it over 1000 followers and append

# change the file name
blob = bucket.blob('kol_list.csv')
# add the non duplicate ig_id to dataframe
print("starting to check non duplicate")
temp_a = no_of_following
temp_c = 0
for x in list_for_followed:
    if x in set(temp_df['ig_id']) == True:
        list_for_followed = list_for_followed.remove(x)
        print(f"{x} is duplicate")
        print(f"remain {temp_a} items")
        temp_a = temp_a - 1
    else:
        temp_c = temp_c + 1
        temp_a = temp_a - 1
        print(f"{x} is no.{temp_c} ig_id that no duplicates")

pending_list = pd.read_csv("pending_list.csv", index_col=[0])
no_of_pending = pending_list['ig_id'].count()
print(f"the number of pending is: {no_of_pending} now")
temp_d = no_of_pending
for x in pending_list:
    if x in set(pending_list['ig_id']) == True:
        list_for_followed = list_for_followed.remove(x)
        print(f"{x} has been already in pending list")
        temp_c = temp_c - 1
    else:
        pass
print(f"There is {temp_c} non duplicate following ig_id")

temp_df.loc[temp_df['ig_id'] == selected_kol, ['updated_following_list_time']] = datetime.now().strftime("%Y-%m-%d")
print("updated following list time is update to today")

temp_b = 0
for x in list_for_followed:
    new_row = [x]
    cols = ['ig_id']
    new_df = pd.DataFrame([new_row], columns=cols)
    pending_list = pd.concat([pending_list, new_df])
    pending_list = pending_list.reset_index(drop=True)
    print(f"{x} appended")
    temp_b = temp_b + 1

print(f"There is {temp_b} ig_id added in pending list" )
pending_list.to_csv('pending_list.csv')
blob = bucket.blob('pending_list.csv')
blob.upload_from_filename('pending_list.csv')
time.sleep(20)
