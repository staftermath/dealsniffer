from django import forms

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
