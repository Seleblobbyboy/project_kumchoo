import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from stadium.models import Field

fields_data = [
    {"name": "สนาม 1", "description": "สนามหญ้าเทียม (ฟุตบอล 7 คน) - เหมาะสำหรับการแข่งกระชับมิตร", "price_per_hour": 800},
    {"name": "สนาม 2", "description": "สนามหญ้าเทียม (ฟุตบอล 7 คน) - มีที่นั่งเชียร์", "price_per_hour": 800},
    {"name": "สนาม 3", "description": "สนามหญ้าจริง (ฟุตบอล 11 คน) - ขนาดมาตรฐานสำหรับการแข่งขัน", "price_per_hour": 1500},
    {"name": "สนาม 4", "description": "สนามหญ้าเทียม (ฟุตบอล 5 คน) - ขนาดเล็กเล่นสนุก", "price_per_hour": 500},
]

for fd in fields_data:
    obj, created = Field.objects.get_or_create(name=fd["name"], defaults={
        "description": fd["description"],
        "price_per_hour": fd["price_per_hour"]
    })
    if created:
        pass
print("Done populating fields.")
