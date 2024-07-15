from django import forms
from .models import Phone

class PhoneConditionForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['condition']
        widgets = {
            'condition': forms.Select(choices=[
                ('brand new', 'Brand New'),
                ('used', 'Used'),
                ('faulty', 'Faulty')
            ])
        }

from django import forms
from .models import Phone

class PhoneSellerForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['salesman']
        widgets = {
            'salesman': forms.Select(attrs={'class': 'form-control'})
        }

# forms.py
from django import forms
from .models import Accessory, Seller

class AccessorySellerForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['seller']
        widgets = {
            'seller': forms.Select(attrs={'class': 'form-control'}),
        }


# forms.py

from django import forms
from .models import Seller, Shipment

class AccessoryAssociationForm(forms.Form):
    seller = forms.ModelChoiceField(queryset=Seller.objects.all(), empty_label="Select Seller")
    quantity = forms.IntegerField(min_value=1, initial=1)
    shipment = forms.ModelChoiceField(queryset=Shipment.objects.all(), empty_label="Select Shipment")

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

