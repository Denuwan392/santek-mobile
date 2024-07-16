# utils.py

import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from inventory.models import Item  # Replace 'your_app' with your actual Django app name

def import_items_from_text_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            # Split the line by tabs
            data = line.strip().split('\t')
            
            # Assuming the format: name, category, cost, retail_selling_price, etc.
            name = data[0]
            category = data[1]
            cost = float(data[2])
            retail_selling_price = float(data[3])
            retail_minimum_price = float(data[4])
            wholesale_selling_price = float(data[5])
            warranty = data[6]
            serial_number = data[7]
            
            # Create an instance of Item
            item = Item(
                name=name,
                category=category,
                cost=cost,
                retail_selling_price=retail_selling_price,
                retail_minimum_price=retail_minimum_price,
                wholesale_selling_price=wholesale_selling_price,
                warranty=warranty,
                serial_number=serial_number
            )
            item.save()  # Save the item to the database

# Example usage:
if __name__ == "__main__":
    file_path = 'Items_phones.txt'  # Replace with your actual file path
    import_items_from_text_file(file_path)
