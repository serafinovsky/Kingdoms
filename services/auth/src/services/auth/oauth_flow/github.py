import json

from httpx import AsyncClient, HTTPError, QueryParams, TimeoutException
from pydantic import ValidationError

from logger import logging
from schemas.auth import GithubUser, UserData

from .base import AuthFlow
from .exceptions import AuthError

logger = logging.getLogger(__name__)


class GithubAuthFlow(AuthFlow):
    """
    GitHub OAuth authentication flow implementation.

    Handles the OAuth2 flow for GitHub authentication, including:
    - Generating authorization URLs
    - Exchanging authorization codes for access tokens
    - Fetching user information
    """

    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    TIMEOUT_SECONDS = 5

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize GitHub authentication flow.

        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret
            redirect_uri: OAuth callback URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def authorize_url(self) -> str:
        """
        Generate GitHub OAuth authorization URL.

        Returns:
            str: Complete authorization URL with query parameters
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",
        }
        url = f"{self.AUTH_URL}?{str(QueryParams(params))}"
        logger.debug(f"Generated GitHub authorization URL: {url}")
        return url

    async def process_response(self, code: str) -> UserData:
        """
        Process OAuth callback response.

        Args:
            code: Authorization code from GitHub

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
                "Timeout while processing GitHub authentication",
                exc_info=e,
            )
            raise AuthError("Authentication timeout") from e
        except HTTPError as e:
            logger.error("HTTP error during GitHub authentication", exc_info=e)
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
            "code": code,
        }

        try:
            response = await client.post(
                self.TOKEN_URL,
                json=params,
                timeout=self.TIMEOUT_SECONDS,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            token_data: dict[str, str] = response.json()
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in token response", exc_info=e, stack_info=True)
            raise AuthError("Invalid token response") from e
        except Exception as e:
            logger.error("Can't take token", exc_info=e, stack_info=True)
            raise AuthError("Can't take token") from e

        token = token_data.get("access_token")
        if not token:
            logger.error("No access token in GitHub response")
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
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(self.USER_URL, headers=headers, timeout=self.TIMEOUT_SECONDS)
        response.raise_for_status()

        try:
            user_data = response.json()
            github_user = GithubUser(**user_data)
            return github_user.to_user_data()
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in user response", exc_info=e, stack_info=True)
            raise AuthError("Invalid user data response") from e
        except ValidationError as e:
            logger.error("Invalid user data schema", exc_info=e, stack_info=True)
            raise AuthError("Invalid user data format") from e
        except Exception as e:
            logger.error("Unexpected error", exc_info=e, stack_info=True)
            raise AuthError("Unexpected error") from e
