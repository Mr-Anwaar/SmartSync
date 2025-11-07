from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from .models import *
import json

# Form Layout from Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class DateInput(forms.DateInput):
    input_type = 'date'


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['clientName', 'clientLogo', 'addressLine1', 'province', 'postalCode', 'phoneNumber', 'emailAddress',
                  'taxNumber']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'quantity', 'price', 'currency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True


class InvoiceForm(forms.ModelForm):
    THE_OPTIONS = [
        ('14 days', '14 days'),
        ('30 days', '30 days'),
        ('60 days', '60 days'),
    ]
    STATUS_OPTIONS = [
        ('CURRENT', 'CURRENT'),
        ('OVERDUE', 'OVERDUE'),
        ('PAID', 'PAID'),
    ]

    title = forms.CharField(
        required=True,
        label='Invoice Name or Title',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Invoice Title'}), )
    paymentTerms = forms.ChoiceField(
        choices=THE_OPTIONS,
        required=True,
        label='Select Payment Terms',
        widget=forms.Select(attrs={'class': 'form-control mb-3'}), )
    status = forms.ChoiceField(
        choices=STATUS_OPTIONS,
        required=True,
        label='Change Invoice Status',
        widget=forms.Select(attrs={'class': 'form-control mb-3'}), )
    notes = forms.CharField(
        required=True,
        label='Enter any notes for the client',
        widget=forms.Textarea(attrs={'class': 'form-control mb-3'}))

    dueDate = forms.DateField(
        required=True,
        label='Invoice Due',
        widget=DateInput(attrs={'class': 'form-control mb-3'}), )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-6'),
                Column('dueDate', css_class='form-group col-md-6'),
                css_class='form-row'),
            Row(
                Column('paymentTerms', css_class='form-group col-md-6'),
                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'),
            'notes',

            Submit('submit', ' SAVE INVOICE '))

    class Meta:
        model = Invoice
        fields = ['title', 'dueDate', 'paymentTerms', 'status', 'notes']


class ClientSelectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get the 'user' argument
        self.initial_client = kwargs.pop('initial_client')
        self.CLIENT_LIST = Client.objects.filter(user=user)  # Filter clients by the logged-in user
        self.CLIENT_CHOICES = [('-----', '--Select a Client--')]

        for client in self.CLIENT_LIST:
            d_t = (client.uniqueId, client.clientName)
            self.CLIENT_CHOICES.append(d_t)

        super(ClientSelectForm, self).__init__(*args, **kwargs)

        # Set the initial value for the 'client' field
        self.fields['client'] = forms.ChoiceField(
            label='Choose a related client',
            choices=self.CLIENT_CHOICES,
            widget=forms.Select(attrs={'class': 'form-control mb-3'}),
            initial=self.initial_client,  # Set initial value here
        )

    class Meta:
        model = Invoice
        fields = ['client']

    def clean_client(self):
        c_client = self.cleaned_data['client']
        if c_client == '-----':
            return self.initial_client
        else:
            return Client.objects.get(uniqueId=c_client)

from django import forms

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['clientName', 'clientLogo', 'addressLine1', 'province', 'postalCode', 'phoneNumber', 'emailAddress',
                  'taxNumber']  # Or specify the fields you want to include
        widgets = {
            'clientName': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'clientLogo': forms.ClearableFileInput(attrs={'required': True}),  # Make file input required
            'addressLine1': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'province': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'postalCode': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'phoneNumber': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'emailAddress': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'taxNumber': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }


# <input type="email" class="form-control" id="floatingInput" placeholder="name@example.com">
# <input type="password" class="form-control" id="floatingPassword" placeholder="Password">
