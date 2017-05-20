from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django import forms
from .forms import ContactForm, SelectDeal, SelectCategory
import datetime
import pytz
import json
import calendar
from books.models import Book, Publisher
from parsers.models import Deal, Category

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def index(request):
	return render(request, 'index.html')


def profile(request):
	user = request.user#User.objects.get(username=username)
	return render(request, 'user_profile.html', \
		{"user":user})

def logout_user(request):
	logout(request)
	return render(request, 'log_out.html')

def search(request):
	error = False
	if 'q' in request.GET:
		q = request.GET['q']
		if not q:
			error = True
		else:
			books = Book.objects.filter(title__icontains=q)
			return render(request, 'search_results.html',\
					  {'books': books, 'query':q})
	return render(request, 'search_form.html', \
					 {'error':error})


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
	# if 'title' in request.GET:
	# 	title = request.GET.get('title', default="")
	# 	brand = request.GET.get('brand', default="")
	# 	mainclass = request.GET.get('mainclass', default="")
	# 	subclass = request.GET.get('subclass', default="")
	# 	selected = dict(zip(["brand","mainclass","subclass","title"],[brand, mainclass, subclass, title]))
	# 	print(selected)
	# 	rawData = list(Deal.objects.filter(title=title).values('date', 'price'))
	# 	return render(request, 'chart.html', {"menuDict":json.dumps(menuDict), \
	# 		"data":json.dumps(rawData, default=datetime_handler).encode('utf8'), \
	# 		"selected":json.dumps(selected)})
	return render(request, 'chart.html', {"menuDict":json.dumps(menuDict)})

def plottrend(request):
	brand = request.GET.get('brand', default="")
	mainclass = request.GET.get('mainclass', default="")
	subclass = request.GET.get('subclass', default="")
	title = request.GET.get('title', default="")
	category = Category.objects.filter(brand=brand, mainclass=mainclass,subclass=subclass)
	if (category.count() > 0):
		category = category[0]
		rawData = list(Deal.objects.filter(title=title, category=category).values('date', 'price'))
	else:
		rawData = None
	return render(request, 'deal_trend.html', {"data":json.dumps(rawData,default=datetime_handler).encode('utf8'),\
		"title":title})


def generate_deal_data(request, item=None):
	if not item:
		data = list(Deal.objects.values('date', 'price'))
	else:
		data = list(Deal.objects.filter(title=item).values('date', 'price'))
	return JsonResponse(data, safe=False)

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			send_mail(
				cd['subject'],
				cd['message'],
				cd.get('email', 'noreply@example.com'),
				['siteowner@example.com']
				)
			return HttpResponseRedirect('/contact/thanks/')
	else:
		form = ContactForm(initial={'subject':'I love your site!'})
	return render(request, 'contact_form.html', \
			{'form': form})

def PassDjangoData(request):
    data = Deal.objects.all()
    return JsonResponse(list(data), safe=False)

class PublisherList(ListView):
	model = Publisher

class PublisherDetail(DetailView):
	model = Publisher

	def get_context_data(self, **kwargs):
		context = super(PublisherDetail, self).get_context_data(**kwargs)
		context['book_list'] = Book.objects.all()
		return context

class PublisherBookList(ListView):
	template_name = 'books/books_by_publisher.html'
	"""docstring for PublisherBookList"""
	def get_queryset(self):
		self.publisher = get_object_or_404(Publisher, name=self.args[0])
		return Books.objects.filter(publisher=self.publisher)

	def get_context_data(self, **kwargs):
		context = super(PublisherBookList, self).get_context_data(**kwargs)

		context['publisher'] = self.publisher
		return context

