import asyncio
import json
from typing import Optional, Union, Dict, Any

from aiohttp import FormData
from loguru import logger

import aiohttp

"""
useful urls for MCM
/MaiChartManagerServlet/ImportChartCheckApi
/MaiChartManagerServlet/AddMusicApi/{assetDir}/{id}
/MaiChartManagerServlet/ImportChartApi
/MaiChartManagerServlet/SetAudioApi/{assetDir}/{id}
/MaiChartManagerServlet/SetMovieApi/{assetDir}/{id}
/MaiChartManagerServlet/SetMusicJacketApi/{assetDir}/{id}
"""


async def aio_package(method: str, url: str, data: Optional[Union[bytes, str, Dict, FormData]] = None,
                      timeout: int = 300, headers: Optional[Dict] = None):
    """
    Args:
        method: 'GET', 'POST', 'PUT'
        url: URL
        data: 请求体
        timeout: 超时时间
        headers: 请求头

    Returns:
        resp dict
    """
    method = method.upper()

    # 设置超时
    timeout_obj = aiohttp.ClientTimeout(total=timeout)

    # 设置默认请求头
    if headers is None:
        headers = {}

    try:
        async with aiohttp.ClientSession(timeout=timeout_obj, headers=headers) as session:
            if method.upper() == "GET":
                async with session.get(url=url, ssl=False) as response:
                    # 读取响应内容并返回
                    content = await response.read()
                    text = await response.text()
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'content': content,
                        'text': text,
                    }

            elif method.upper() == "POST":
                if data is None:
                    # 没有数据的POST请求
                    async with session.post(url=url, ssl=False) as response:
                        content = await response.read()
                        text = await response.text()
                        return {
                            'status': response.status,
                            'headers': dict(response.headers),
                            'content': content,
                            'text': text,
                        }
                else:

                    if not isinstance(data, dict) and not isinstance(data, FormData):
                        form_data = FormData()
                        form_data.add_field('file', data)
                    else:
                        form_data = data

                    async with session.post(url=url, data=form_data, ssl=False) as response:
                        content = await response.read()
                        text = await response.text()
                        return {
                            'status': response.status,
                            'headers': dict(response.headers),
                            'content': content,
                            'text': text,
                        }
            elif method.upper() == "PUT":
                async with session.put(url=url, data=data, ssl=False) as response:
                    content = await response.read()
                    text = await response.text()
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'content': content,
                        'text': text,
                    }
            else:
                return ValueError(f"Unsupported HTTP method: {method}")

    except Exception as e:
        return logger.exception(f"Unknown exception: {e}")


async def import_music(music_file):
    flag = False
    music_path = await unzip_music(music_file)
    try:
        pre_check = await import_check(music_path)
        if not pre_check["accept"]:
            flag = False
            logger.info("Bad")
            return flag
        logger.info("Good")

        music_id = await get_music_id()
        if pre_check['isDx']:
            music_id += 10000

        logger.debug(f"Music id: {music_id}")
        await add_music_dir(music_id)
        await import_music_file(music_path, music_id)
        await import_acb(music_path, music_id)
        await import_pv(music_path, music_id)
        await import_jacket(music_path, music_id)
        flag = True
    except:
        logger.exception("导入音乐失败")
        flag = False




    await clean_music(music_path)

    return flag

async def import_jacket(file_path, music_id, asset_dir="A403"):
    url = f"https://127.0.0.1:5001/MaiChartManagerServlet/SetMusicJacketApi/{asset_dir}/{music_id}"

    fd = FormData({
        'file': open(f"{file_path}/bg.png", "rb"),
    })
    resp = await aio_package("put", url, data=fd)
    if resp["status"] != 200:
        logger.error("导入封面失败")
        logger.debug("错误信息: ", resp)

async def import_acb(file_path, music_id, asset_dir="A403"):
    url = f"https://127.0.0.1:5001/MaiChartManagerServlet/SetAudioApi/{asset_dir}/{music_id}"

    fd = FormData({
        'padding': "0",
        'file': open(f"{file_path}/track.mp3", "rb"),
    })
    resp = await aio_package("put", url, data=fd)

    if resp["status"] != 200:
        logger.error("导入音频失败")
        logger.debug("错误信息: ", resp)


