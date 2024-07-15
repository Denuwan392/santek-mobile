from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import generate_barcode

urlpatterns = [
    path('items/', views.item_list, name='item_list'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('phones/add/', views.add_phone, name='add_phone'),
    path('phones/', views.phone_list, name='phone_list'),
    path('phones/<int:pk>/edit-condition/', views.edit_phone_condition, name='edit_phone_condition'),
    path('phones/phone_associate_seller/', views.phone_associate_seller, name='phone_associate_seller'),
    path('accessories/', views.add_accessory, name='add_accessory'),
    #path('accessories/<int:pk>/edit/', views.edit_accessory, name='edit_accessory'),
    # urls.py
    path('inventory/accessory/associate_seller/<int:accessory_id>/', views.accessory_associate_seller, name='accessory_associate_seller'),
    #path('shipment/<int:shipment_id>/barcodes/', views.generate_barcode, name='generate_barcodes'),

    path('accessories/list/', views.accessory_list, name='accessory_list'),  # Add this line
    path('assign_shipment_number/', views.assign_shipment_number, name='assign_shipment_number'),
    #path('select_shipment/', views.select_shipment, name='select_shipment'),
    #path('generate_barcodes/', views.generate_barcodes, name='generate_barcodes'),  
    path('accessory/associate_seller/', views.accessory_associate_seller, name='accessory_associate_seller'),
    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),
    path('sellers/', views.seller_list, name='seller_list'),
    path('remove_accessory_association/<int:association_id>/', views.remove_item, name='remove_accessory_association'),
    path('remove_phone/<int:phone_id>/', views.remove_phone, name='remove_phone'),

    path('select_shipment/', views.generate_barcode, name='select_shipment'),

    #path('accessories/print/<int:accessory_id>/', views.print_single_barcode, name='print_single_barcode'),
    path('generate_barcode/', views.generate_barcode, name='generate_barcode'),
    path('show_barcodes/', views.show_barcodes, name='show_barcodes'),
    path('accessories/generate_accessory_barcode/<int:accessory_id>/', views.generate_single_barcode, name='generate_single_barcode'),
    path('accessories/generate_phone_barcode/<int:phone_id>/', views.generate_single_phone_barcode, name='generate_single_phone_barcode'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)