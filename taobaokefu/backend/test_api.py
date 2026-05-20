
import requests

try:
    response = requests.post(
        'http://localhost:8080/chat',
        json={'question': '帮我查询订单号TB20260520001的物流信息'}
    )
    print("Status code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
