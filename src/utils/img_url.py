import aiohttp
import json
from typing import Optional



async def base64_to_URL(base64_str: str) -> Optional[str]:
    """
    将base64编码的图像上传到图床并返回URL
    :param base64_str: base64编码的图像字符串
    :return: 图像的URL，如果上传失败则返回None
    """
    # 确保base64字符串格式正确
    if not base64_str:
        print("Error: Base64 string is empty.")
        return None

    # 如果base64字符串包含data URI前缀，需要移除
    if base64_str.startswith('data:'):
        # 提取实际的base64数据
        if 'base64,' in base64_str:
            base64_str = base64_str.split('base64,')[1]
        else:
            print("Warning: Base64 string starts with 'data:' but does not contain 'base64,'. Proceeding with full string.")

    url = "https://www.picgo.net/api/1/upload"

    # 正确的payload格式，aiohttp的data参数会将其作为form-urlencoded数据发送
    payload = {
        "source": base64_str
    }

    headers = {
        'X-API-Key': 'chv_Sr5Xh_f326f7265114c537b46345d95ab1df7cfe17bac631a3f9ad6be0e18826b97e48622b20404fe84eccf49d261abc1ae6211764c573a326d0debad46980b8b7d557'
    }

    try:
        # 使用aiohttp.ClientSession() 创建一个会话，推荐使用async with
        async with aiohttp.ClientSession() as session:
            # 发送POST请求，设置超时时间
            async with session.post(url, headers=headers, data=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                # 打印响应信息用于调试
                print(f"Status Code: {response.status}")
                print(f"Response Headers: {response.headers}")
                
                # 异步获取响应文本
                response_text = await response.text()
                print(f"Response Text: {response_text}")

                # 检查响应状态码
                if response.status == 200:
                    # 尝试解析JSON响应
                    try:
                        response_data = json.loads(response_text)
                        # 检查响应中是否包含错误信息
                        if "error" in response_data:
                            print(f"API Error: {response_data['error']}")
                            return None
                        
                        # 返回图像URL
                        image_url = response_data.get("image", {}).get("url")
                        if image_url:
                            return image_url
                        else:
                            # 如果没有url，尝试url_viewer
                            url_viewer = response_data.get("image", {}).get("url_viewer")
                            if url_viewer:
                                print("Warning: 'url' not found, returning 'url_viewer'.")
                                return url_viewer
                            else:
                                print("Error: Neither 'url' nor 'url_viewer' found in response.")
                                return None
                    except json.JSONDecodeError:
                        print("Failed to decode JSON response. Response was not valid JSON.")
                        return None
                else:
                    print(f"Upload failed with status code: {response.status}")
                    print(f"Response text: {response_text}")
                    return None
    except aiohttp.ClientError as e:
        # 捕获aiohttp客户端相关的错误（如连接错误、超时等）
        print(f"Request failed due to aiohttp client error: {e}")
        return None
    except Exception as e:
        # 捕获其他意外错误
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # 测试base64_to_URL函数
    test_base64 = "iVBORw0KGgoAAAANSUhEUgAAABwAAAA4CAIAAABhUg/jAAAAMklEQVR4nO3MQREAMAgAoLkoFreTiSzhy4MARGe9bX99lEqlUqlUKpVKpVKpVCqVHksHaBwCA2cPf0cAAAAASUVORK5CYII="
    image_url = base64_to_URL(test_base64)
    if image_url:
        print(f"Image URL: {image_url}")
    else:
        print("Image upload failed or returned no URL.")