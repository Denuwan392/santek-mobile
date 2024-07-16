from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_info = models.TextField()
    is_main_shop = models.BooleanField(default=False)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group_name = 'Main Shop' if self.is_main_shop else 'Small Sellers'
        group, created = Group.objects.get_or_create(name=group_name)
        self.user.groups.add(group)
        self.user.save()

    def __str__(self):
        return self.name

from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError

class Item(models.Model):
    category = models.CharField(max_length=20, choices=[
        ('Mobile Phones', 'Mobile Phones'),
        ('Accessories', 'Accessories'),
    ], default='Mobile Phones')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    retail_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    wholesale_minimum_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    wholesale_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    warranty = models.CharField(max_length=100,choices=[
        ('No Warranty', 'No Warranty'),
        ('1 Week', '1 Week'),
        ('2 Week', '2 Week'),
        ('1 Month', '1 Month'),
        ('2 Month', '2 Month'),
        ('6 Month', '6 Month'),
    ], default='No Warranty')
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.category.lower() == 'accessories' and not self.serial_number:
            raise ValidationError("Serial number is required for accessories.")
        super().save(*args, **kwargs)


class Shipment(models.Model):
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    shipment_date = models.DateField()
    history = HistoricalRecords()

    def __str__(self):
        return f"Shipment {self.id} on {self.shipment_date}"

class Phone(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    condition = models.CharField(max_length=100)
    retail_minimum_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    retail_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    wholesale_minimum_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    wholesale_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    salesman = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True)
    added_date = models.DateField(default=timezone.now)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.item.name} - {self.serial_number} - {self.condition}"

    def save(self, *args, **kwargs):
        if not self.pk:
            stock, created = Stock.objects.get_or_create(item=self.item)
            stock.quantity += 1
            stock.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            stock = Stock.objects.get(item=self.item)
            stock.quantity -= 1
            if stock.quantity < 0:
                stock.quantity = 0
            stock.save()
        except Stock.DoesNotExist:
            pass
        super().delete(*args, **kwargs)

@receiver(pre_delete, sender=Phone)
def reset_salesman(sender, instance, **kwargs):
    if instance.salesman is not None:
        instance.salesman = None
        instance.save()

class Accessory(models.Model):
    serial_number = models.CharField(max_length=100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    retail_minimum_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    retail_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    wholesale_minimum_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    wholesale_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    added_date = models.DateField(default=timezone.now)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.item.name} - {self.serial_number}"

    class Meta:
        unique_together = ('item', 'serial_number')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        update_stock_accessory(Accessory, self, created=False)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        delete_stock_accessory(Accessory, self)

class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"

    class Meta:
        db_table = 'inventory_stock'

@receiver(post_save, sender=Phone)
def update_stock_phone(sender, instance, created, **kwargs):
    stock, created = Stock.objects.get_or_create(item=instance.item)
    if created:
        stock.quantity = 1
    else:
        stock.quantity = Phone.objects.filter(item=instance.item).count()
    stock.save()

@receiver(post_delete, sender=Phone)
def delete_stock_phone(sender, instance, **kwargs):
    try:
        stock = Stock.objects.get(item=instance.item)
        stock.quantity = Phone.objects.filter(item=instance.item).count()
        stock.save()
    except Stock.DoesNotExist:
        pass

@receiver(post_save, sender=Accessory)
def update_stock_accessory(sender, instance, created, **kwargs):
    stock, created = Stock.objects.get_or_create(item=instance.item)
    stock.quantity = sum([acc.quantity for acc in Accessory.objects.filter(item=instance.item)])
    stock.save()

@receiver(post_delete, sender=Accessory)
def delete_stock_accessory(sender, instance, **kwargs):
    try:
        stock = Stock.objects.get(item=instance.item)
        stock.quantity = sum([acc.quantity for acc in Accessory.objects.filter(item=instance.item)])
        stock.save()
    except Stock.DoesNotExist:
        pass

class Shop(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class AccessoryAssociation(models.Model):
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='associations')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    serial_number = models.CharField(max_length=100, default='')
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.accessory.item.name} - {self.seller.name} - {self.quantity}"

    class Meta:
        unique_together = ('accessory', 'seller')
