from urllib.parse import urlsplit


def split_url(url):
    parsed = urlsplit(url)
    scheme_netloc = (
        f"{parsed.scheme}://{parsed.netloc}"
        if parsed.scheme
        else f"http://{parsed.netloc}"
    )
    url_path = parsed.path

    return scheme_netloc, url_path[1:]
