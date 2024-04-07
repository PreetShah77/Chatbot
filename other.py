import requests

url = 'http://localhost:5000/get_student_info'
data = {'prompt': 'What is enrollment number of Manthan Mehta'}

response = requests.post(url, json=data)
print(requests.post(url,json=data) )
print(response.json())