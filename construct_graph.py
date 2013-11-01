#! /usr/bin/env python

import networkx as nx
from networkx.readwrite import json_graph
import json
import bulbs.rexster as rex
from sets import Set
import random
import rdflib

def get_team_graph(G, team):
	#get all the team members
	team_members = filter(lambda x: "team" in x[-1] and x[-1]["team"] == team, [node for node in G.nodes_iter(data=True)])
	return G.subgraph(["GOAL"] + map(lambda x: x[0], team_members))

def main(filename, rexter_uri):
	# open the players file
	players = map(lambda x: json.loads(x), open(filename))
	
	#get a NetworkX graph
	G = nx.DiGraph()
	
	for p in players:
		G.add_node(p['name'], name=p['name'], team=p['team'])
		if p['goals'] > 0:
			G.add_edge(p['name'], "GOAL", weight=float(p['goals']))
		for passes in p['passesOut']:
			G.add_edge(p['name'], passes['Name'], weight=float(passes['Passes']), long_pass=passes['Long'],\
				short_pass=passes['Short'], medium_pass=passes['Medium'])
		for passes in p['passesIn']:
			G.add_edge(passes['Name'], p['name'], weight=float(passes['Passes']), long_pass=passes['Long'],\
				short_pass=passes['Short'], medium_pass=passes['Medium'])
		
		#print out the built node
		print G.node[p['name']]['name'], G.node[p['name']]['team'], G.in_degree(p['name'], weight="weight"), G.out_degree(p['name'], weight="weight")
	#print the number of edges and nodes in the graph
	print G.size(), len(G)
	#get the set of teams represented
	teams = filter(lambda x: 'team' in x, [node[1] for node in G.nodes_iter(data=True)])
	teams = Set(map(lambda x: x['team'], teams))
	
	
	for team in teams:
		team_graph = get_team_graph(G, team)
		#get the betweenness centrality for the team
		centrality = nx.betweenness_centrality(team_graph, weight="weight")
		for player in team_graph.nodes_iter():
			if player != "GOAL":
				team_graph.node[player]['centrality'] = centrality[player]
				G.node[player]['centrality'] = centrality[player]
		
	#print the whole graph as a JSON graph
	viz_graph = json_graph.node_link_data(G)
	json.dump(viz_graph, open("javascript/world_cup_graph.json", "w"))
	
	rdf_staging = rdflib.Graph() #open("rdf_staging_data.csv", "w")
	action_namespace = rdflib.Namespace("http://oracleworldcup.com/actions/")
	
	for edge in G.edges():
		team = G.node[edge[0]]['team']
		if edge[1] != "GOAL":
			#print >> rdf_staging, edge[0]+"-"+team, "passes", edge[1]+"-"+team, "worldcup"
			p1 = rdflib.URIRef("http://oracleworldcup.com/players/"+edge[0]+"-"+team)
			p2 = rdflib.URIRef("http://oracleworldcup.com/players/"+edge[1]+"-"+team)
			rdf_staging.add((p1, action_namespace.passes, p2))
		else:
			p1 = rdflib.URIRef("http://oracleworldcup.com/players/"+edge[0]+"-"+team)
			p2 = rdflib.URIRef("http://oracleworldcup.com/players/"+edge[1])
			rdf_staging.add((p1, action_namespace.scores, p2))
			#print >> rdf_staging, edge[0]+"-"+team, "scores", edge[1], "worldcup"
	#rdf_staging.close()
	rdf_staging.serialize("rdf_staging_table.nt", format="nt")
	
	nx.write_graphml(G, "worldcup.graphml")

		
	
if __name__ == "__main__":
	main("worldcup_passes.json", "localhost:8182")
	
