import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import FoodItem
from user.services.food_scan_service import FoodScanService

def main():
    service = FoodScanService()
    print("Testing _find_food_match('food')")
    m1 = service._find_food_match('food')
    if m1: print("MATCH for 'food':", m1.name)
    
    print("Testing _find_food_match('scan')")
    m2 = service._find_food_match('scan')
    if m2: print("MATCH for 'scan':", m2.name)
    
    print("Testing _find_food_match('apple')")
    m3 = service._find_food_match('apple')
    if m3: print("MATCH for 'apple':", m3.name)

if __name__ == '__main__':
    main()
