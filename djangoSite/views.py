from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django import forms
from .forms import ContactForm, SelectDeal
import datetime
import pytz
import json
import calendar
from books.models import Book, Publisher
from parsers.models import Deal


def index(request):
	return render(request, 'index.html')

# def chart(request):
# 	dealName = list(Deal.objects.values_list('title', flat=True).distinct())
# 	selectDeal = SelectDeal(dealName)
# 	rawData = list(Deal.objects.values_list('date', 'price'))
# 	# rawData = [(x1, x2) for (x1, x2) in rawData]
# 	convertedData = {'date':[(x[0]-datetime.datetime(1970,1,1,tzinfo=pytz.UTC)).total_seconds()*1000 \
# 						for x in rawData],
# 					'price':[float(x[1]) for x in rawData]}
# 	# convertedData = serialize('json', Deal.objects.all(), \
# 	# 								cls=DjangoJSONEncoder, \
# 	# 								fields=('date', 'price'))
# 	chartcontainer = 'linechart_container'
# 	data = {
# 	'charttype': 'lineChart',
# 	'chartdata': {'x':convertedData['date'],
# 				  'y':convertedData['price'],
# 				  'name': 'Deal Price'},
# 	'chartcontainer': chartcontainer,
# 	'extra': {
# 		'x_is_date': True,
# 		'x_axis_format': '%m/%d %H:%M:%S',
# 		'tag_script_js': True,
# 		'jquery_on_ready': False,
# 		'y_axis_format': ".2f",
# 		'y_axis_scale_min': 0,
# 	}
# 	}

# 	return render(request, 'chart.html', data, selectDeal)	

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
	dealName = list(Deal.objects.values_list('title', flat=True).distinct())
	selectDeal = SelectDeal(dealName)
	return render(request, 'chart.html', \
		{"selectDeal":selectDeal})

def generate_deal_data(request):
	rawData = list(Deal.objects.values('date', 'price'))
	# print(rawData)
	return JsonResponse(rawData, safe=False)

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

