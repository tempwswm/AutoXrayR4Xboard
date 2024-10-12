import asyncio
import datetime
from urllib.parse import urlsplit

import httpx
import uvicorn
from fastapi import FastAPI, Request

import helper
from helper import g_logger

cache_data = {
    "interval": 10.0,
    "headers": {"authorization": ""},
    "nodes": {},
    "labels": {"board": {"ip": "127.0.0.1", "last_connect": datetime.datetime.now()}},
}
httpx_client = httpx.AsyncClient(headers=cache_data["headers"])


def update_label_record(label, ip):
    if (  # 这里有逻辑短路所以不会有KeyError
        label not in cache_data["labels"]  # 没有记录就新增
        or cache_data["labels"][label]["ip"] == ip  # IP相同更新时间
        # IP不相同且老IP离线超过 间隔时间的10倍，就更新
        or (
            cache_data["labels"][label]["ip"] != ip
            and datetime.datetime.now() - cache_data["labels"][label]["last_connect"]
            > datetime.timedelta(seconds=(10 * cache_data["interval"]))
        )
    ):
        cache_data["labels"][label] = {
            "ip": ip,
            "last_connect": datetime.datetime.now(),
        }


def is_label_use_ip(label, ip):
    return cache_data["labels"][label]["ip"] == ip


async def hello(label: str, request: Request):

    update_label_record(label, request.client.host)

    ret = {
        "board_base_url": cache_data["board_base_url"],
        "interval": cache_data["interval"],
        "board_token": cache_data["board_token"],
        "nodes": cache_data["nodes"].get(label, []),
    }

    if is_label_use_ip(label, request.client.host):
        return ret
    else:
        ret["board_base_url"] = None
        ret["board_token"] = None
        ret["interval"] = 60
        ret["nodes"] = []

        return ret


async def board_login():
    url = cache_data["board_base_url"] + "/api/v1/passport/auth/login"
    payload = {
        "email": cache_data["board_email"],
        "password": cache_data["board_password"],
    }

    response = await httpx_client.post(url, data=payload)
    cache_data["headers"] = {"authorization": response.json()["data"]["auth_data"]}


async def board_update():
    while True:
        await get_nodes()
        await get_config()
        await asyncio.sleep(cache_data.get("interval", 10))


async def get_nodes():
    try:
        response = await httpx_client.get(
            url=f"{cache_data['board_base_url']}/api/v1/{cache_data['board_endpoint']}/server/manage/getNodes",
            headers=cache_data["headers"],
        )
        cache_data["nodes"] = {}
        for node in response.json()["data"]:
            label = node["ips"][0] if node["ips"] else ""
            node_type = node["type"]
            node_id = node["id"]

            cache_data["nodes"][label] = cache_data["nodes"].get(label, list())
            cache_data["nodes"][label].append(
                {
                    "type": node_type,
                    "id": node_id,
                }
            )

    except Exception as e:
        g_logger.error(e)


async def get_config():
    try:
        response = await httpx_client.get(
            url=f"{cache_data['board_base_url']}/api/v1/{cache_data['board_endpoint']}/config/fetch",
            headers=cache_data["headers"],
        )
        cache_data["board_token"] = response.json()["data"]["server"]["server_token"]
        cache_data["interval"] = (
            int(response.json()["data"]["server"]["server_pull_interval"]) / 2
        )
    except Exception as e:
        g_logger.error(e)


async def init_update():
    await board_login()
    task = asyncio.create_task(board_update())

    g_logger.info("初始化完成")


def server_f(url, board_url, board_email, board_password):
    if board_email is None or board_password is None or board_url is None:
        g_logger.error("请输入面板邮箱和密码")
        exit(1)

    base_url, token = helper.split_url(url)
    board_base_url, board_endpoint = helper.split_url(board_url)

    cache_data["board_base_url"] = board_base_url
    cache_data["board_endpoint"] = board_endpoint
    cache_data["board_email"] = board_email
    cache_data["board_password"] = board_password

    port = urlsplit(base_url).port
    app = FastAPI()
    app.get(f"/{token}")(hello)
    app.on_event("startup")(init_update)
    g_logger.debug("连接密钥：" + token)
    uvicorn.run(app, host="0.0.0.0", port=port)
