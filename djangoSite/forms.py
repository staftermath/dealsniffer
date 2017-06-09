from django import forms
from parsers.models import Category, Parser

class ContactForm(forms.Form):
    # TODO: Define form fields here
    subject = forms.CharField(max_length=100)
    email = forms.EmailField(required=False, \
    		label='Your e-mail address')
    message = forms.CharField(widget=forms.Textarea)

    def clean_message(self):
    	message = self.cleaned_data['message']
    	num_words = len(message.split())
    	if num_words < 4:
    		raise forms.ValidationError("Not enough words! Minimal 4")
    	return message

class SelectDeal(forms.Form):
    def __init__(self, dealName):
        self.dealName = dealName
        super(SelectDeal, self).__init__()
        self.fields['dealMenu'] = forms.ChoiceField(zip(self.dealName,self.dealName))

class SelectCategory(forms.Form):
    def __init__(self, brand, mainclass, subclass, item = None):
        self.brand = brand
        self.mainclass = mainclass
        self.subclass = subclass
        self.item = item
        super(SelectCategory, self).__init__()
        self.fields['brand'] = forms.ChoiceField(zip(self.brand,self.brand))
        self.fields['mainclass'] = forms.ChoiceField(zip(self.mainclass,self.mainclass))
        self.fields['subclass'] = forms.ChoiceField(zip(self.subclass,self.subclass))
        if self.item:
            self.fields['item'] = forms.ChoiceField(zip(self.item,self.item))

    def AddItem(self, item):
        if item:
            self.fields['item'] = forms.ChoiceField(zip(item,item))

class AddParser(forms.Form):
    name = forms.CharField(max_length=100,min_length=1)
    body = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 10}))
    url = forms.URLField()
    filename = forms.CharField(max_length=100,min_length=1)

class AddDeal(forms.Form):
    title = forms.CharField(max_length=100,min_length=1)
    website = forms.URLField()
    filename = forms.CharField(max_length=100,min_length=1)
    
    def addparser(self, parsers):
        self.fields['parser'] = forms.ChoiceField(zip(parsers, parsers))

class SelectParser(forms.Form):
    def __init__(self, choices = None):
        self.choices = choices
        super(SelectParser, self).__init__()
        if self.choices:
            self.fields['parser'] = forms.ChoiceField(zip(self.choices,self.choices))

    def AddItem(self, item):
        if item:
            self.fields['parser'] = forms.ChoiceField(zip(item,item))