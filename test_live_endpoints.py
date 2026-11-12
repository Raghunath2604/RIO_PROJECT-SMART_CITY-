import urllib.request
import json

req = urllib.request.urlopen('http://127.0.0.1:8000/api/v1/models')
print('Models endpoint status:', req.status)
data = json.loads(req.read().decode())
print('Total models available:', len(data.get('models', [])))
for m in data.get('models', [])[:4]:
    print(' -', m.get('model_name'), '| type:', m.get('type'), '| size:', m.get('file_size_bytes'), 'bytes')

req_alerts = urllib.request.urlopen('http://127.0.0.1:8000/api/v1/alerts')
print('Alerts endpoint status:', req_alerts.status)

req_dash = urllib.request.urlopen('http://127.0.0.1:8501')
print('Streamlit dashboard status:', req_dash.status)
