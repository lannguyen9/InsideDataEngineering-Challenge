#!/usr/bin/python
# coding: utf-8

import os
import json
import sys
import time
import numpy as np
from dateutil import parser
import datetime
import networkx as nx
import matplotlib.pyplot as plt

### Data Munge
data = []
with open(sys.argv[1]) as f:   
    for line in f:
        data.append(json.loads(line))    #Decode JSON to Python

# find length of tweet_input
with open(sys.argv[1]) as f:  
    last = sum(1 for _ in f) - 1

# scan for tweets in last 60 seconds
prev=0
delta=datetime.timedelta(0,0)
while delta < datetime.timedelta(minutes=1):
    t0 = parser.parse(data[last-prev]['created_at'])
    t1 = parser.parse(data[last-1]['created_at'])
    delta = t1-t0
    prev=prev+1
    
first = last-prev

### Pull hashtags and Merge to Adjacency List

graph = {}

def merge_two_graphs(x, y):    #Function to merge (extend) dictionaries with lists
    d = {}
    for key in set(graph.keys() + graphy.keys()):
        try:
            d.setdefault(key,[]).extend(graph[key])        
        except KeyError:
            pass
        try:
            d.setdefault(key,[]).extend(graphy[key])          
        except KeyError:
            pass
    return d

def pull_hashtags(j):    #Retrieve hashtags from tweets.txt
    graph_temp={}
    htag_num=len(data[j]['entities']['hashtags'])
    if htag_num > 1:    #hashtag order
        for i in range(0,htag_num, 1):    
            if i == 0:
                graph_temp = {data[j]['entities']['hashtags'][0]['text'].lower(): [data[j]['entities']['hashtags'][htag_num-1]['text'].lower()]}
            elif 0< i < htag_num:
                graph_temp[data[j]['entities']['hashtags'][i]['text'].lower()] = [data[j]['entities']['hashtags'][i-1]['text'].lower()]
            elif i == htag_num-1:
                graph_temp[data[j]['entities']['hashtags'][i]['text'].lower()] = [data[j]['entities']['hashtags'][0]['text'].lower()]
    return graph_temp
                
                
for j in range(last, first, -1):    # Build adjacency list
    if j == last:
        graph = pull_hashtags(j)
    else:
        graphy = pull_hashtags(j)
        graph = merge_two_graphs(graph, graphy)


### Draw Graph Logic
def gen_edges(graph):
    edges = []
    for node in graph:
        for neighbour in graph[node]:
            edges.append((node, neighbour))

    return edges

def draw_graph(graph2):
    plt.clf()
    nodes = set([n1 for n1, n2 in graph2] + [n2 for n1, n2 in graph2])  # Extract nodes from graph

    G = nx.Graph()   # Graph - No Edges

    for node in nodes:    #Nodes
        G.add_node(node)

    for edge in graph2:    #Edges
        G.add_edge(edge[0], edge[1])

    pos = nx.spring_layout(G)    # Layout settings
    nx.draw_networkx_nodes(G,pos,node_size=1500, node_color='w', font_size=6)
    nx.draw_networkx_edges(G,pos,alpha=0.75,width=3)
    nx.draw_networkx_labels(G,pos, font_color='b')

    plt.title('Twitter Hashtag Graph')
    plt.axis('off')     # Show graph
    plt.savefig(".\\images\\graph.png")
    
    # Calculate average degree
    average_degree = np.mean(nx.degree(G).values())
    ft2 = open(sys.argv[2], 'a')    # Write to ft2.txt
    
    if np.isnan(average_degree): # NaN for no hashtags
        ft2.write('0.00'+'\n')
    else:
        aver_deg = format(average_degree, '.2f')
        ft2.write(str(aver_deg)+'\n')
    ft2.close()
    
    return

# Draw Graph and Calculate 
edge_graph = gen_edges(graph)  # Edge list first
draw_graph(edge_graph)   # Graph


### Check for latest tweet
n=0
while True:
    data = []
    with open(sys.argv[1]) as f:   
        for line in f:
            data.append(json.loads(line))    #Decode JSON to Python
        
    # find length of tweet_input
    with open(sys.argv[1]) as f:  
        latest = sum(1 for _ in f) - 1

    # Check the previous first tweet to the latest tweet's timestamp
    t2 = parser.parse(data[latest-1]['created_at'])
    delta2 = t2-t0
    if delta2 > datetime.timedelta(minutes=1): # first is too far away
        pass
        if data[latest]==data[last]:   # latest is still the last received
            pass
        
        else:   # Latest is new
            print('Latest tweet is a new tweet.')
            
            
            # Rerun Setup
            prev=0
            last = latest # New last
            while delta < datetime.timedelta(minutes=1):
                t0 = parser.parse(data[last-prev]['created_at'])
                t1 = parser.parse(data[last-1]['created_at'])
                delta = t1-t0
                prev=prev+1
    
            first = last-prev
            
            graph = {}
            
            for j in range(last, first, -1):    # Build adjacency list
                if j == last:
                    graph = pull_hashtags(j)
                else:
                    graphy = pull_hashtags(j)
                    graph = merge_two_graphs(graph, graphy)
            
            
            # Draw Graph and Calculate Average Degree
            edge_graph = gen_edges(graph)  # Edge list first
            draw_graph(edge_graph)   # Graph
            print('Constructing graph. Re-calculating rolling average degree.')
    
    print('No new tweets. Retrying in 20 seconds...')
    time.sleep(20)  # Wait for 20s to retry
    n=n+1
    if n==3:
        break
