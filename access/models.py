from django.db import models
from django.contrib.auth.models import User
from parsers.models import Deal

# Create your models here.
class DealAccess(models.Model):
	user = models.ForeignKey(User)
	deal = models.ForeignKey(Deal)
	text = models.CharField(max_length=200, blank=True)
	def __str__(self):
		return self.deal.title
