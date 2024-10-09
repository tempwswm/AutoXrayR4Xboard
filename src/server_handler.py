import asyncio
import datetime
import random
import string
from urllib.parse import urlsplit, urlparse

import click
import httpx
import starlette
import uvicorn
from fastapi import FastAPI

import helper

cache_data = {
    "headers": {"authorization": ""},
    "nodes": {},
}
httpx_client = httpx.AsyncClient(headers=cache_data["headers"])


async def hello(label: str):
    return {
        "board_base_url": cache_data["board_base_url"],
        "interval": cache_data["interval"],
        "board_token": cache_data["board_token"],
        "nodes": cache_data["nodes"].get(label, []),
    }


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
            label = node["ips"][0]
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
        click.echo(e)


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
        click.echo(e)


async def init_update():
    await board_login()
    task = asyncio.create_task(board_update())

    click.echo("初始化完成")


def server_f(url, board_url, board_email, board_password):
    if board_email is None or board_password is None or board_url is None:
        click.echo("请输入面板邮箱和密码")
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
    click.echo("连接密钥：" + token)
    uvicorn.run(app, host="0.0.0.0", port=port)
