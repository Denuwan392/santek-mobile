from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Phone, Item
from django.http import HttpResponse
from .models import Item, Stock
from .models import Phone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from django.core.paginator import Paginator
from django.shortcuts import render


@login_required
def item_list(request):
    items = Item.objects.all()
    query = request.GET.get('q', '')  # Use empty string as default

    if query:
        items = items.filter(Q(name__icontains=query))

    paginator = Paginator(items, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    return render(request, 'inventory/item_list.html', {
        'page_obj': page_obj,
        'query': query
    })

@login_required
def stock_list(request):
    stocks = Stock.objects.all()
    query = request.GET.get('q', '')  # Use empty string as default

    if query:
        stocks = stocks.filter(Q(item__name__icontains=query))

    paginator = Paginator(stocks, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory/stock_list.html', {
        'page_obj': page_obj,
        'query': query  # Pass the query to the template
    })


@group_required('Stock Manager')
def add_phone(request):
    if request.method == 'POST':
        serial_number = request.POST['serial_number']
        item_id = request.POST['item']
        condition = request.POST['condition']

        if Phone.objects.filter(serial_number=serial_number).exists():
            messages.error(request, 'A phone with this serial number already exists.')
            return redirect('phone_list')


        item = Item.objects.get(id=item_id)

        phone = Phone(
            serial_number=serial_number,
            item=item,
            condition=condition,
            cost=item.cost,
            retail_selling_price=item.retail_selling_price,
            retail_minimum_price=item.retail_minimum_price,
            wholesale_selling_price=item.wholesale_selling_price,
        )
        phone.save()

        return redirect('phone_list')  # Adjust this accordingly


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Phone, Shipment, Item, Shop
from django.db.models import Q

from django.shortcuts import render
from django.utils import timezone
from .models import Phone
@group_required('Stock Manager')
def phone_list(request):
    phones = Phone.objects.all()
    shipments = Shipment.objects.all()

    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        phones = phones.filter(added_date__gte=start_date, added_date__lte=end_date)

    
    #phone_category = Category.objects.get(name='Mobile Phones')
    items = Item.objects.filter(category='Mobile Phones')

    context = {
        'phones': phones,
        'shipments': shipments,
        'items': items,  # Ensure items are passed to the context
    }
    return render(request, 'inventory/phone_list.html', context)

