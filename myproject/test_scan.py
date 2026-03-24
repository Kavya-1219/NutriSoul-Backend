import os
import django
import sys
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.services.food_scan_service import FoodScanService

def main():
    service = FoodScanService()
    
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    img_byte_arr.name = "food_scan.jpg"
    
    with open("scan_results.txt", "w") as f:
        f.write("Test 1: 'Fruit, Apple, Snack'\n")
        res1, msg1 = service.scan_food(img_byte_arr, "Fruit, Apple, Snack")
        f.write(str(res1) + "\n" + str(msg1) + "\n\n")
        
        img_byte_arr.seek(0)
        f.write("Test 2: 'Dessert, Plate, Sweet'\n")
        res2, msg2 = service.scan_food(img_byte_arr, "Dessert, Plate, Sweet")
        f.write(str(res2) + "\n" + str(msg2) + "\n\n")
        
        img_byte_arr.seek(0)
        f.write("Test 3: 'UnknownThing, Utensil'\n")
        res3, msg3 = service.scan_food(img_byte_arr, "UnknownThing, Utensil")
        f.write(str(res3) + "\n" + str(msg3) + "\n\n")

if __name__ == '__main__':
    main()
