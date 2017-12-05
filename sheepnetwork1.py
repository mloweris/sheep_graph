# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pandas as pd
import math
import numpy as np

edgelist = pd.read_csv("edgelist.csv")
edgelist.columns = ['Row', 'source_str', 'target_str', 'day', 'animal_list']
edgelist['source'] = edgelist.source_str.str.replace("/", "").astype('int')
edgelist['target'] = edgelist.target_str.str.replace("/", "").astype('int')
edgelist.animal_list = [np.array(list(map(int, eval(x)))) for x in edgelist.animal_list]
edgelist.drop(['source_str', 'target_str'], axis = 1, inplace = True)
edgelist['num_animals'] = [len(x) for x in edgelist.animal_list]

nodeinfo = pd.read_csv("nodeinfo.csv")
nodeinfo.columns = ['ROW', 'nullname', 'locType', 'locID2_str', 'day', 'animal_list']
nodeinfo = nodeinfo[~pd.isnull(nodeinfo.animal_list)]
nodeinfo['locID'] = nodeinfo.locID2_str.str.replace("/", "").astype('int')
nodeinfo.animal_list = [np.array(list(map(int, eval(x)))) for x in nodeinfo.animal_list]

node_types = pd.read_csv("node_type.csv")
node_types.columns = ["value", "locID_str", "locType"]
node_types = node_types[~pd.isnull(node_types.locID_str)]
node_types['locID'] = node_types.locID_str.str.replace("/", "").astype('int')

nodeinfo.day.fillna(value = -9999, inplace=True)

issue_locs = nodeinfo[~(nodeinfo.day == -9999)].copy()
issue_locs.drop(['ROW', 'nullname', 'locType'], axis = 1, inplace = True)

nodes_types = node_types[['locID', "locType"]].copy().drop_duplicates()

##data frame of all nodes and types
nodes_types.sort_values(by = ["locID", "locType"],ascending = [True, False], inplace = True)
nodes_types = nodes_types[~nodes_types.locID.duplicated(keep="first")].dropna(axis=0, how='any')

##data frame containing list of animals added each day by issue date before end of year
issue_locs['num_animals'] = [len(x) for x in issue_locs.animal_list]
issue_locs = issue_locs[issue_locs.day < 366]
#issue_locs = issue_locs.groupby(['locID', 'day'], as_index=False).sum()
##data frame of all movements
edgelist

##issue when converting locID to numeric:
##duplicated numeric for locID = "01/122/9003" and "11/2/29003"
##second one does not match the format of all others - input error?

import networkx as nx

graph = nx.MultiDiGraph()

graph.add_nodes_from(list(nodes_types.locID))
nx.set_node_attributes(graph, dict(zip(list(nodes_types.locID), list(nodes_types.locType))), 'Type')

##add animals from issue dates as new animals per farm - each farm has one array with as many rows as number of days when animals are registered
##first value in each row of array is the day the animals were added, the rest are animalIDs

animals_born = pd.DataFrame({'locID' : list(set(issue_locs.locID))})
reg_animals = []

for i in animals_born.locID:
    temp_df = issue_locs[issue_locs.locID==i].copy()
    temp_df['day_array'] = [np.insert(x, 0, y) for (x, y) in zip(temp_df.animal_list, temp_df.day)]
    reg_animals = reg_animals + [np.array(list(temp_df.day_array))]

animals_born['reg_animals'] = reg_animals

nx.set_node_attributes(graph, dict(zip(list(animals_born.locID), list(animals_born.reg_animals))), 'Day-AnimalsRegistered')
    
##add edges, weight, animal_list and day are attributes
##weight - number of animals moved, int
##animal_list - list of animalIDs moved, np.array
##day - day of move, int

edgelist['dict'] = [{'Weight':len(x), 'animal_list':x, 'Day':y} for x,y in zip(list(edgelist.animal_list), list(edgelist.day))]
edgelist_dict = list(zip(list(edgelist.source), list(edgelist.target), list(edgelist.dict)))
graph.add_edges_from(edgelist_dict)

nx.write_gpickle(graph, "sheep_sparse.gpickle")
nx.write_graphml(graph, 'sheep_sparse.graphml')
nx.write_gexf(graph,"sheep_sparse.gexf")

