import requests

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
        "Host": "www.jianshu.com",
        "Pragma": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded"
    }
def get_sms_code(phone_number:str) -> None:
    code_url = "https://www.jianshu.com/mobile_phone/send_code"
    post_data = {
        "force_user_nonexist": "true",
        "iso_code": "CN",
        "mobile_number": phone_number,
        "captcha": {
            "validation": {
                "challenge": "1829c0d6b028b09c726e44278671da58",
                "gt": "ec47641997d5292180681a247db3c92e",
                "seccode": "4c40a7bd14bb1b5301dcc80122c53746|jordan",
                "validate": "4c40a7bd14bb1b5301dcc80122c53746"
            }
        }
    }
    response = requests.post(url=url,data=post_data)
    assert (response.json=={"message":"验证码已发送"})
def auto_register(phone_number:str,code:str) -> None:
    register_url = "https://www.jianshu.com/users/register"
    post_data = {
        "authenticity_token":"R5hmVN5tFLWOgNlpG65uGYWQgp2Uwx4qH5SWGUnr4DkhOZg+GsHwZqVz4qf4YJaI9HLkfR8eNhz9+xBJD86UnA==",
        "captcha[id]": "",
        "captcha[validation][challenge]":"b98ab6d878ac64f1dcfe6eab37559635",
        "captcha[validation][gt]":"ec47641997d5292180681a247db3c92e",
        "captcha[validation][seccode]":"1e9d37eb4f2e478857b160d4795eaa5d|jordan",
        "captcha[validation][validate]":"1e9d37eb4f2e478857b160d4795eaa5d",
        "commit":"注册",
        "force_user_nonexist":"true",
        "oversea":"false",
        "security_number":"true",
        "sms_code":code,
        "user[mobile_number_country_code]":"CN",
        "user[mobile_number]":phone_number,
        "user[nickname]":"shuangzizuo",
        "user[password]":"shuangzizuo",
        "utf8":"✓",
    }
    response = requests.post(url=url,data=post_data)
    print(response.text)
if __name__ == "__main__":
    get_sms_code(phone_number="")
    auto_register()