async def import_pv(file_path, music_id, asset_dir="A403"):
    url = f"https://127.0.0.1:5001/MaiChartManagerServlet/SetMovieApi/{asset_dir}/{music_id}"
    fd = FormData(
        {
            'padding': "0",
            'file': open(f"{file_path}/pv.mp4", "rb"),
            'noScale': 'false',
            'h264': 'false'
        }
    )

    resp = await aio_package("put", url, data=fd)
    if resp["status"] != 200:
        logger.error("导入PV失败")
        logger.debug("错误信息: ", resp)


async def import_music_file(music_path, music_id, asset_dir="A403"):
    url = "https://127.0.0.1:5001/MaiChartManagerServlet/ImportChartApi"
    fd = FormData(
        {
            'id': str(music_id),
            'file': open(f"{music_path}/maidata.txt", "rb"),
            'ignoreLevelNum': "true",
            'addVersionId': "24",
            'genreId': "100",
            'version': "25500",
            'assetDir': asset_dir,
            'shift': 'NoShift',
            'debug': "false"
        }
    )

    resp = await aio_package("post", url, data=fd)
    resp_json = json.loads(resp["content"])
    if resp_json["fatal"]:
        logger.error("导入失败")
        logger.debug("错误信息: ", resp)


async def import_check(path):
    url = "https://127.0.0.1:5001/MaiChartManagerServlet/ImportChartCheckApi"
    try:
        with open(f"{path}/maidata.txt", "r", encoding="utf-8") as f:
            maidata = f.read().encode("utf-8")
    except FileNotFoundError:
        logger.error(f"maidata.txt not found in {path}")
        return {"accept": False}
    resp = await aio_package(method="post", url=url, data=maidata)
    if resp["status"] != 200:
        return {"accept": False}
    resp_json = json.loads(resp["content"])

    if resp_json["accept"]:
        return resp_json
    else:
        return {"accept": False}


async def get_music_id():
    """
    https://127.0.0.1:5001/MaiChartManagerServlet/GetMusicListApi
    """
    url = "https://127.0.0.1:5001/MaiChartManagerServlet/GetMusicListApi"
    resp = await aio_package(method="get", url=url)
    max_id = 5000
    resp_json = json.loads(resp["content"])
    for i in resp_json:
        if i["nonDxId"] > max_id:
            max_id = i["nonDxId"]
        elif i["nonDxId"] == max_id:
            max_id += 1

    return max_id


async def add_music_dir(music_id, asset_dir="A403"):
    # async with (aiohttp.ClientSession() as session):
    #     async with session.post(url=f"https://127.0.0.1:5001/MaiChartManagerServlet/AddMusicApi/{asset_dir}/{music_id}",
    #                             ssl=False) as response:
    #         resp = await response.text()
    #         logger.debug(resp)
    url = f"https://127.0.0.1:5001/MaiChartManagerServlet/AddMusicApi/{asset_dir}/{music_id}"
    resp = await aio_package(method="post", url=url)
    if resp["content"] == b'':
        logger.debug("Good")
        return
    else:
        logger.debug("Not Good")


async def unzip_music(file_path):
    import zipfile
    import os
    filename = os.path.basename(file_path)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        zip_ref.extractall(f"temp/{filename}")

    # found maidata.txt and so on
    music_dir = f"temp/{filename}"
    if not os.path.exists(f"{music_dir}/maidata.txt"):
        logger.warning(f"No maidata.txt in {music_dir}")
        logger.warning("Try goto subfolder")
        for root, dirs, files in os.walk(music_dir):
            if "maidata.txt" in files:
                music_dir = root
                break
        else:
            logger.error("maidata.txt not found")

    return music_dir


async def clean_music(file_path):
    import shutil
    import os

    file_path = os.path.abspath(file_path)

    if os.path.abspath("temp") != os.path.dirname(file_path):
        file_path = os.path.dirname(file_path)

    try:
        shutil.rmtree(f"{file_path}")
        logger.info(f"Cleaned up {file_path}")
    except FileNotFoundError:
        logger.warning(f"Directory {file_path} not found for cleanup")


# with open("ライアーメイデン (feat. りぃふ)/maidata.txt", "r", encoding="utf-8") as f:
#     mf = f.read().encode("utf-8")

# with open("ライアーメイデン (feat. りぃふ).zip","rb")

# Example usage
# loop = asyncio.get_event_loop()
# loop.run_until_complete(import_music(mf))
# loop.run_until_complete(import_music("ライアーメイデン (feat. りぃふ).zip"))
# loop.run_until_complete(clean_music("temp/ライアーメイデン (feat. りぃふ).zip/ライアーメイデン (feat. りぃふ)"))

"""
使用import_music
形参是压缩包路径

"""
