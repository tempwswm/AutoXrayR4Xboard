import logging
import os.path

import docker
from docker.errors import NotFound
from docker.types import Mount
import yaml

from model import Node


def run_xrayr():
    client = docker.from_env()
    mount1 = Mount(
        target="/etc/XrayR/config.yml",
        source="/etc/XrayR/config.yml",
        type="bind",
        read_only=False,
    )
    try:
        client.containers.get("xrayr").stop()
        client.containers.get("xrayr").remove()
    except NotFound:
        pass
    except Exception as e:
        logging.error(e)
    try:
        client.containers.run(
            "ghcr.io/xrayr-project/xrayr:latest",
            detach=True,
            tty=True,
            mounts=[mount1],
            name="xrayr",
            network_mode="host",
            restart_policy={"Name": "always"},
        )
    except Exception as e:
        logging.error(e)


def gen_nodes_yml(res):
    all_nodes = [
        gen_node_yml(node, res["board_base_url"], res["board_token"])
        for node in res["nodes"]
    ]
    useful_nodes = [node for node in all_nodes if node is not None]
    return useful_nodes


def gen_node_yml(node, board_base_url, board_token):
    template_f = f'./config_template/{node["type"]}.yml'
    if not os.path.exists(template_f):
        return None
    with open(template_f, "r+") as f_read:
        node_yml = yaml.safe_load(f_read)

    node_yml["ApiConfig"]["ApiHost"] = board_base_url
    node_yml["ApiConfig"]["ApiKey"] = board_token
    node_yml["ApiConfig"]["NodeID"] = node["id"]

    return node_yml


def gen_xrayr_config_yml(res):
    with open("./config_template/config.yml", "r+") as f_read:
        sample_yaml = yaml.safe_load(f_read)

    sample_yaml["Nodes"] = gen_nodes_yml(res)
    with open("/etc/XrayR/config.yml", "w") as f_out:
        yaml.safe_dump(sample_yaml, f_out)
