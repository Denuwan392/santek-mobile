@group_required('Stock Manager')
def add_phone(request):
    if request.method == 'POST':
        serial_number = request.POST['serial_number']
        item_name = request.POST['item']  # Changed to get the item name
        condition = request.POST['condition']

        if Phone.objects.filter(serial_number=serial_number).exists():
            messages.error(request, 'A phone with this serial number already exists.')
            return redirect('phone_list')

        # Retrieve the item based on the name
        try:
            item = Item.objects.get(name=item_name)
        except Item.DoesNotExist:
            messages.error(request, 'The selected item does not exist.')
            return redirect('phone_list')

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

        return redirect('phone_list')

    # If GET request, render the add phone form
    items = Item.objects.all()
    shipments = Shipment.objects.all()
    return render(request, 'inventory/phone_list.html', {'items': items, 'shipments': shipments})
