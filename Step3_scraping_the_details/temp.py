# Add row

# use loc
import pandas as pd
df = pd.DataFrame({"col1":["row1", "row2"], "col2":["apple", "banana"]})
new_row = ['row3', 'cherry']
df.loc[-1] = new_row
df = df.reset_index(drop=True)

# use concat
new_row = ['row4', 'donut']
cols = ['col1', 'col2']
new_df = pd.DataFrame([new_row], columns=cols)
df = pd.concat([df, new_df])
df = df.reset_index(drop=True)

from datetime import datetime
df.loc[df['col1'] == "row3", ['col2']] = datetime.now().strftime("%Y-%m-%d")

import pandas as pd
df = pd.read_csv("kol_list.csv", index_col=[0])
df['details_updated_time'] = datetime(2020, 1, 1).strftime("%Y-%m-%d")
df.loc[df['ig_id'] == "ngoldenberg", ['details_updated_time']] = datetime.now().strftime("%Y-%m-%d")
df.to_csv("kol_list.csv")

import time
from gcloud import storage
client = storage.Client.from_service_account_json('alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('kol_info.csv')
blob = bucket.blob('kol_info.csv')
blob.upload_from_filename('kol_info.csv')
time.sleep(1)
blob = bucket.blob('kol_list.csv')
blob.upload_from_filename('kol_list.csv')
time.sleep(1)
blob = bucket.blob('kol_post.csv')
blob.upload_from_filename('kol_post.csv')
print("Finished")

import requests as r
from bs4 import BeautifulSoup
h = r.get("https://www.instagram.com/p/CbWeL0fvz05/")
h.text
soup = BeautifulSoup(h, 'html.parser')