import urllib2
import re
from bs4 import BeautifulSoup
from sets import Set
import json

conversion_list = ["passesTo", "passesFrom", "name", "matches", "HomeTeamName",\
"HomeCountryCode", "AwayTeamName", "AwayCountryCode", "MatchDate", "ResultStr", "LongPass", "MediumPass",\
"ShortPass", "Pass", "label", "value"]

class Player(object):
    def __init__(self):
        self.info = {}
        

def convert_to_hash(data):
    data = re.sub("\(", "", data)
    data = re.sub("\)", "", data)
    player_regex = re.compile("pl_.*?:")
    player_strings = player_regex.findall(data)
    for s in player_strings:
        data = re.sub(s,'"'+s[:-1]+'":', data)
    for l in conversion_list:
        data = re.sub(l, '"'+l+'"', data)
    data = re.sub('\w"Pass""', 'Pass"', data)
    return data
    

def find_out_players(p_hash):
	players = p_hash["passesTo"].keys()
	players = map(lambda x: re.sub("pl_", "", x), players)
	return players

def find_in_players(p_hash):
	players = p_hash["passesFrom"].keys()
	players = map(lambda x: re.sub("pl_", "", x), players)
	return players
    

def get_passes(pl, pass_hash):
	result = {}
	player_passes = pass_hash["pl_"+pl]
	result["Name"] = player_passes["name"]
	result["Passes"] = player_passes["Pass"]
	result["Long"] = player_passes["LonPass"]
	result["Short"] = player_passes["ShorPass"]
	result["Medium"] = player_passes["MediuPass"]
	return result

def main():
	#this is a list of player IDs from the FIFA website
	#trivially, we're starting with the top 5 scorers
	player_list = Set(["321722", "229884", "215002", "189259", "271550"])
	processed = Set()
	output_file = open("worldcup_passes.json", "w")
	while len(player_list) > 0:
		pl = player_list.pop() #note: this is an unordered operation
		base_url = "http://www.fifa.com/worldcup/archive/southafrica2010/statistics/players/player="+pl
		passing_url = "http://www.fifa.com/worldcup/archive/southafrica2010/statistics/players/player="+pl+"/passingdistributionpermatch.txt"
		stats_url = "http://www.fifa.com/worldcup/archive/southafrica2010/statistics/players/player="+pl+"/mstat.txt"

		a = re.sub("\s", "",urllib2.urlopen(passing_url).read())

		d = convert_to_hash(a)
		player_pass_hash = eval(d)
		if len(player_pass_hash["passesTo"]) > 0:
			name_soup = BeautifulSoup(urllib2.urlopen(base_url).read())
			#this is a valid record, so get the goals
			goal_stats = re.sub("\s", "",urllib2.urlopen(stats_url).read())
			#get the goal string
			goal_regex = re.compile('{label:"Goalsscored".*?}')
			goals_field = goal_regex.findall(goal_stats)[0]
			goal_hash = eval(convert_to_hash(goals_field))
			players_out = find_out_players(player_pass_hash)
			players_in = find_in_players(player_pass_hash)
			players = Set(players_out).union(Set(players_in))
			player_list = player_list.union(Set(players))
			player_list = player_list.difference(processed) #use the difference to ensure we don't duplicate
			print player_list
			p  = Player()
			p.info['name'] = name_soup.find_all("div", class_="lastPlayerName lastColor")[-1].get_text()
			p.info['team'] = name_soup.find("span", class_="playerTriCode").get_text()
			p.info['name'] = re.sub(" ", "", re.sub(p.info['team'], "", p.info['name']))
			p.info['goals'] = goal_hash['value']
			p.info['passesOut'] = []
			for teammate in players_out:
				player_to = get_passes(teammate, player_pass_hash["passesTo"])
				p.info['passesOut'].append(player_to)
			p.info['passesIn'] = []
			for teammate in players_in:
				player_from = get_passes(teammate, player_pass_hash["passesFrom"])
				p.info['passesIn'].append(player_from)

			print >> output_file, json.dumps(p.info)
			processed.add(pl)
	output_file.close()

if __name__ == "__main__":
	main()
    