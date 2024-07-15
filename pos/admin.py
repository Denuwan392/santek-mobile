# pos_system/admin.py
from django.contrib import admin
from .models import Customer, Transaction, TransactionItem, ReturnItem, TransactionLog
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Customer)
class CustomerAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'email', 'phone',)
    search_fields = ('email', 'phone')


@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin):
    list_display = ('invoice_number', 'shop', 'seller', 'customer', 'transaction_date', 'total_amount', 'bill_discount', 'total_item_discount', 'total_discount')
    list_filter = ('transaction_date',)
    search_fields = ('invoice_number', 'customer__name')


@admin.register(TransactionItem)
class TransactionItemAdmin(SimpleHistoryAdmin):
    list_display = ('transaction', 'item', 'serial_number', 'quantity', 'price', 'item_discount')


@admin.register(TransactionLog)
class TransactionLogAdmin(SimpleHistoryAdmin):
    list_display = ('get_invoice_number', 'bank_account', 'cheque_number', 'cheque_date', 'payment_method', 'amount_paid', 'balance', 'total_paid')
    search_fields = ('transaction__invoice_number', 'payment_method')
    list_filter = ('payment_method',)

    def get_invoice_number(self, obj):
        return obj.transaction.invoice_number if obj.transaction else None

    get_invoice_number.short_description = 'Invoice Number'


@admin.register(ReturnItem)
class ReturnItemAdmin(SimpleHistoryAdmin):
    list_display = ('get_invoice_number', 'get_customer', 'get_seller', 'item', 'serial_number', 'condition', 'price',)

    def get_invoice_number(self, obj):
        return obj.transaction.invoice_number if obj.transaction else None

    get_invoice_number.short_description = 'Invoice Number'

    def get_seller(self, obj):
        return obj.transaction.seller if obj.transaction else None

    get_seller.short_description = 'Seller'

    def get_customer(self, obj):
        return obj.transaction.customer if obj.transaction else None

    get_customer.short_description = 'Customer'
