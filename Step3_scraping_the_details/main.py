from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import pandas as pd
import os
from datetime import datetime
import requests
from webdriver_manager.chrome import ChromeDriverManager
import re
from random import randint
from gcloud import storage
from selenium.webdriver.common.keys import Keys

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

# blob download kol_info.csv, kol_list.csv, kol_post.csv

client = storage.Client.from_service_account_json('alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('kol_info.csv')
blob.download_to_filename('kol_info.csv')
time.sleep(1)
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')
time.sleep(1)
blob = bucket.blob('kol_post.csv')
blob.download_to_filename('kol_post.csv')

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

# -------------- Cookies FOR LOGIN ----------------
driver = webdriver.Chrome(options=options, service=s)
driver.get("https://www.instagram.com/accounts/login/?hl=zh-tw")
# YOU NEED TO DELETE THE "sameSite" Value Pair in JSON file
with open ('cookies_jar3.json') as f:
    cookies = json.load(f)
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()

for gogogo in range(300):
    print(f"scrape no.{gogogo + 1} ig account")
    try:
        # selecting ig_id
        time.sleep(randint(1, 3))
        temp_kol_list = pd.read_csv('kol_list.csv', index_col=[0])
        # Only Location is Hong Kong
        temp_kol_list = temp_kol_list[temp_kol_list['is_HK'] == "Hong Kong"]
        temp_kol_list = temp_kol_list[temp_kol_list['details_updated_time'] == min(temp_kol_list['details_updated_time'])]
        temp_kol_list = temp_kol_list.reset_index()
        ig_id = temp_kol_list['ig_id'].sample().item()
        print(f"select {ig_id}")

        # section 1: ig_id
        # ig_id = "hkfoodtalk"
        driver.get("https://www.instagram.com/{}".format(ig_id))
        time.sleep(randint(0, 1))

        # check private account
        try:
            check_private = driver.find_element(By.CSS_SELECTOR, "h2[class=\"rkEop\"]").text
            if check_private == "此帳號為私人帳號":
                print("this account is private account, need to be dropped")
                temp_df = pd.read_csv("kol_list.csv", index_col=[0])
                index_pending = temp_df[temp_df['ig_id'] == ig_id].index
                temp_df = temp_df.drop(index_pending)
                temp_df = temp_df.reset_index(drop=True)
                temp_df = temp_df.reset_index(drop=True)
                print("dropped")
                temp_df.to_csv("kol_list.csv")
                blob = bucket.blob('kol_list.csv')
                blob.upload_from_filename('kol_list.csv')
                print("uploaded to GCS")
            else:
                pass
        except:
            print("This account is public!")

        # section 2: name
        description = driver.find_element(By.CSS_SELECTOR, "div[class=\"QGPIr\"]").text.split("\n")
        name = description[0]
        # section 3: ig_description
        ig_description = description[1:]
        # section 4: no_of_post
        no_of_post = driver.find_element(By.CSS_SELECTOR, "body > div[id=\"react-root\"] > section > main > div > header > section > ul > "
                                                              "li > div > span").text
        no_of_post = convert_number(no_of_post)
        # section 5: no_of_follower
        no_of_follower = driver.find_element(By.CSS_SELECTOR, "a[href=\"/"+ig_id+"/followers/\"] > div > span").text
        no_of_follower = convert_number(no_of_follower)
        # section 6: no_of_following
        no_of_following = driver.find_element(By.CSS_SELECTOR, "a[href=\"/"+ig_id+"/following/\"] > div > span").text
        no_of_following = convert_number(no_of_following)
        # section 7: profile_image
        profile_image_link = driver.find_element(By.CSS_SELECTOR, "img[class=\"_6q-tv\"]").get_attribute('src')
        r = requests.get(profile_image_link)
        name_of_pic = f"{ig_id}_profile.png"
        with open(name_of_pic, 'wb') as f:
            f.write(r.content)
        profile_img = "scrap_web_details_image/"+name_of_pic
        os.replace(name_of_pic, profile_img)
        # basic information is completed

        ###############################################

        df_post = pd.read_csv("kol_post.csv", index_col=[0])
        # section 8: scrap post
        count_num = 0

        # check the last one post, prevent duplication
        last_post_year = datetime.now().year
        the_last_day = df_post[df_post['ig_id'] == ig_id]['post_date'].max()
        last_post_alt = df_post[df_post['post_date'] == the_last_day]['post_alt']
        last_post_alt = last_post_alt.tolist()
        # x = 2
        for x in range(no_of_post):

            if last_post_year < datetime.now().year:
                break

            elif count_num > 25:
                # only scrap 25 post
                break
            else:
                count_num = count_num + 1
                print(f"this is {count_num}th times to run post")

                y = x + 1
                if y > 3:
                    y = y % 3
                if y == 0:
                    y = y + 3
                y = str(y)
                z = int((x + 3)/3)
                z = str(z)
                print(f"x is {x}")
                print(f"y is {y}")
                print(f"z is {z}")
                print(f"第{x+1}個，位置是第{z}行，第{y}個。")
                # post_alt
                print("# post_alt")
                post_alt_element = driver.find_element(By.CSS_SELECTOR,
                                               "div[class=\" _2z6nI\"] > article > div > div > div:nth-child(" + z + ") > div:nth-child(" + y + ") > a > div > div > img")
                                                                                                  # z 是第幾行                         y 是第幾個
                # post date
                print("# post date")
                post_alt = post_alt_element.get_attribute("alt")
                post_alt = str(post_alt)
                print(f"post_alt is {post_alt}")
                if post_alt in last_post_alt:
                    break
                else:
                    pass
                try:
                    post_date = re.search(r"on.*2022|2021", post_alt).group()
                    post_date = post_date.split(" ")
                    last_post_year = int(post_date[3])
                    post_date = post_date[1] + ' ' + post_date[2].replace(",", "") + ' ' + post_date[3]
                    post_date = datetime.strptime(post_date, '%B %d %Y').strftime('%Y-%m-%d')
                    post_type = "image"
                except:
                    print("no date in post_alt, we set post_date = 0 for now")
                    post_date = 0

                # hover
                time.sleep(randint(0, 1))
                action = ActionChains(driver=driver)
                time.sleep(1)
                print('try to hover')
                try:
                    hover_a = action.move_to_element(post_alt_element)
                    hover_a.perform()
                except:
                    try:
                        print("try_hover again")
                        time.sleep(1)
                        hover_a = action.move_to_element(post_alt_element)
                        hover_a.perform()
                    except:
                        print("refresh and try hover again")
                        driver.refresh()
                        hover_a = action.move_to_element(post_alt_element)
                        hover_a.perform()

                try:
                    print("try to getting the hover data")
                    hover = driver.find_element(By.CSS_SELECTOR, "div[class=\" _2z6nI\"] > article > div > div > div:nth-child(" + z + ") > div:nth-child(" + y + ") > a > div[class=\"qn-0x\"]").text
                    #post_like_& comment
                    hover = hover.split("\n")
                    post_like = convert_number(hover[0])
                    post_comment = convert_number(hover[1])
                except:
                    post_like = 0
                    post_comment = 0
                    print("post and comment are 0, represent no show")
                    continue

                # click to post
                print('try to find the post_loc and click')
                try:
                    post_loc = driver.find_element(By.CSS_SELECTOR,
                                                   "div[class=\" _2z6nI\"] > article > div > div > div:nth-child(" + z + ") > div:nth-child(" + y + ") > a")
                    post_loc.click()
                except:
                    print('post_loc cannot found or cannnot click, try again')
                    try:
                        time.sleep(0.5)
                        post_loc = driver.find_element(By.CSS_SELECTOR,
                                                       "div[class=\" _2z6nI\"] > article > div > div > div:nth-child(" + z + ") > div:nth-child(" + y + ") > a")
                        time.sleep(0.5)
                        post_loc.click()
                    except:
                        print("try to refresh and find the post_loc again and try to click to")
                        driver.refresh()
                        try:
                            time.sleep(1)
                            post_loc = driver.find_element(By.CSS_SELECTOR,
                                                           "div[class=\" _2z6nI\"] > article > div > div > div:nth-child(" + z + ") > div:nth-child(" + y + ") > a")
                            time.sleep(0.5)
                            post_loc.click()
                        except:
                            print('I don\'t know what wrong in finding & clicking post_loc')

                # content
                time.sleep(randint(4, 5))
                try:
                    print("try to find the content")
                    content = driver.find_element(By.CSS_SELECTOR, "div[class=\"MOdxS \"] > span").text
                except:
                    time.sleep(5)
                    try:
                        print("try to find the content again")
                        content = driver.find_element(By.CSS_SELECTOR, "div[class=\"MOdxS \"] > span").text
                    except:
                        print("refresh then find the content again")
                        driver.refresh()
                        time.sleep(5)
                        try:
                            content = driver.find_element(By.CSS_SELECTOR, "div[class=\"MOdxS \"] > span").text
                            print("success to find the content")
                        except:
                            print("something wrong about ModxS class")
                            content = ""
                            print("cannot find so provide empty content")

                # post type
                print("# post type")
                try:
                    post_type_element = driver.find_element(By.CSS_SELECTOR, "section[class=\"EDfFK ygqzn \"] > div").text
                    if post_type_element[-1] == "讚":
                        post_type = "img"
                    elif post_type_element[-1] == "看":
                        post_type = "video"
                    else:
                        post_type = "unknown"
                except:
                    print("something wrong about scraping 看 or 讚")
                    print("try to get the post_type later")
                    post_type = "unknown"

                # post date ###################################
                print("# post date ###################################")
                try:
                    if post_date == 0:
                        print("post date = 0")
                        post_date_element = driver.find_element(By.CSS_SELECTOR, "time[class=\"_1o9PC\"]").get_attribute("datetime")
                        post_date_element = post_date_element.split("T")
                        post_date = datetime.strptime(post_date_element[0], '%Y-%m-%d').strftime('%Y-%m-%d')
                    else:
                        pass
                except:
                    print("cannot find post date from time element")
                    pass

                print("# close the post pop u")
                # close the post pop u
                time.sleep(randint(1, 2))
                try:
                    close_pop = driver.find_element(By.CSS_SELECTOR, "svg[aria-label=\"關閉\"]")
                    close_pop.click()
                    print("get post_date")
                    time.sleep(randint(2,3))
                except:
                    try:
                        time.sleep(randint(1, 2))
                    except:
                        driver.back()
                        time.sleep(randint(1, 2))
                        print("use the last method to go back to main page")

                # try to get post_type
                print("# try to get post_type")
                if post_type == "unknown":
                    try:
                        post_type2 = driver.find_element(By.CSS_SELECTOR,
                                                       "div[class=\" _2z6nI\"] > article > div > div > div:nth-child(" + z + ") > div:nth-child(" + y + ") > a > div > div > img").get_attribute("decoding")
                    except:
                        print("cannot find the post_type according to attribute decoding")
                        post_type = "img"
                        post_type2 = "unknown"

                    if post_type2 == "auto":
                        post_type = "video"
                        print("The post type is video")
                    else:
                        post_type = "unknown"

                if post_type == "unknown":
                    print("check if post_type finally is unknown")
                    if "Photo shared by" or "Photo by" in post_alt:
                        post_type = "img"
                    else:
                        post_type = "unknown"
                else:
                    pass

                if int(datetime.strptime(post_date, '%Y-%m-%d').year) < 2022:
                    print("this post is < 2022, finish scrapping")
                    break
                else:
                    new_row = [ig_id, post_date, post_alt, post_type, post_like, post_comment, content]
                    df_post.loc[-1] = new_row
                    df_post = df_post.reset_index(drop=True)
        # try to get post_type
        # add before
        df_basic = pd.read_csv("kol_info.csv", index_col=[0])
        if ig_id in df_basic['ig_id'][0]:
            print("has been already added before, update now")
            new_row = [ig_id, name, ig_description, no_of_post, no_of_follower, no_of_following, profile_img]
            index_row = df_basic[df_basic['ig_id'] == ig_id].index
            df_basic.loc[index_row] = new_row
            print(df_basic[df_basic['ig_id'] == ig_id])
            print("it should be replace the old one")
        # add new
        else:
            print("add new")
            new_row = [ig_id, name, ig_description, no_of_post, no_of_follower, no_of_following, profile_img]
            df_basic.loc[-1] = new_row
            df_basic = df_basic.reset_index(drop=True)
            df_basic.to_csv("kol_info.csv")
            print("upload the basic information")

        temp_df = pd.read_csv("kol_list.csv", index_col=[0])
        temp_df.loc[temp_df['ig_id'] == ig_id, ['details_updated_time']] = datetime.now().strftime("%Y-%m-%d")
        temp_df.to_csv("kol_list.csv")
        print("updated details updated time is update to today")
        print('kol_list is updated to csv file')

        df_post.to_csv("kol_post.csv")
        print("kol_post is updated to csv file")

        # Finally upload to GCS
        blob = bucket.blob('kol_info.csv')
        blob.upload_from_filename('kol_info.csv')
        time.sleep(1)
        blob = bucket.blob('kol_list.csv')
        blob.upload_from_filename('kol_list.csv')
        time.sleep(1)
        blob = bucket.blob('kol_post.csv')
        blob.upload_from_filename('kol_post.csv')
        time.sleep(1)
        image_name_ = '/scrap_web_details_image/' + ig_id + '_profile.png'
        blob = bucket.blob(image_name_)
        blob.upload_from_filename(image_name_)
        print("Finished")
        time.sleep(randint(5, 10))
    except:
        print("I don't know what wrong")
        driver.refresh()
        print("refresh")
        time.sleep(randint(5, 10))

driver.close()




