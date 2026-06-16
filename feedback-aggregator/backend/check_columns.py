import requests
r = requests.get('http://localhost:5000/api/get-data')
data = r.json()
print(f'Colonnes: {len(data["columns"])}')
print(f'Lignes: {data["lines"]}')
print('Dernieres 5:', data['columns'][-5:])
print('Colonnes Cell:', [c for c in data['columns'] if 'cell' in c.lower()])
