# pos_system/forms.py
from django import forms
from .models import Transaction, TransactionItem, Customer
from inventory.models import Shop, Item

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['shop']

class TransactionItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), empty_label="Select Item", widget=forms.Select(attrs={'onchange': 'updatePrice();'}))

    class Meta:
        model = TransactionItem
        fields = ['item', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        super(TransactionItemForm, self).__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['readonly'] = True  # Make the price field read-only

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name',  'phone']


class TransactionUpdateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount_paid', 'payment_method', 'bill_discount']


# pos_system/forms.py
from django import forms

from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Start Date'
        }),
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'End Date'
        }),
        label="End Date"
    )



