import requests
import json
import re
import datetime
from parsers.models import Parser, Category, Deal

def ParserValidate(string):
	returnMsg = []
	try:
		parser = json.loads(string)
	except json.JSONDecodeError:
	    returnMsg.append("Incorrect Json String")
	    return returnMsg, False
	keys = list(parser.keys())
	returnItems = [x for x in keys if x != "default"]
	if "default" not in keys:
	    returnMsg.append("No default. Assigning empty string to all item defaults")
	    parser["default"] = dict(zip(keys, [""]*len(keys)))
	else:
	    try:
	        assert type(parser["default"]) is dict
	    except AssertionError:
	        returnMsg.append("default item in JSON is not a dict")
	        return returnMsg, False
	    for _, key in enumerate(parser):
	        if key != "default":
	            if key not in parser["default"]:
	                returnMsg.append( "Item " + key + " does not have a default. Assigning empty string")
	                parser["default"][key]=""
	    return returnMsg, True

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
		if (key != "default"):
			pattern = re.compile(parserDict[key])
			parsed = pattern.findall(content)
			if (len(parsed) > 0):
				result[key] = parsed[0]
			else:
				print("Can't parse %s" % key)
				result[key] = parserDict["default"][key]
	return result

def LoadCSV(csvfile):
	with open(csvfile, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			deal = models.Deal(title = row[0], \
							   website=row[1], \
							   price=float(row[2]), \
							   date=datetime.datetime.strptime(row[3], "%m/%d/%y %I:%M %p"), \
							   parser=models.Parser.objects.all()[0], \
							   category=models.Category.objects.all()[0])
			deal.save()

def TrackingDeal(dealTitle):
	deal = Deal.objects.filter(title=dealTitle).value("category", "website","parser").distinct()
	if len(deal) > 1:
		print("multiple url found. selecting first one.")
	deal = deal[0]
	parserloc = Parser.objects.filter(id=deal['parser']).values("filepath")[0]["filepath"]
	dealresult = ParseDeal(url=deal['website'], parserloc=parserloc)
	if dealresult:
		if dealresult.get('inStock', 'Out Of Stock') != 'Out Of Stock':
			price = dealresult.get('Price')
			try:
				float(price)
			except ValueError:
				print("Price is not float. Returned: " + price)
				return False
			newdeal = Deal(title=dealTitle, category=deal['category'], \
				website=deal['website'], price=price, \
				date=datetime.datetime.now(), parser=deal['parser'])
			newdeal.save()
			return True
	return False
			


