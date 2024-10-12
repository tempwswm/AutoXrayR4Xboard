import logging
import click

from helper import g_logger
from node_handler import node_f
from server_handler import server_f


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.option("-s", "--server", is_flag=True, help="以服务端模式运行")
@click.option("-n", "--node", is_flag=True, help="以节点模式运行")
@click.option("--url", help="对外暴露的地址，比如：http://1.1.1.1:1234/token")
@click.option("--board_email", help="面板登录邮箱")
@click.option("--board_password", help="面板登录密码")
@click.option("--board_url", help="面板链接地址，比如：http://127.0.0.1:7001/abcdefgh")
@click.option("--label", help="节点标签")
@click.option("--certmode", default=None, help="使用证书")
@click.version_option("0.0.1", "-v", "--version", help="查看版本")
def main(
    server, node, debug, url, board_email, board_password, board_url, label, certmode
):
    if debug:
        g_logger.setLevel(logging.DEBUG)
    if server:
        server_f(url, board_url, board_email, board_password)
    else:
        node_f(url, label, certmode)


if __name__ == "__main__":
    main()
