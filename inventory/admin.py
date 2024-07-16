from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Category, Seller, Item, Shipment, Phone, Stock, Shop, Accessory, AccessoryAssociation

class ShipmentAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'shop', 'quantity', 'shipment_date')
    search_fields = ('shop__name',)
    list_filter = ('shipment_date', 'shop')

class CategoryAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description')

class SellerAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'contact_info', 'is_main_shop')

class ItemAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'category', 'cost', 'retail_selling_price', 'wholesale_minimum_price', 'wholesale_selling_price', 'warranty', 'serial_number')

class PhoneAdmin(SimpleHistoryAdmin):
    list_display = ('serial_number', 'item', 'condition', 'salesman', 'shipment')
    search_fields = ('serial_number', 'item__name')
    list_filter = ('condition', 'shipment')

class StockAdmin(SimpleHistoryAdmin):
    list_display = ('item', 'quantity')

class ShopAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'address')

class AccessoryAdmin(SimpleHistoryAdmin):
    list_display = ('serial_number', 'item', 'quantity', )
    search_fields = ('serial_number', 'item__name')
    list_filter = ('item', 'quantity', )

class AccessoryAssociationAdmin(SimpleHistoryAdmin):
    list_display = ('accessory', 'seller', 'serial_number','quantity', 'shipment')
    search_fields = ('accessory__item__name', 'seller__name')
    list_filter = ('seller', 'shipment')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Phone, PhoneAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(AccessoryAssociation, AccessoryAssociationAdmin)
