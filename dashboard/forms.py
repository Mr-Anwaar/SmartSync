from .models import *
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter First Name'}))
    last_name = forms.CharField(
        required=False,
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Last Name'}))
    addressLine1 = forms.CharField(
        required=True,
        label='Address Line 1',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Address Line 1'}))
    addressLine2 = forms.CharField(
        required=False,
        label='Address Line 2',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Address Line 2 (Optional)'}))
    city = forms.CharField(
        required=True,
        label='City',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter City'}))
    province = forms.CharField(
        required=True,
        label='Province',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Province'}))
    country = forms.CharField(
        required=True,
        label='Country',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Country'}))
    postalCode = forms.CharField(
        required=True,
        label='Postal Code',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Postal Code'}))

    def __init__(self, *args, **kwargs):
        self.user=kwargs.pop('user')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(Column(Field('first_name', value =self.user.first_name), css_class='form-group col-md-6'),
                Column(Field('last_name', value =self.user.last_name), css_class='form-group col-md-6')),
            Row(Column('addressLine1', css_class='form-group col-md-6'),
                Column('addressLine2', css_class='form-group col-md-6')),
            Row(Column('city', css_class='form-group col-md-6'), Column('province', css_class='form-group col-md-6')),
            Row(Column('country', css_class='form-group col-md-6'),
                Column('postalCode', css_class='form-group col-md-6')),
            Submit('submit', 'Save Changes', css_class="btn btn-primary me-2")
        )

    class Meta:
        model = Profile
        fields = ['addressLine1', 'addressLine2', 'city', 'province', 'country', 'postalCode']

    # overloaded
    def save(self, *args, **kwargs):
        user = self.instance.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        profile = super(ProfileForm, self).save(*args, **kwargs)
        return profile


# Image uploader
class ProfileImageForm(forms.ModelForm):
    profileImage = forms.ImageField(
        required=True,
        label='Upload Profile Image',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['profileImage']
