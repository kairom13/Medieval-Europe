"""
Created on Jan 1, 2022

@author: kairom13
"""

import networkx as nx
#import matplotlib.pyplot as plt
import json

from Medieval_Europe.Code.CustomObjects import Person, Logger


with open("../Medieval_Europe/Files/Data/people.json", 'r') as stream:
    personList = {'Person': {}}
    init_list = json.loads(stream.read())

    logger = Logger(personList)

    if init_list is not None:
        for key in init_list:
            personDict = init_list[key]

            person = Person(logger, personDict['Gender'], personDict, key)

            personList['Person'].update({person.getID(): person})


G = nx.DiGraph()
labels = {}

for p, person in personList['Person'].items():
    edge = False
    if person.father is not None:
        #dad = personList[person.father]
        G.add_edge(person.father, p, color='r')
        edge = True
        
    if person.mother is not None:
        #mom = personList[person.mother]
        G.add_edge(person.mother, p, color='b')
        edge = True
        
    for s in person.spouses:
        if s != 'unknown_spouse':
            G.add_edge(p, s, color='g')
            edge = True

    if not edge:
        G.add_node(p)

    labels[p] = person.getAttribute('Name')
        
colors = nx.get_edge_attributes(G, 'color').values()
pos = nx.kamada_kawai_layout(G)

nx.draw_kamada_kawai(G, with_labels=False, edge_color=colors, node_size=15, width=0.5, font_size=7)
#print(pos)
nx.draw_networkx_labels(G, pos, labels, font_size=6, alpha=.7)
#nx.draw_spectral(G, pos, labels, with_labels=True, edge_color=colors, node_size=15, width=0.5, font_size=7)