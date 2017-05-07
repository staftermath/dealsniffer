from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from .forms import ContactForm
import datetime
from books.models import Book, Publisher

def index(request):
	return render(request, 'index.html')

def profile(request):
	return render(request, 'profile.html')

def logout_user(request):
	logout(request)
	return render(request, 'log_out.html')

# def search_form(request):
#     return render(request, 'search_form.html')

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