@group_required('Stock Manager')
def assign_shipment_number(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        shipment_id = request.POST.get('shipment_id')
        selected_phones = request.POST.getlist('phones')
        print("Shipment ID:", shipment_id)
        print("Selected Phones:", selected_phones)

        if not shipment_id:
            messages.error(request, 'Please provide a shipment.')
            return redirect('phone_list')

        if not selected_phones:
            messages.error(request, 'Please select at least one phone.')
            return redirect('phone_list')

        try:
            shipment = Shipment.objects.get(pk=shipment_id)
        except Shipment.DoesNotExist:
            messages.error(request, 'The selected shipment does not exist.')
            return redirect('phone_list')

        phones = Phone.objects.filter(pk__in=selected_phones)
        for phone in phones:
            phone.shipment = shipment
            phone.save()

        messages.success(request, f'Shipment "{shipment}" assigned to selected phones successfully.')
        return redirect('phone_list')

    return redirect('phone_list')



from django.shortcuts import render, get_object_or_404, redirect
from .models import Phone
from .forms import PhoneConditionForm
@group_required('Stock Manager')
def edit_phone_condition(request, pk):
    phone = get_object_or_404(Phone, pk=pk)
    
    if request.method == 'POST':
        form = PhoneConditionForm(request.POST, instance=phone)
        if form.is_valid():
            form.save()
            return redirect('phone_list')  # Assuming 'phone_list' is the name of the view displaying the list of phones
    else:
        form = PhoneConditionForm(instance=phone)
    
    return render(request, 'inventory/edit_phone_condition.html', {'form': form, 'phone': phone})


from django.shortcuts import render, redirect
from .models import Phone, Seller
from django.db.models import Q

@group_required('Stock Manager')
def phone_associate_seller(request):
    query = request.GET.get('q')
    if query:
        phones = Phone.objects.filter(Q(serial_number__icontains=query))
    else:
        phones = Phone.objects.all()
        
    sellers = Seller.objects.all()  # Retrieve all sellers

    if request.method == 'POST':
        # Handle form submission to associate sellers with serial numbers
        for phone in phones:
            seller_id = request.POST.get(f"seller_{phone.id}")  # Get selected seller ID from the form
            if seller_id:
                seller = Seller.objects.get(id=seller_id)
                phone.salesman = seller  # Associate the phone with the selected seller
                phone.save()  # Save the changes

        return redirect('phone_associate_seller')  # Redirect back to the same page after processing the form

    return render(request, 'inventory/phone_association.html', {'phones': phones, 'sellers': sellers})







from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item, Accessory, Category, Shipment
from .decorators import group_required  # Assuming you have a custom decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item, Accessory, Category, Shipment
from .decorators import group_required  # Assuming you have a custom decorator

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item, Accessory, Category
from .decorators import group_required

@group_required('Stock Manager')
def add_accessory(request):
    #accessories_category = get_object_or_404(Category, name='Accessories')
    
    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')

        # Fetch the item and its price
        item = get_object_or_404(Item, id=item_id, category='Accessories')
        serial_number = item.serial_number
        cost=item.cost,
        retail_selling_price=item.retail_selling_price,
        retail_minimum_price=item.retail_minimum_price,
        wholesale_selling_price=item.wholesale_selling_price,

        # Create or update the Accessory
        accessory, created = Accessory.objects.get_or_create(
            serial_number=serial_number,
            item=item,
            defaults={'quantity': quantity}  # Default values can be adjusted
        )

        if not created:
            accessory.quantity += int(quantity)
            accessory.save()

        messages.success(request, 'Accessory added successfully.')
        return redirect('add_accessory')

    items = Item.objects.filter(category='Accessories')
    accessories = Accessory.objects.filter(item__category='Accessories')
    return render(request, 'inventory/add_accessory.html', {'items': items, 'accessories': accessories})


@group_required('Stock Manager')
def accessory_list(request):
    accessories = Accessory.objects.all()
    return render(request, 'inventory/accessory_list.html', {'accessories': accessories})

# inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from .models import Accessory, Seller, Shipment, AccessoryAssociation
from .decorators import group_required  # Assuming you have a decorator for group permissions

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .models import Accessory, Seller, AccessoryAssociation

@login_required
@group_required('Stock Manager')
def accessory_associate_seller(request):
    if request.method == "POST":
        seller_id = request.POST.get('seller')
        serial_number = request.POST.get('serial_number')
        quantity = int(request.POST.get('quantity'))
        
        seller = get_object_or_404(Seller, id=seller_id)
        
        # Filter accessories by serial_number (assuming serial_number is not unique)
        accessories = Accessory.objects.filter(serial_number=serial_number)
        
        # Handle case where no accessory is found
        if not accessories.exists():
            return HttpResponseBadRequest("Accessory not found.")

        # Iterate over filtered accessories and select the first one
        # You may need additional logic to select the appropriate accessory
        accessory = accessories.first()

        # Check if the quantity can be subtracted from stock
        if accessory.quantity < quantity:
            return HttpResponseBadRequest("Insufficient stock.")
        
        # Subtract the quantity from accessory stock
        accessory.quantity -= quantity
        accessory.save()

        # Check if there is already an association with this seller
        association = AccessoryAssociation.objects.filter(accessory=accessory, seller=seller, serial_number=serial_number).first()

        if association:
            # Update existing association quantity
            association.quantity += quantity
            association.save()
        else:
            # Create a new association
            accessory_association = AccessoryAssociation.objects.create(
                accessory=accessory,
                seller=seller,
                quantity=quantity,
                serial_number=serial_number
            )
        
        return redirect('accessory_associate_seller')
    
    accessories = Accessory.objects.all()
    sellers = Seller.objects.all()
    associations = AccessoryAssociation.objects.all()
    return render(request, 'inventory/accessory_association.html', {
        'accessories': accessories,
        'sellers': sellers,
        'associations': associations
    })






from django.shortcuts import render, get_object_or_404
from .models import Seller, Phone, Accessory
@group_required('Stock Manager')
def seller_profile(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    phones = Phone.objects.filter(salesman=seller)
    accessory_associations = AccessoryAssociation.objects.filter(seller=seller)
    accessories = [association.accessory for association in accessory_associations]

    context = {
        'seller': seller,
        'phones': phones,
        'accessories': accessories,
        'accessory_associations': accessory_associations,
    }
    return render(request, 'inventory/seller_profile.html', context)


from django.shortcuts import render
from .models import Seller

def seller_list(request):
    sellers = Seller.objects.all()
    context = {
        'sellers': sellers,
    }
    return render(request, 'inventory/seller_list.html', context)


from django.shortcuts import get_object_or_404, redirect
from .models import AccessoryAssociation, Accessory
@group_required('Stock Manager')
def remove_item(request, association_id):
    # Get the association object
    association = get_object_or_404(AccessoryAssociation, id=association_id)
    
    # Restore the quantity to the accessory stock
    accessory = association.accessory
    accessory.quantity += association.quantity
    accessory.save()
    
    # Delete the association
    association.delete()
    
    return redirect('seller_profile', seller_id=association.seller.id)




from django.shortcuts import get_object_or_404, redirect
from .models import Phone

from django.shortcuts import render, redirect, get_object_or_404
from .models import Phone, Accessory, Seller
@group_required('Stock Manager')
def remove_phone(request, phone_id):
    phone = get_object_or_404(Phone, id=phone_id)
    seller_id=phone.salesman.id
    
    # Remove the seller association from the phone
    phone.salesman = None
    phone.save()
    
    # Optionally, mark the phone as available again or handle any other logic
    phone.available = True
    phone.save()

    # Redirect to the seller profile if salesman exists, else to a default view
    
    return redirect('seller_profile', seller_id)
     # Replace 'default_view' with your desired fallback URL








# views.py

import os
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from io import BytesIO
from .models import Phone, Shipment

import os
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from io import BytesIO
from .models import Phone, Shipment

def group_required(group_name):
    def decorator(view_func):
        @user_passes_test(lambda u: u.is_authenticated and u.groups.filter(name=group_name).exists())
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

from django.shortcuts import render
from .models import Phone, Shipment

@group_required('Stock Manager')
def generate_barcode(request):
    if request.method == 'POST':
        selected_shipment_id = request.POST.get('shipment_id')

        if not selected_shipment_id:
            return HttpResponseBadRequest("Invalid request parameters")

        # Fetch all phones associated with the selected shipment
        phones = Phone.objects.filter(shipment_id=selected_shipment_id)

        # Pass phones data to the template
        context = {
            'phones': phones,
            'selected_shipment_id': selected_shipment_id,
        }
        return render(request, 'inventory/generate_barcode.html', context)

    # If GET request or invalid POST request, render shipment selection form
    shipments = Shipment.objects.all()
    context = {
        'shipments': shipments,
    }
    return render(request, 'inventory/select_shipment.html', context)





from django.shortcuts import render

@group_required('Stock Manager')
def show_barcodes(request):
    barcode_paths = request.session.get('barcode_paths', [])
    context = {
        'barcode_paths': barcode_paths,
        
    }
    barcode_paths = [
        '/media/barcodes/2/Phone_5454448484.png',
        '/media/barcodes/2/Phone_5r56f797y.png',
        '/media/barcodes/2/Phone_576730494rt.png',
    ]
    return render(request, 'inventory/show_barcodes.html', context)



from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from io import BytesIO


@group_required('Stock Manager')
def generate_single_barcode(request, accessory_id):
    accessory = get_object_or_404(Accessory, id=accessory_id)
    
    

    # Pass phones data to the template
    context = {
        'accessory': accessory,
    }
    return render(request, 'inventory/generate_accessory_barcode.html', context)


@group_required('Stock Manager')
def generate_single_phone_barcode(request, phone_id):
    phone = get_object_or_404(Phone, id=phone_id)
    
    

    # Pass phones data to the template
    context = {
        'phone': phone,
    }
    return render(request, 'inventory/generate_phone_barcode.html', context)


