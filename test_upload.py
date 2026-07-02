import requests

url = 'https://catbox.moe/user/api.php'
files = {'fileToUpload': open('test-assets/truck.jpg', 'rb')}
data = {'reqtype': 'fileupload'}
r = requests.post(url, files=files, data=data)
print(r.status_code)
print(r.text)
