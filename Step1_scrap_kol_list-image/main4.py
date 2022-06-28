# 手動處理

import pandas as pd
from gcloud import storage
from datetime import datetime
client = storage.Client.from_service_account_json('../Step4_machine_learning/alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')

blob = bucket.blob('pending_list.csv')
blob.download_to_filename('pending_list.csv')
pending_list = pd.read_csv('pending_list.csv', index_col=[0])
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')
temp_df = pd.read_csv("kol_list.csv", index_col=[0])

# input kol id
x = ""
index_pending = pending_list[pending_list['ig_id'] == x].index
pending_list = pending_list.drop(index_pending)
pending_list = pending_list.reset_index(drop=True)

new_row = [x, "Check Yet", datetime(2020, 1, 1).strftime("%Y-%m-%d"),
           datetime(2020, 1, 1).strftime("%Y-%m-%d"), 'yet']
cols = ['ig_id', 'is_HK', 'updated_following_list_time', 'details_updated_time', 'following_list']
new_df = pd.DataFrame([new_row], columns=cols)
temp_df = pd.concat([temp_df, new_df])
temp_df = temp_df.reset_index(drop=True)


# update 'updated_following_list_time' of selected_kol
temp_df.to_csv('kol_list.csv')
pending_list.to_csv('pending_list.csv')
# upload file which file name is ...
blob = bucket.blob('kol_list.csv')
blob.upload_from_filename('kol_list.csv')
# upload file which file name is ...
blob = bucket.blob('pending_list.csv')
blob.upload_from_filename('pending_list.csv')