# This file is to clean data before send to Big Query

import pandas as pd
from gcloud import storage

# download from google cloud storage
client = storage.Client.from_service_account_json('alpine-freedom-346707-ee6c1a5cbd5f.json')
bucket = client.get_bucket('dataproc-staging-us-central1-151287915422-novabmnn')
blob = bucket.blob('kol_post.csv')
blob.download_to_filename('kol_post.csv')

# clean data - kol_post
df = pd.read_csv('kol_post.csv', index_col=[0])
df['content'] = df['content'].replace('\n', '', regex=True)
df['content'] = df['content'].replace('\n', '', regex=True)
df['content'] = df['content'].replace('\n\n', '', regex=True)
df['content'] = df['content'].replace('\n\n\n', '', regex=True)
df['content'] = df['content'].replace('\n\n\n\n', '', regex=True)
df['post_alt'] = df['post_alt'].replace('\n', '', regex=True)
df['post_alt'] = df['post_alt'].replace('\n\n', '', regex=True)
df['post_alt'] = df['post_alt'].replace('\n\n\n', '', regex=True)
df['post_alt'] = df['post_alt'].replace('\n\n\n\n', '', regex=True)
df.reset_index(drop=True)
df.to_csv("kol_post.csv")

# kol_post upload to GCS
blob = bucket.blob('kol_post.csv')
blob.upload_from_filename('kol_post.csv')

# kol_info reset index
blob = bucket.blob('kol_info.csv')
blob.download_to_filename('kol_info.csv')

df2 = pd.read_csv('kol_info.csv', index_col=[0])
df2.reset_index(drop=True)
df2.to_csv("kol_info.csv")

blob = bucket.blob('kol_info.csv')
blob.upload_from_filename('kol_info.csv')

# kol_list reset index
blob = bucket.blob('kol_list.csv')
blob.download_to_filename('kol_list.csv')

df = pd.read_csv('kol_list.csv', index_col=[0])
df2 = pd.read_csv('check.csv', index_col=[0])

igid_list = df2['ig_id'].to_list()
is_HK_list = df2['is_HK'].to_list()

df = df.set_index('ig_id')
y = 0
for x in igid_list:
    df.loc[[igid_list[y]], ['is_HK']] = is_HK_list[y]
    y = y + 1
df = df.reset_index()
df.to_csv('kol_list.csv')

temp_df = df[['is_HK', 'ig_id']]
temp_df2 = temp_df.merge(df2, how='inner', on='ig_id')
temp_df2.to_csv('check2.csv')
temp_df2.to_csv('check.csv')


df3 = pd.read_csv('kol_list.csv', index_col=[0])
df3.reset_index(drop=True)
df3['following_list']
df3.to_csv("kol_list.csv")

blob = bucket.blob('kol_list.csv')
blob.upload_from_filename('kol_list.csv')