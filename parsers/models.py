from django.db import models

# Create your models here.
class Parser(models.Model):
	name = models.CharField(max_length=100, unique=True)
	filepath = models.CharField(max_length=500, blank=True)
	
	def __str__(self):
		return self.name


class Category(models.Model):
	brand = models.CharField(max_length=50)
	mainclass = models.CharField(max_length=50)
	subclass = models.CharField(max_length=50)

	def __str__(self):
		return "%s -> %s || <Brand> %s" % (self.mainclass, \
										self.subclass, \
										self.brand)


class Deal(models.Model):
	title = models.CharField(max_length=100)
	category = models.ForeignKey(Category)
	website = models.URLField()
	parser = models.ForeignKey(Parser)
	
	def __str__(self):
		return self.title

class Price(models.Model):
	deal = models.ForeignKey(Deal)
	price = models.CharField(max_length=100)
	date = models.DateTimeField()

	def __str__(self):
		return "{2} on {0}: ${1}".format(self.date, self.price, self.deal)

