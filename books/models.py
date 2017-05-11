from django.db import models

# Create your models here.

class BookManager(models.Manager):
	"""docstring for BookManager"""
	def title_count(self, keyword):
		return self.filter(title__icontains=keyword).count()
		

class Publisher(models.Model):
	name = models.CharField(max_length=30)
	address = models.CharField(max_length=30)
	city = models.CharField(max_length=60)
	state_province = models.CharField(max_length=30)
	country = models.CharField(max_length=50)
	website = models.URLField()

	class Meta:
		ordering = ["-name"]

	def __str__(self):
		return self.name


class Author(models.Model):
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=40)
	email = models.EmailField(blank=True)

	def __str__(self):
		return u'%s %s' % (self.first_name, 
			self.last_name)


class Book(models.Model):
	title = models.CharField(max_length=100)
	authors = models.ManyToManyField(Author)
	publisher = models.ForeignKey(Publisher)
	publication_date = models.DateField(blank=True,
										null=True)
	num_pages = models.IntegerField(blank=True, null=True)
	objects = BookManager()
	

	def __str__(self):
		return self.title