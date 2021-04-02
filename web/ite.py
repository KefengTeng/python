import requests

# 验证码url
verifyCodeUrl = 'https://x.x.x.x:x/x/image.jsp'
# 登录页面url
loginUrl = 'https://x.x.x.x:x/x/x'
# 请求头
headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E)',
    'Cookie': 'adminstatusR.jspRecordspPage=20; JSESSIONID=abcCg0he5Rwj3_uHJcUhx'
}

# 拉取验证码图片, 并保存到本地
verifyReq = requests.get(verifyCodeUrl, headers=headers, verify=False)
img = verifyReq.content
with open('number.jpg', 'wb') as f:
    f.write(img)

# post请求传递的表单
number = input('请输入验证码: \n')
data = {
    'netuserid_h': 'x',
    'password_h': 'x',
    'netuserid': '',
    'psccode': '',
    'rand': number
}
# 🎃登录页面
req = requests.post(loginUrl, headers=headers, verify=False, data=data)
print(req.text)
