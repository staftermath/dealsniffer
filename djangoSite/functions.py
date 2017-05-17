import requests
import json
import re
import datetime
from parsers.models import Parser, Category, Deal

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

def LoadCSV(csvfile):
	with open(csvfile, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			deal = models.Deal(title = row[0], \
							   website=row[1], \
							   price=float(row[2]), \
							   date=datetime.datetime.strptime(row[3], "%m/%d/%y %I:%M %p"), \
							   parser=Parser.objects.all()[0], \
							   category=Category.objects.all()[0])
			deal.save()

