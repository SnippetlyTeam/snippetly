from typing import Optional

from fastapi.requests import Request


class Paginator:
    @staticmethod
    def calculate_offset(page: int, per_page: int) -> int:
        return (page - 1) * per_page

    @staticmethod
    def build_links(
        request: Request, page: int, per_page: int, total: int
    ) -> tuple[Optional[str], Optional[str]]:
        params = dict(request.query_params)
        params["per_page"] = str(per_page)

        prev_page = None
        if page > 1:
            params["page"] = str(page - 1)
            prev_page = str(request.url.replace_query_params(**params))

        next_page = None
        if (page * per_page) < total:
            params["page"] = str(page + 1)
            next_page = str(request.url.replace_query_params(**params))

        return prev_page, next_page

    @staticmethod
    def total_pages(total: int, per_page: int) -> int:
        return (total + per_page - 1) // per_page
