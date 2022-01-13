import aiohttp
from typing import Awaitable, Union

BASE_URL = "https://www.vlive.tv"

JsonResponse = Union[dict, list]


async def _arequest(
    endpoint: str, method: str = "get", body: dict = None, params: dict = None
) -> Awaitable[JsonResponse]:
    async with aiohttp.ClientSession() as session:
        api = getattr(session, method)
        url = f"{BASE_URL}/{endpoint}"
        if len(params.keys()) > 0:
            url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        async with api(url, data=body) as res:
            return await res.json()


def search_channels(search: str) -> Awaitable[JsonResponse]:
    return _arequest(
        "search/auto/channels",
        params={
            "dataType": "json",
            "query": search,
            "maxNumOfRows": 5,
        },
    )
