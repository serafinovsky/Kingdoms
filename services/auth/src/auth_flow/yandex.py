import json

from httpx import AsyncClient, HTTPError, QueryParams, TimeoutException
from pydantic import ValidationError

from auth_flow.base import AuthFlow
from logger import logging
from schemas.auth import UserData, YandexUser

from .exeptions import AuthError

logger = logging.getLogger(__name__)


class YandexAuthFlow(AuthFlow):
    """
    Yandex OAuth authentication flow implementation.

    Handles the OAuth2 flow for Yandex authentication, including:
    - Generating authorization URLs
    - Exchanging authorization codes for access tokens
    - Fetching user information
    """

    AUTH_URL = "https://oauth.yandex.ru/authorize"
    TOKEN_URL = "https://oauth.yandex.ru/token"
    USER_URL = "https://login.yandex.ru/info"
    TIMEOUT_SECONDS = 10

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Yandex authentication flow.

        Args:
            client_id: Yandex OAuth app client ID
            client_secret: Yandex OAuth app client secret
            redirect_uri: OAuth callback URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def authorize_url(self) -> str:
        """
        Generate Yandex OAuth authorization URL.

        Returns:
            str: Complete authorization URL with query parameters
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        url = f"{self.AUTH_URL}?{str(QueryParams(params))}"
        logger.debug(f"Generated Yandex authorization URL: {url}")
        return url

    async def process_response(self, code: str) -> UserData:
        """
        Process OAuth callback response.

        Args:
            code: Authorization code from Yandex

        Returns:
            UserData: Normalized user information

        Raises:
            AuthError: If authentication fails at any step
        """
        try:
            async with AsyncClient() as client:
                token = await self._get_token(client, code)
                return await self._get_user(client, token)
        except TimeoutException as e:
            logger.error(
                "Timeout while processing Yandex authentication",
                exc_info=e,
            )
            raise AuthError("Authentication timeout") from e
        except HTTPError as e:
            logger.error("HTTP error during Yandex authentication", exc_info=e)
            raise AuthError("Authentication failed") from e
        except Exception as e:
            logger.error("Unexpected error", exc_info=e)
            raise AuthError("Authentication failed") from e

    async def _get_token(self, client: AsyncClient, code: str) -> str:
        """
        Exchange authorization code for access token.

        Args:
            client: HTTP client
            code: Authorization code

        Returns:
            str: Access token

        Raises:
            AuthError: If token exchange fails
        """
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        response = await client.post(
            self.TOKEN_URL,
            data=QueryParams(params),
            headers=headers,
            timeout=self.TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        try:
            token_data: dict[str, str] = response.json()
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in token response", exc_info=e)
            raise AuthError("Invalid token response") from e

        token = token_data.get("access_token")
        if not token:
            logger.error("No access token in Yandex response")
            raise AuthError("No access token received")

        return token

    async def _get_user(self, client: AsyncClient, token: str) -> UserData:
        """
        Fetch user information using access token.

        Args:
            client: HTTP client
            token: Access token

        Returns:
            UserData: Normalized user information

        Raises:
            AuthError: If user data fetch or validation fails
        """
        params = {"format": "json"}
        headers = {"Authorization": f"OAuth {token}"}

        response = await client.get(
            self.USER_URL,
            params=params,
            headers=headers,
            timeout=self.TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        try:
            user_data = response.json()
            yandex_user = YandexUser(**user_data)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in user response", exc_info=e)
            raise AuthError("Invalid user data response") from e
        except ValidationError as e:
            logger.error("Invalid user data schema", exc_info=e)
            raise AuthError("Invalid user data format") from e

        return yandex_user.to_user_data()
