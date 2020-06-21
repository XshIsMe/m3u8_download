import hashlib
import re

import requests
from Crypto.Cipher import AES
from tqdm import tqdm


def md5(plain):
    return hashlib.md5(plain.encode()).hexdigest()


def read_m3u8(url):
    response = requests.get(url)
    ts_name_list = re.findall(r"#EXTINF:.*?,\n(.*?)\n", response.text)
    key_name_list = re.findall(r'#EXT-X-KEY:METHOD=AES-128,URI="(.*?)"', response.text)
    if 0 < len(key_name_list):
        key_name = key_name_list[0]
    else:
        key_name = None
    return key_name, ts_name_list


def read_ts(url):
    response = requests.get(url)
    return response.content


def download(m3u8_url, output_path):
    # 参数预处理
    base_url = re.findall(r"(.*/)", m3u8_url)[0]
    key_name, ts_name_list = read_m3u8(m3u8_url)
    if "\\" != output_path[-1]:
        output_file = "{output_path}\\{output_name}.mp4".format(
            output_path=output_path, output_name=md5(m3u8_url)
        )
    else:
        output_file = "{output_path}{output_name}.mp4".format(
            output_path=output_path, output_name=md5(m3u8_url)
        )
    # 初始化文件
    init_file = open(output_file, "w")
    init_file.close()
    # 获取密钥
    if None != key_name:
        key_url = base_url + key_name
        key = read_ts(key_url)
        cryptor = AES.new(key, AES.MODE_CBC, key)
    # 合并ts
    print("开始下载：{m3u8_url}".format(m3u8_url=m3u8_url))
    for i in tqdm(range(len(ts_name_list))):
        ts_url = base_url + ts_name_list[i]
        ts_content = read_ts(ts_url)
        with open(output_file, "ab") as file:
            if None != key_name:
                file.write(cryptor.decrypt(ts_content))
            else:
                file.write(ts_content)
    print("下载完成：{output_file}".format(output_file=output_file))


m3u8_url_list = [
    r"https://www.demo.com/1.m3u8",
    r"https://www.demo.com/2.m3u8",
]
output_path = r"C:\m3u8"

for m3u8_url in m3u8_url_list:
    download(m3u8_url, output_path)
