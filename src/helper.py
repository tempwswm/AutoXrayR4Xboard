from urllib.parse import urlsplit
import logging


def split_url(url):
    parsed = urlsplit(url)
    scheme_netloc = (
        f"{parsed.scheme}://{parsed.netloc}"
        if parsed.scheme
        else f"http://{parsed.netloc}"
    )
    url_path = parsed.path

    return scheme_netloc, url_path[1:]


g_logger = logging.getLogger("global")
g_logger.setLevel(logging.INFO)
format_str = logging.Formatter(
    "%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s"
)
sh = logging.StreamHandler()  # 往屏幕上输出
sh.setFormatter(format_str)
g_logger.addHandler(sh)
