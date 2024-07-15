from django.core.management.base import BaseCommand
from pos_system.models import Transaction
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Update invoice numbers to ensure uniqueness'

    def handle(self, *args, **kwargs):
        transactions = Transaction.objects.all()
        for transaction in transactions:
            # Generate a new unique invoice number
            date_str = now().strftime('%y%b').upper()  # e.g., '24JUN'
            prefix = f'NSA{date_str}'
            last_transaction = Transaction.objects.filter(invoice_number__startswith=prefix).order_by('invoice_number').last()
            if last_transaction:
                last_number = int(last_transaction.invoice_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            transaction.invoice_number = f'{prefix}{new_number:04d}'  # e.g., 'NSA24JUN0001'
            transaction.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Transaction ID {transaction.id} with invoice number {transaction.invoice_number}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated all invoice numbers'))
