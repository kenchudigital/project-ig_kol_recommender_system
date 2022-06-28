# Graph Analysis
import pandas as pd

df = pd.read_csv('kol_features.csv')
df_list = pd.read_csv('kol_info.csv')
df[['ig_id', 'following_list', 'is_HK']]
df.drop(df.loc[df.following_list ==  "yet"].index, inplace=True)
df.drop(df.loc[df.following_list ==  "[]"].index, inplace=True)
df = df[['ig_id', 'name', 'following_list', 'is_HK', 'no_of_follower']].reset_index(drop=True)

# table for Gephi - > edged table
count = 0
column_names = ["Target", "Source", "is_HK", "no_of_follower"]
df2 = pd.DataFrame(columns = column_names)
for x in df['ig_id'].to_list():
    df['ig_id'].iloc[count]
    df['is_HK'].iloc[count]
    df['no_of_follower'].iloc[count]
    df['following_list'].iloc[count]
    convertlist = df['following_list'].iloc[count].replace('\'', '').replace('[', '').replace(']', '').replace('\"', '').split(', ')
    df_temp = pd.DataFrame(convertlist).rename(columns={0:'Target'})
    df_temp['Source'] = df['ig_id'].iloc[count]
    df_temp['is_HK']= df['is_HK'].iloc[count]
    df_temp['no_of_follower'] = df['no_of_follower'].iloc[count]
    df2 = pd.concat([df_temp, df2], join="inner")
    count = count+1

# kill_list
kill_list = []
for x in df2['Target'].to_list():
    if x in df_list['ig_id'].to_list():
        pass
    else:
        kill_list.append(x)

df2 = df2[['Source', 'Target']].set_index('Target')
kill_list = list(set(kill_list))
count = 0
# kill_list has 100,000
for y in kill_list:
    try:
        df2 = df2.drop(y)
        print(count)
        count += 1
    except:
        pass
df2.to_csv('temp.csv')

df2 = df2.reset_index()
edge_tuples = df2[["Source", "Target"]].itertuples(index=False, name=None)
import networkx as nx
G = nx.Graph()
G.add_edges_from(edge_tuples)
import matplotlib.pyplot as plt
from networkx.algorithms import community

barbell_G = nx.barbell_graph(5, 1)
communities_generator = community.girvan_newman(barbell_G)
top_level_communities = next(communities_generator)
next_level_communities = next(communities_generator)

from networkx.algorithms.community import greedy_modularity_communities

c = list(greedy_modularity_communities(G))
print("Number of groups:", len(c))
print("Group sizes:", list(map(len, c)))

c.type()