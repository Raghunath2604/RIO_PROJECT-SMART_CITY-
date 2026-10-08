import urllib.request
import json
import time

base_url = 'http://localhost:8000'
print('=' * 75)
print('FOG-IDS COMPREHENSIVE LIVE SYSTEM VERIFICATION')
print('=' * 75)

# 1. Health Check
res = urllib.request.urlopen(f'{base_url}/health')
data = json.loads(res.read().decode('utf-8'))
print(f"1. HEALTH CHECK:        [{data['status']}] | Service: {data['service']} | Version: {data['version']}")

# 2. Models List
res = urllib.request.urlopen(f'{base_url}/api/v1/models')
data = json.loads(res.read().decode('utf-8'))
print(f"2. MODEL REGISTRY:      [{len(data['models'])} Models Loaded] across Binary, 8-Class, 34-Class")

# 3. Single Flow Inference (8-Class with XAI explanation)
payload = json.dumps({
    'features': {'Rate': 980.0, 'syn_count': 18.0, 'ack_count': 12.0, 'Tot size': 90.0, 'IAT': 1.2, 'TCP': 1.0},
    'model_name': 'LightGBM',
    'task': '8class',
    'include_explanation': True
}).encode('utf-8')
req = urllib.request.Request(f'{base_url}/api/v1/predict', data=payload, headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
pred_data = json.loads(res.read().decode('utf-8'))
print(f"3. LIVE PREDICTION:     Detected [{pred_data['prediction']}] | Category: {pred_data['category']} | Severity: {pred_data['threat_severity']} | Latency: {pred_data['latency_us']/1000.0:.2f} ms | Confidence: {pred_data['confidence']*100:.1f}%")
if pred_data.get('feature_attributions'):
    top_ind = pred_data['feature_attributions'][0]
    print(f"   Top XAI Indicator:   {top_ind['feature']} = {top_ind['raw_value']} ({top_ind['direction']}, Impact: {top_ind['impact_score']:+.4f})")

# 4. Adaptive Tier Switching (FR5)
payload = json.dumps({
    'features': {'Rate': 500.0, 'TCP': 1.0, 'syn_count': 10.0},
    'task': '8class'
}).encode('utf-8')
req = urllib.request.Request(f'{base_url}/api/v1/predict/adaptive', data=payload, headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
d = json.loads(res.read().decode('utf-8'))
print(f"4. ADAPTIVE TIER (FR5): Selected [{d['model_selected']}] in [{d['active_tier']}] tier | Latency: {d['latency_us']/1000.0:.2f} ms | Predicted: {d['prediction']}")

# 5. Batch Inference (100 flows)
flows = [{'Rate': float(i * 10), 'TCP': 1.0, 'syn_count': float(i % 5)} for i in range(100)]
payload = json.dumps({'flows': flows, 'model_name': 'CompactMLP', 'task': '8class'}).encode('utf-8')
req = urllib.request.Request(f'{base_url}/api/v1/predict/batch', data=payload, headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
batch_data = json.loads(res.read().decode('utf-8'))
t_sec = batch_data['total_time_ms'] / 1000.0
fps = batch_data['total_flows'] / t_sec if t_sec > 0 else 0
print(f"5. BATCH INFERENCE:     Processed {batch_data['total_flows']} flows in {batch_data['total_time_ms']:.2f} ms ({fps:.1f} flows/sec)")

# 6. Static SOC UI Delivery
res = urllib.request.urlopen(f'{base_url}/')
html_len = len(res.read())
print(f"6. ENTERPRISE SOC UI:   HTTP {res.status} OK | Size: {html_len} bytes")

print('=' * 75)
print('ALL 6 SUBSYSTEMS CONFIRMED 100% OPERATIONAL.')
print('=' * 75)
