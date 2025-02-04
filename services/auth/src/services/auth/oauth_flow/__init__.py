__all__ = ["AuthError", "get_auth_flow", "AuthFlow"]

from app_types.common import Provider
from settings import settings

from .base import AuthFlow
from .exceptions import AuthError
from .github import GithubAuthFlow
from .yandex import YandexAuthFlow


def get_auth_flow(provider: Provider) -> AuthFlow:
    return {
        Provider.GITHUB: GithubAuthFlow(
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            redirect_uri=settings.github_redirect,
        ),
        Provider.YANDEX: YandexAuthFlow(
            client_id=settings.yandex_client_id,
            client_secret=settings.yandex_client_secret,
            redirect_uri=settings.yandex_redirect,
        ),
    }[provider]
