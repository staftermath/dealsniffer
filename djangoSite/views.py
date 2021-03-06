from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
# from django.core.serializers import serialize
# from django.core.serializers.json import DjangoJSONEncoder
from django import forms
from .forms import ContactForm, SelectDeal, SelectCategory, AddParser, SelectParser, AddDeal, AddCategory, QueryMenu
import datetime
import pytz
import json
import calendar
import os
from django.conf import settings
from books.models import Book, Publisher
from parsers.models import Deal, Category, Parser, Price
from .functions import ParseDeal, ParserValidate, GetAllCategory
from access.models import DealAccess
# from settings import BASE_DIR
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def index(request):
	user = request.user#User.objects.get(username=username)
	msg = []
	if user.is_staff:
		accessibleDealId = set(DealAccess.objects.filter(user=user).values_list("deal", flat=True))
		allDeals = set(Deal.objects.values_list("id", flat=True))
		unsavedDeal = allDeals - accessibleDealId
		for id in unsavedDeal:
			dealaccess = DealAccess(user=user,deal=Deal.objects.filter(id=id)[0])
			dealaccess.save()
		if len(unsavedDeal) > 0:
			msg.append(str(len(unsavedDeal)) + " new deals are saved for you as staff account")
		else:
			msg.append("No new deals added to your account")
	if not user.is_anonymous():
		accessibleDealId = list(DealAccess.objects.filter(user=user).values_list("deal", flat=True))
		accessibleDeal = Deal.objects.filter(id__in=accessibleDealId)
		menuUserDealAccessible = QueryMenu(queryset=accessibleDeal, id="menu_user_deal_accessible")
		return render(request, 'index.html', {"menuUserDealAccessible":menuUserDealAccessible})
	else:
		return render(request, 'index.html')


def profile(request):
	user = request.user#User.objects.get(username=username)
	accessibleDeal = DealAccess.objects.filter(user=user)
	menuUserDealAccessible = QueryMenu(queryset=accessibleDeal, id="menu_user_deal_accessible")
	return render(request, 'user_profile.html', \
		{"menuUserDealAccessible": menuUserDealAccessible})

def logout_user(request):
	logout(request)
	return render(request, 'log_out.html')

def dealtrend(request):
	allCategories = Category.objects.all()
	brandList = list(allCategories.values_list('brand', flat=True).distinct())
	menuDict = dict(zip(brandList, [None]*len(brandList)))
	for brand in brandList:
		thisBrandQuery = allCategories.filter(brand=brand)
		mainclassList = list(thisBrandQuery.values_list('mainclass', flat=True).distinct())
		menuDict[brand] = dict(zip(mainclassList, [None]*len(mainclassList)))
		for mainclass in mainclassList:
			thisMainclassQuery = thisBrandQuery.filter(mainclass=mainclass)
			subclassList = list(thisMainclassQuery.values_list('subclass', flat=True).distinct())
			menuDict[brand][mainclass] = dict(zip(subclassList, [None]*len(subclassList)))
			for subclass in subclassList:
				categorySelected = Category.objects.get(brand=brand, mainclass=mainclass,\
													subclass=subclass)
				allDealsSelected = Deal.objects.filter(category=categorySelected)
				dealList = list(allDealsSelected.values_list('title', flat=True).distinct())
				menuDict[brand][mainclass][subclass] = dealList
	return render(request, 'chart.html', {"menuDict":json.dumps(menuDict)})

def plottrend(request):
	brand = request.GET.get('brand', default="")
	mainclass = request.GET.get('mainclass', default="")
	subclass = request.GET.get('subclass', default="")
	title = request.GET.get('title', default="")
	category = Category.objects.filter(brand=brand, mainclass=mainclass,subclass=subclass)
	if (category.count() > 0):
		category = category[0]
		thisdeal = Deal.objects.filter(title=title, category=category).distinct()[0]
		rawData = list(Price.objects.filter(deal=thisdeal).values('date', 'price'))
		# rawData = list(Deal.objects.filter(title=title, category=category).values('date', 'price'))
	else:
		rawData = None
	return render(request, 'deal_trend.html', {"data":json.dumps(rawData,default=datetime_handler).encode('utf8'),\
		"title":title})

