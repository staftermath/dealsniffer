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
	mainclassList = list(allCategories.values_list('mainclass', flat=True).distinct())
	subclassList = list(allCategories.values_list('subclass', flat=True).distinct())
	categorySelect = SelectCategory(brandList, mainclassList, subclassList)
	if request.method == 'GET':
		
		brand = request.GET.get('brand')
		mainclass = request.GET.get('mainclass')
		subclass = request.GET.get('subclass')
		categorySelected = Category.objects.get(brand=brand, mainclass=mainclass,\
												subclass=subclass)
		rawData = list(Deal.objects.values('date', 'price').filter(category=categorySelected))
		rawData = json.dumps(rawData, default=datetime_handler).encode('utf8')
		return render(request, 'chart.html', \
		{"categorySelect":categorySelect, "data":rawData})
	else:
		rawData = list(Deal.objects.values('date', 'price'))
		rawData = json.dumps(rawData, default=datetime_handler).encode('utf8')
	return render(request, 'chart.html', \
		{"categorySelect":categorySelect, "data":rawData})

def generate_deal_data(request, data=None):
	if not data:
		data = list(Deal.objects.values('date', 'price'))
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