##graph with only movement weights and node type

graph2 = nx.MultiDiGraph()

graph2.add_nodes_from([np.uint64(i).item() for i in list(nodes_types.locID)])
nx.set_node_attributes(graph2, dict(zip(list(nodes_types.locID), list(nodes_types.locType))), 'Type')

edgelist['dict2'] = [{'Weight':np.uint64(len(x)).item(), 'Day':np.uint64(y).item()} for x,y in zip(list(edgelist.animal_list), list(edgelist.day))]
edgelist_dict2 = list(zip([np.uint64(i).item() for i in list(edgelist.source)], [np.uint64(i).item() for i in list(edgelist.target)], list(edgelist.dict2)))
graph2.add_edges_from(edgelist_dict2)

nx.write_gpickle(graph2, "sheep_sparse_weightsonly.gpickle")
nx.write_graphml(graph2, 'sheep_sparse_weightsonly.graphml')









##not so sparse graph
import networkx as nx

graph = nx.MultiDiGraph()

graph.add_nodes_from(list(nodes_types.locID))

nx.set_node_attributes(graph, dict(zip(list(nodes_types.locID), list(nodes_types.locType))), 'Type')

for i in range(len(issue_locs)):
    loc = issue_locs.locID.iloc[i]
    animals = issue_locs.locID.iloc[i]
    day = issue_loc.day.iloc[i]
    att_name = "Day " + str(day) + " new animals"
    nx.set_node_attribut
    


#for i in list(nodes_types.locID):
#    graph.node[i]['Day']['-1'] = {'current_animals':[], 'historical_animals':[], 'new_animals':[], 'animals_lost':[]}

##first add animal lists from issue dates as attributes (animals being born on farm)
##second add edges based on movements (weight is number of animals moved, animal list, and day of move)
##third update nodes to reflect animals moved
    
for i in range(366):
    df = issue_locs[issue_locs.day==i]
        
    for k in list(nodes_types.locID):
        
        if len(df)>0 and (k in list(df.locID2)):
            graph.node[k]['Day'][str(i)] = graph.node[k]['Day'][str(i-1)]
            graph.node[k]['Day'][str(i)]['current_animals'] = list(set(graph.node[k]['Day'][str(i-1)]['current_animals'] + df.animal_list[df.locID2==k].item()))
            graph.node[k]['Day'][str(i)]['historical_animals'] = list(set(df.animal_list[df.locID2==k].item() + graph.node[k]['Day'][str(i-1)]['historical_animals']))
            graph.node[k]['Day'][str(i)]['new_animals'] = df.animal_list[df.locID2==k].item()
        else:
           graph.node[k]['Day'][str(i)] = graph.node[k]['Day'][str(i-1)]
    
    df1 = edgelist[edgelist.day==i].copy()
    
    if len(df1)>0:
        df1['dict1'] = [{'Weight':len(x), 'animal_list':x, 'Day':str(i)} for x in list(df1.animal_list)]
        dftup = list(zip(list(df1.source), list(df1.target), list(df1.dict1)))
        
        graph.add_edges_from(dftup)
        
        for k in list(df1.target):
            animals_recd=[st for row in df1.animal_list[df1.target==k] for st in row]
            graph.node[k]['Day'][str(i)]['current_animals'] = list(set(graph.node[k]['Day'][str(i)]['current_animals'] + animals_recd))
            graph.node[k]['Day'][str(i)]['historical_animals'] = list(set(animals_recd + graph.node[k]['Day'][str(i)]['historical_animals']))
            graph.node[k]['Day'][str(i)]['new_animals'] = list(set(animals_recd))
            
        for k in list(df1.source):
            animals_sent = [st for row in df1.animal_list[df1.source==k] for st in row]
            graph.node[k]['Day'][str(i)]['current_animals'] = list(set(graph.node[k]['Day'][str(i)]['current_animals']) - set(animals_sent))
            graph.node[k]['Day'][str(i)]['historical_animals'] = list(set(animals_sent + graph.node[k]['Day'][str(i)]['historical_animals']))   
            
            
nx.write_gpickle(graph, "sheep_nw1.gpickle")
nx.write_graphml(graph, 'sheep_nw1.graphml')
nx.write_gexf(graph,"sheep_nw1.gexf")
