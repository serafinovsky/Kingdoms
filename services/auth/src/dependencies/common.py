from fastapi import Request

from services.auth import make_fingerprint


def get_fingerprint(request: Request):
    ua = request.headers.get("user-agent", "")
    return make_fingerprint(ua)


async def get_client_ip(request: Request) -> str:
    """
    Extract the client's IP address from the request.

    Args:
        request (Request): The incoming request object.

    Returns:
        str: The client's IP address.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = ""
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0]
    elif request.client:
        client_ip = request.client.host
    return client_ip
