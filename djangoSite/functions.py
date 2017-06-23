import requests
import json
import re
import datetime
from parsers.models import Parser, Category, Deal, Price

class ParserException(Exception):
    def __init__(self, message=""):
        self.message = message

def ParserValidate(string):
	returnMsg = []
	try:
		parser = json.loads(string)
	except json.JSONDecodeError:
		returnMsg.append("Incorrect Json String")
		return returnMsg, False
	for _, key in enumerate(parser):
		thisEntry = parser[key]
		thisEntryKeys = thisEntry.keys()
		if "default" not in thisEntryKeys:
			returnMsg.append("KEY "+key+": No default. Assigning empty string to default")
			thisEntry["default"] = ""
		if "type" not in thisEntryKeys:
			returnMsg.append("KEY "+key+ ": No type. Assigning type 'string'")
			thisEntry["default"] = "string"
		else:
			if thisEntry.get("type", "") not in ["logical", "string"]:
				returnMsg.append("KEY "+key+ ": type must be 'string' or 'logical'")
				return returnMsg, False
		if "values" not in thisEntryKeys:
			returnMsg.append("KEY "+key+": No values. You must give regex patterns to value")
			return returnMsg, False
		else:
			try:
				assert type(thisEntry["values"]) is list
			except AssertionError:
				returnMsg.append("KEY "+key+": values is not a list")
				return returnMsg, False
			for pattern in thisEntry["values"]:
				try:
					re.compile(pattern)
				except TypeError:
					returnMsg.append("KEY "+key+": "+pattern+" is not a valid regex pattern")
					return returnMsg, False

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
	result = {"dealurl":url}
	for _, key in enumerate(parserDict):
		thisEntry = parserDict[key]
		try:
			parsed = content
			lenOfPatterns = len(thisEntry["values"])
			for i in range(lenOfPatterns - 1):
				pattern = re.compile(thisEntry["values"][i])
				searchResult = pattern.findall(parsed)
				if (len(searchResult) > 0):
					parsed = searchResult[0]
				else:
					raise ParserException("Parsor Returns Nothing: " + \
										  thisEntry["values"][i])
			pattern = re.compile(thisEntry["values"][lenOfPatterns-1])
			searchResult = pattern.findall(parsed)
			if (len(searchResult) > 0):
				if thisEntry.get("type", "") == "logical":
					result[key] = thisEntry.get("match")
				else:
					result[key] = searchResult[0]
			else:
				raise ParserException("Parsor Returns Nothing: " + \
										  thisEntry["values"][lenOfPatterns-1])
			prefix = thisEntry.get("prefix", "")
			suffix = thisEntry.get("suffix", "")
			result[key] = prefix + result[key] + suffix
		except ParserException:
			result[key] = thisEntry["default"]
	return result

def LoadCSV(csvfile):
	with open(csvfile, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			title = row[0]
			dealObject = Deal.objects.filter(title=title).distinct()[0]
			price = Price(deal = dealObject, \
							   price=float(row[2]), \
							   date=datetime.datetime.strptime(row[3], "%m/%d/%y %I:%M %p"))
			price.save()

# def TrackingDeal(dealTitle):
# 	deal = Deal.objects.filter(title=dealTitle).value("category", "website","parser").distinct()
# 	if len(deal) > 1:
# 		print("multiple url found. selecting first one.")
# 	deal = deal[0]
# 	parserloc = Parser.objects.filter(id=deal['parser']).values("filepath")[0]["filepath"]
# 	dealresult = ParseDeal(url=deal['website'], parserloc=parserloc)
# 	if dealresult:
# 		if dealresult.get('inStock', 'Out Of Stock') != 'Out Of Stock':
# 			price = dealresult.get('Price')
# 			try:
# 				float(price)
# 			except ValueError:
# 				print("Price is not float. Returned: " + price)
# 				return False
# 			newdeal = Deal(title=dealTitle, category=deal['category'], \
# 				website=deal['website'], price=price, \
# 				date=datetime.datetime.now(), parser=deal['parser'])
# 			newdeal.save()
# 			return True
# 	return False
			

def GetAllCategory():
	categoryObjects = Category.objects.all()
	brands = [x[0] for x in list(categoryObjects.values_list("brand").distinct())]
	mainclasses = [x[0] for x in list(categoryObjects.values_list("mainclass").distinct())]
	subclasses = [x[0] for x in list(categoryObjects.values_list("subclass").distinct())]
	return list(set(brands)), list(set(mainclasses)), list(set(subclasses))
	
def RecordPrice(dealId, queryset=None):
	if not queryset:
		queryset = Deal.objects.all()
	thisDeal = queryset.filter(id=dealId)[0]
	url = thisDeal.website
	parserloc = thisDeal.parser.filepath
	with open(parserloc, 'r') as file:
		parserDict = json.load(file)
	result = ParseDeal(url=url, parserloc=parserloc)
	for _, key in enumerate(parserDict):
		if result[key] == parserDict[key]["default"]:
			return None
	return float(re.findall("([0-9.]+)", result['Price'])[0])

