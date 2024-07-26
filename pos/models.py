from django.db import models
from inventory.models import Item, Shop, Seller
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

class Customer(models.Model):
    name = models.CharField(max_length=255)
    
    phone = models.CharField(max_length=20, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Transaction(models.Model):
    invoice_number = models.CharField(max_length=12, unique=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='pos_transactions')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer')
    ], default='cash')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bill_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add bill_discount field
    total_item_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            date_str = now().strftime('%y%b').upper()
            prefix = f'NSA{date_str}'
            last_transaction = Transaction.objects.filter(invoice_number__startswith=prefix).order_by('invoice_number').last()
            if last_transaction:
                last_number = int(last_transaction.invoice_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.invoice_number = f'{prefix}{new_number:04d}'
        super(Transaction, self).save(*args, **kwargs)

    def calculate_total_amount(self):
        total_items_price = sum(item.total_price() for item in self.items.all())
        self.total_amount = total_items_price - self.bill_discount
        self.save()

    def __str__(self):
        return f'Purchased by {self.customer} by {self.seller}'

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    serial_number = models.CharField(max_length=255, default="UNKNOWN")
    item_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    history = HistoricalRecords()

    def total_price(self):
        return self.price * self.quantity

class TransactionLog(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='logs')
    payment_method = models.CharField(max_length=20)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    cheque_number = models.CharField(max_length=255, null=True, blank=True)
    cheque_date = models.DateField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'Payment of {self.amount_paid} using {self.payment_method} for transaction {self.transaction.invoice_number}'

class ReturnItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    salesman = models.ForeignKey(Seller, on_delete=models.CASCADE)
    return_date = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Return Item {self.id} for Transaction {self.transaction.id}"