def grabdeal(request):
	parser = request.GET.get('parser', default="")
	objectParser = list(Parser.objects.filter(name=parsername).values('filepath'))[0]
	alldeals = [x[0] for x in list(Deal.objects.filter(parser=objectParser))]
	thisdealURL = list(Deal.objects.filter(title=title).values('website'))[0]
	testResult = ParseDeal(url=thisdealURL['website'], parserloc=objectParser['filepath'])
	testResult['inStock'] = testResult.get('testResult', "Out Of Stock")
	lastResult = {"title":title, \
				  "parser":parsername}

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			print()
			send_mail(
				cd['subject'],
				"from " + cd.get('email') + "\n============================\n" + cd['message'],
				cd.get('email', 'noreply@example.com'),
				['dealsniffer.com@gmail.com']
				)
			return HttpResponseRedirect('/')
	else:
		form = ContactForm(initial={'subject':'I love your site!'})
	return render(request, 'contact_form.html', \
			{'form': form})

def PassDjangoData(request):
    data = Deal.objects.all()
    return JsonResponse(list(data), safe=False)

@staff_member_required
def addparser(request):
	print(request.user.is_staff)
	parserform = AddParser()
	dealform = AddDeal()
	# allParsers = list(Parser.objects.values_list('name'))
	# allParsers = [x[0] for x in allParsers]
	# menu = SelectParser(choices=allParsers)
	allParsers = Parser.objects.all()
	menu = QueryMenu(queryset=allParsers, id="form_select_parser_view_deal")
	dealform.addparser(queryset=allParsers, id="form_select_parser_add_deal")
	allCategory = GetAllCategory()
	categoryForm = AddCategory(*allCategory)
	if request.method == "POST":
		if request.POST.get('add_parser')=='add_parser':
			name = request.POST['name']
			parser = request.POST['body']
			filename = request.POST['filename']
			filepath = os.path.join(settings.BASE_DIR, 'parsers','parserfiles',filename)
			msgs, validParser = ParserValidate(parser)
			if validParser:
				with open(filepath, 'w') as file:
					print(parser, file=file)
				parserData = Parser(name=name, filepath=filepath)
				try:
					parserData.save()
					msgs.append("New Parser Saved!")
				except:
					msgs.append("Could not save new parser")
			return render(request, 'view_parser.html', {"addparser":parserform, \
														"adddeal":dealform,\
														"categoryform":categoryForm,\
														"parsermenu":menu, \
														"allParsers":allParsers, \
														"msgs":msgs, \
														"validparser":validParser})
		if request.POST.get('add_deal')=='add_deal':
			title = request.POST['title']
			website = request.POST['website']
			parserid = request.POST['parser']
			brand = request.POST['brand']
			mainclass = request.POST['mainclass']
			subclass = request.POST['subclass']
			
			parserID = Parser.objects.filter(id=parserid)[0]
			msgs = []
			newCategory = Category(brand=brand, mainclass=mainclass, subclass=subclass)
			if Category.objects.filter(brand=brand, mainclass=mainclass, subclass=subclass).count() == 0:
				try:
					newCategory.save()
					msgs.append("New Category Saved")
				except:
					msgs.append("Could not save new deal")
			targetCategory = Category.objects.filter(brand=brand, mainclass=mainclass, subclass=subclass)[0]
			newdeal = Deal(title=title, website=website, parser = parserID, category=targetCategory)
			try:
				newdeal.save()
				msgs.append("New Deal Saved")
			except:
				msgs.append("Could not save new deal")
			
			return render(request, 'view_parser.html', {"addparser":parserform, \
														"adddeal":dealform,\
														"categoryform":categoryForm,\
														"parsermenu":menu, \
														"allParsers":allParsers, \
														"msgs":msgs})

	return render(request, 'view_parser.html', {"addparser":parserform, \
												"adddeal":dealform,\
												"categoryform":categoryForm,\
												"parsermenu":menu, \
												"allParsers":allParsers})



def generate_deal_data(request):
	dealId = request.GET.get('deal', default="")
	deal = Deal.objects.filter(id=dealId)[0]
	parser = deal.parser
	parserloc = parser.filepath
	url = deal.website
	dealresult = ParseDeal(url=url, parserloc=parserloc)
	return render(request, "display_deal.html", {"dealresult":dealresult})


def get_deal_for_parser(request, parser=None):
	if request.GET.get('parser'):
		objectParser = Parser.objects.filter(id=request.GET.get('parser'))
		dealList = list(Deal.objects.filter(parser=objectParser).values_list("id","title").distinct())
		
		return JsonResponse(dealList, safe=False)
	else:
		return ""
