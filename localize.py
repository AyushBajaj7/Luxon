import os
import re

templates_dir = r'd:\projects\Luxon\app\templates'
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Jinja2 rendering replacements
            content = content.replace('${{', '₹{{')
            content = content.replace('Price ($)', 'Price (₹)')
            content = content.replace('Max Price ($)', 'Max Price (₹)')
            content = content.replace("value = '$' + this.value", "value = '₹' + this.value")
            
            # JS template literal replacements
            content = content.replace('`$${', '`₹${')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

shop_py = r'd:\projects\Luxon\app\shop.py'
with open(shop_py, 'r', encoding='utf-8') as f:
    shop_content = f.read()

shop_content = shop_content.replace("'currency': 'USD'", "'currency': 'INR'")
shop_content = shop_content.replace('"currency": "USD"', '"currency": "INR"')

with open(shop_py, 'w', encoding='utf-8') as f:
    f.write(shop_content)

print('Localization replacements complete.')
