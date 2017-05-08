import requests
import json
import re

def ParseDeal(url, parserloc):
	try:
		r = requests.get(url)
	except:
		print("Can't get URL")
		return None
	content = r.text
	with open(parserloc, 'r') as file:
		parserDict = json.load(file)
	result = dict()
	for _, key in enumerate(parserDict):
		pattern = re.compile(parserDict[key])
		parsed = pattern.findall(content)
		if (len(parsed) > 0):
			result[key] = parsed[0]
		else:
			print("Can't parse %s" % key)
	print(result)

