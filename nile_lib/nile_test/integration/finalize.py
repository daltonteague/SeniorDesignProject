import requests
import datetime

end_time = datetime.datetime.now().isoformat()
print(f"Nile: Test finalized with end time: {end_time}")
data = {
  'end': end_time}
finalize_endpoint = f'http://localhost:5000/api/v1/tests/finalize'
response = requests.post(finalize_endpoint, json=data)
if response.status_code != 200:
    raise RuntimeError('Could not finalize test')
else:
    print('Nile: Test Finalized')
