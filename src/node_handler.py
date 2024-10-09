import asyncio
import logging

import click
import httpx

import xrayr_handler

httpx_client = httpx.AsyncClient()

cache_data = {"res": {}}


# 应用变更
async def update_xray():
    click.echo("应用变更")
    xrayr_handler.gen_xrayr_config_yml(cache_data["res"])
    xrayr_handler.run_xrayr()


async def cycle(url, label):
    while True:
        try:
            response = await httpx_client.get(
                url=url,
                params={"label": label},
            )
            new_res = response.json()
        except Exception as e:
            logging.error(e)
            new_res = cache_data["res"]

        if new_res != cache_data["res"] and new_res["nodes"]:
            cache_data["res"] = new_res
            await update_xray()

        await asyncio.sleep(cache_data["res"].get("interval", 10))


def node_f(url, label):
    asyncio.run(cycle(url, label))
