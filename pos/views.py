

# Create your views here.
# pos_system/views.py

from django.contrib.auth.decorators import login_required

@login_required
def pos_dashboard(request):
    return render(request, 'pos_system/dashboard.html')


'''
# pos_system/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, TransactionItem, Customer
from inventory.models import Item
from .forms import TransactionForm, TransactionItemForm, CustomerForm, TransactionUpdateForm

#@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            return redirect('pos_system:transaction_detail', pk=transaction.pk)
    else:
        form = TransactionForm()
    return render(request, 'pos_system/create_transaction.html', {'form': form})
'''



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, TransactionItem, Customer
from inventory.models import Item
from .forms import TransactionForm, CustomerForm


from django import forms
from django.shortcuts import render, redirect
from .models import Transaction, Customer
@login_required
def create_transaction(request):
    class CustomTransactionForm(forms.ModelForm):
        class Meta:
            model = Transaction
            fields = ['shop']
            widgets = {
                'shop': forms.Select(attrs={'class': 'form-control'}),
            }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set default shop value here
            self.fields['shop'].initial = 1  # Replace default_shop_id with your default shop's ID

    class CustomCustomerForm(forms.ModelForm):
        class Meta:
            model = Customer
            fields = ['name', 'email', 'phone']
            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'phone': forms.TextInput(attrs={'class': 'form-control'}),
            }

    if request.method == 'POST':
        transaction_form = CustomTransactionForm(request.POST)
        customer_form = CustomCustomerForm(request.POST)
        
        if customer_form.is_valid():
            customer = customer_form.save()
        else:
            customer = None

        if transaction_form.is_valid() and customer:
            transaction_instance = transaction_form.save(commit=False)
            transaction_instance.customer = customer
            transaction_instance.seller = request.user.seller  # Set the seller to the logged-in user
            transaction_instance.save()
            return redirect('pos_system:transaction_detail', pk=transaction_instance.pk)
    else:
        transaction_form = CustomTransactionForm()
        customer_form = CustomCustomerForm()

    return render(request, 'pos_system/create_transaction.html', {
        'transaction_form': transaction_form,
        'customer_form': customer_form
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Transaction, TransactionItem
from inventory.models import Item, Stock, Phone, AccessoryAssociation  # Import AccessoryAssociation model

@login_required
def add_transaction_item(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    items = Item.objects.all()  # Fetch all items from the inventory
    
    # Get the associated seller for the current user
    seller = request.user.seller
    
    # Filter phones based on the associated seller
    phones = Phone.objects.filter(salesman=seller)

    # Filter accessory associations based on the associated seller
    accessory_associations = AccessoryAssociation.objects.filter(seller=seller)

    # Create a dictionary mapping item ID to its serial numbers for phones
    item_serial_map = {
        item.id: [phone.serial_number for phone in phones if phone.item_id == item.id]
        for item in items
    }

    # Create a dictionary mapping item ID to its serial numbers for accessories
    accessory_serial_map = {
        item.id: [association.accessory.serial_number for association in accessory_associations if association.accessory.item_id == item.id]
        for item in items
    }
    
    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity = int(request.POST.get('quantity', 1))
        serial_number = request.POST.get('serial_number')
        item = get_object_or_404(Item, id=item_id)
        price = item.retail_selling_price
        stock = get_object_or_404(Stock, item=item.id)
        stock.save()

        if item.category == 'Accessories':
            accessory_association = get_object_or_404(AccessoryAssociation, serial_number=serial_number, seller=seller)
            accessory_association.quantity -= quantity
            accessory_association.save()
        else:
            phone = get_object_or_404(Phone, serial_number=serial_number, salesman=seller)
            phone.delete()

        transaction_item = TransactionItem(transaction=transaction, item=item, quantity=quantity, serial_number=serial_number, price=price)
        transaction_item.save()
        
        return redirect('pos_system:transaction_detail', pk=pk)
    
    return render(request, 'pos_system/add_transaction_item.html', {
        'transaction': transaction,
        'items': items,
        'item_serial_map': item_serial_map,
        'accessory_serial_map': accessory_serial_map,  # Pass the accessory serial numbers mapping to the template
    })



from django.shortcuts import render, redirect, get_object_or_404
from .models import TransactionItem, ReturnItem
from inventory.models import Phone, Stock
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


@login_required
def remove_transaction_item(request, item_id):
    transaction_item = get_object_or_404(TransactionItem, id=item_id)
    transaction = transaction_item.transaction

    item = transaction_item.item
    serial_number = transaction_item.serial_number
    quantity = transaction_item.quantity
    price = transaction_item.price

    if request.user.groups.filter(name='Main Shop').exists():
        # Main Shop User logic
        condition = request.POST.get(f'condition_{item_id}')
        seller = request.user.seller

        if item.category.lower() == 'mobile phones':
            # Restore the phone back to the Phone table with selected condition and salesman
            Phone.objects.create(
                serial_number=serial_number,
                item=item,
                condition=condition,
                price=price,
                salesman=seller,
            )

            # Update the stock quantity
            stock = get_object_or_404(Stock, item=item)
            stock.quantity += quantity
            stock.save()

            # Check if the return item checkbox is checked (only available for Main Shop users)
            if 'return_item' in request.POST:
                # Add a record to the ReturnItem table
                ReturnItem.objects.create(
                    transaction=transaction,
                    item=item,
                    serial_number=serial_number,
                    condition=condition,
                    price=price,
                    salesman=seller,
                )

        elif item.category.lower() == 'accessories':
            # Accessory logic
            # Create or update AccessoryAssociation
            association, created = AccessoryAssociation.objects.get_or_create(
                accessory__item=item,
                seller=seller,
                serial_number=serial_number,
                defaults={
                    'quantity': quantity,
                    'shipment': None,  # Adjust as per your shipment logic
                }
            )

            if not created:
                association.quantity += quantity
                association.save()

            # Update the stock quantity if needed (adjust as per your logic)
            stock = get_object_or_404(Stock, item=item)
            stock.quantity += quantity
            stock.save()

    else:
        # Non Main Shop User logic
        # Restore the phone back to the Phone table with default condition and salesman
        if item.category.lower() == 'mobile phones':
            Phone.objects.create(
                serial_number=serial_number,
                item=item,
                condition=request.POST.get(f'condition_{item_id}'),  # Replace with appropriate default value
                price=price,
                salesman=request.user.seller,
            )

            # Update the stock quantity
            stock = get_object_or_404(Stock, item=item)
            stock.quantity += quantity
            stock.save()

        elif item.category.name.lower() == 'accessories':
            # Accessory logic
            seller = request.user.seller

            # Create or update AccessoryAssociation
            association, created = AccessoryAssociation.objects.get_or_create(
                accessory__item=item,
                seller=seller,
                serial_number=serial_number,
                defaults={
                    'quantity': quantity,
                     # Adjust as per your shipment logic
                }
            )

            if not created:
                association.quantity += quantity
                association.save()

            # Update the stock quantity if needed (adjust as per your logic)
            stock = get_object_or_404(Stock, item=item)
            stock.quantity += quantity
            stock.save()

    # Delete the transaction item
    transaction_item.delete()

    return redirect('pos_system:transaction_detail', pk=transaction.pk)



from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import TransactionItem

@require_POST
def add_item_discount(request, item_id):
    item = get_object_or_404(TransactionItem, id=item_id)
    discount = request.POST.get('item_discount')
    
    if discount is not None:
        item.item_discount = discount
        item.save()

    return redirect('pos_system:transaction_detail', pk=item.transaction.id)


    
















from decimal import Decimal
from .models import Transaction, TransactionLog
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST  # Import require_POST decorator
from .forms import TransactionUpdateForm

from decimal import Decimal
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse



def calculate_transaction_totals(transaction):
    items = transaction.items.all()
    total_items_price = sum(item.quantity * item.retail_selling_price for item in items)
    
    # Calculate total discount applied to all items
    total_item_discount = sum(item.item_discount for item in items) 
    total_discount = total_item_discount + transaction.bill_discount
    
    
    # Calculate total amount after discount
    total_amount = total_items_price   # Adjusted total amount
    amount_paid = sum(log.amount_paid for log in transaction.logs.all())
    balance = total_amount - amount_paid - total_discount 

    transaction.total_amount = total_amount
    transaction.amount_paid = amount_paid
    transaction.balance = balance
    transaction.total_item_discount = total_item_discount
    transaction.total_discount = total_discount
    transaction.save(update_fields=['total_amount', 'amount_paid', 'balance', 'total_item_discount', 'total_discount'])


    return items, total_items_price, total_discount, balance

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    items, total_amount, total_discount, balance = calculate_transaction_totals(transaction)

    is_main_shop_user = request.user.groups.filter(name='Main Shop').exists()

    if request.method == 'POST':
        form = TransactionUpdateForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('pos_system:transaction_detail', pk=transaction.pk)
    else:
        form = TransactionUpdateForm(instance=transaction)
    
    return render(request, 'pos_system/transaction_detail.html', {
        'transaction': transaction,
        'items': items,
        'total_amount': total_amount,  # Use total_items_price here
        'total_discount': total_discount,  # Pass total discount to the template
        'form': form,
        'balance': balance,
        'is_main_shop_user': is_main_shop_user,
    })





@login_required
@require_POST
def add_transaction_log(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    payment_method = request.POST.get('payment_method')
    amount_paid_str = request.POST.get('amount_paid')  # Get amount_paid as string
    amount_paid = Decimal(amount_paid_str)  # Convert amount_paid to Decimal
    bill_discount_str = request.POST.get('bill_discount', '0')  # Get bill_discount from form or default to '0'
    bill_discount = Decimal(bill_discount_str)  # Convert bill_discount to Decimal
    
    try:
        # Update transaction with bill_discount
        transaction.bill_discount = bill_discount
        transaction.save(update_fields=['bill_discount'])
        
        # Recalculate transaction totals with the original total amount
        items, total_items_price, total_discount, balance = calculate_transaction_totals(transaction)
        
        # Calculate balance and total paid amount
        total_paid = sum(log.amount_paid for log in transaction.logs.all()) + amount_paid
        balance = transaction.total_amount - total_paid
        
        # Create and save the transaction log
        log = TransactionLog(
            transaction=transaction,
            payment_method=payment_method,
            amount_paid=amount_paid,  # Save amount_paid as Decimal
            balance=balance,  # Adjust balance for the new payment
            total_paid=total_paid  # Update total paid amount
        )
    
        # Update account details based on payment method
        if payment_method == 'bank_transfer':
            bank_account = request.POST.get('bank_account')
            log.bank_account = bank_account
        elif payment_method == 'cheque':
            cheque_number = request.POST.get('cheque_number')
            cheque_date = request.POST.get('cheque_date')
            log.cheque_number = cheque_number
            log.cheque_date = cheque_date
        
        log.save()
        
        # Recalculate transaction totals to update the balance correctly
        calculate_transaction_totals(transaction)
        
        messages.success(request, 'Payment added successfully.')
    
    except Exception as e:
        messages.error(request, f'Failed to add payment: {str(e)}')
    
    return HttpResponseRedirect(reverse('pos_system:transaction_detail', args=[pk]))



from django.shortcuts import render, get_object_or_404
from .models import Transaction

def receipt_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    items, total_amount, total_discount, balance = calculate_transaction_totals(transaction)
    return render(request, 'pos_system/receipt.html', {
        'transaction': transaction,
        'items': items,
        'total_amount': total_amount,
        'total_discount': total_discount,
        'balance': balance,
    })




















from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from django.db.models import Q
# pos_system/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import DateRangeForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def transaction_report(request):
    user = request.user
    transactions = Transaction.objects.filter(seller=user.seller)  # Assuming user has a seller attribute

    query = request.GET.get('q', '')  # Use empty string as default

    if query:
        transactions = transactions.filter(Q(invoice_number__icontains=query))

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            transactions = transactions.filter(transaction_date__range=[start_date, end_date])
    else:
        form = DateRangeForm()

    return render(request, 'pos_system/transaction_report.html', {
        'transactions': transactions,
        'query': query,
        'form': form
    })




# pos_system/views.py
from django.db.models import Sum, Count, Avg

@login_required
def sales_summary_report(request):
    transactions = Transaction.objects.all()
    summary = transactions.aggregate(
        total_sales=Sum('total_amount'),
        total_transactions=Count('id'),
        average_transaction=Avg('total_amount')
    )

    return render(request, 'pos_system/sales_summary_report.html', {
        'summary': summary,
    })


# pos_system/views.py
from django.db.models import Sum
from django.utils.timezone import localdate
from .forms import DateRangeForm
from django.http import JsonResponse

@login_required
def daily_sales_report(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        else:
            start_date = localdate()
            end_date = localdate()
    else:
        form = DateRangeForm()
        start_date = localdate()
        end_date = localdate()

    sales = Transaction.objects.filter(transaction_date__date__range=[start_date, end_date])
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'pos_system/daily_sales_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'form': form
    })


# pos_system/views.py
from django.db.models import F

@login_required

def customer_debt_report(request):
    customers = Customer.objects.annotate(total_debt=Sum('transaction__balance'))
    return render(request, 'pos_system/customer_debt_report.html', {
        'customers': customers,
    })


# pos_system/views.py
from django.db.models import Count

@login_required
def sold_item_report(request):
    sold_items = TransactionItem.objects.values('item__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')
    return render(request, 'pos_system/sold_item_report.html', {
        'sold_items': sold_items,
    })


from django.shortcuts import render, get_object_or_404
from .models import Customer

from django.db.models import Sum

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    total_debt = customer.transaction_set.aggregate(total_debt=Sum('balance'))['total_debt'] or 0
    return render(request, 'pos_system/customer_detail.html', {'customer': customer, 'total_debt': total_debt})






@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'pos_system/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos_system:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'pos_system/customer_form.html', {'form': form})

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('pos_system:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'pos_system/customer_form.html', {'form': form})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('pos_system:customer_list')
    return render(request, 'pos_system/customer_confirm_delete.html', {'customer': customer})



# views.py

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page, such as a dashboard
            return redirect('pos_dashboard')
        else:
            # Return an error message if authentication fails
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


