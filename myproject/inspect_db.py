import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.db import connection

def inspect_table():
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE user_userprofile")
        rows = cursor.fetchall()
        with open('table_structure.txt', 'w') as f:
            f.write(f"{'Field':<25} | {'Type':<15} | {'Null':<5} | {'Key':<5} | {'Default':<10} | {'Extra':<15}\n")
            f.write("-" * 85 + "\n")
            for row in rows:
                f.write(f"{str(row[0]):<25} | {str(row[1]):<15} | {str(row[2]):<5} | {str(row[3]):<5} | {str(row[4]):<10} | {str(row[5]):<15}\n")

if __name__ == "__main__":
    inspect_table()
