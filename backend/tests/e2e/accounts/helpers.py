def extract_refresh_token_from_set_cookie(
    set_cookie_header: str,
) -> str | None:
    prefix = "refresh_token="
    if prefix not in set_cookie_header:
        return None
    after = set_cookie_header.split(prefix, 1)[1]
    return after.split(";", 1)[0]
