import tinydb

db = tinydb.TinyDB('category_mapping.json')

# data = {
#     'online dining': None,
#     'petrol': 'Petrol',
#     'petronas': 'Petrol',
#     'shell': 'Petrol',
#     'bhp': 'Petrol',
#     'groceries': 'Groceries',
#     'AEON': 'Groceries',
#     'grocery': 'Groceries',
#     'online': 'Online Shopping',
#     'dining': 'Dining',
#     'online shopping': 'Online Shopping',
#     'online spending': 'Online Shopping',
#     'supermarket': 'Groceries',
#     'local': 'Others',
#     'all': 'Others',
#     'other': 'Others',
# }

# db.insert(data)

mapping = db.all()
print(mapping[0])