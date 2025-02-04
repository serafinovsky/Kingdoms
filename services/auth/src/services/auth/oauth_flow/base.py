from abc import ABC, abstractmethod

from schemas.auth import UserData


class AuthFlow(ABC):
    @abstractmethod
    def authorize_url(self) -> str:
        pass

    @abstractmethod
    async def process_response(self, code: str) -> UserData:
        pass
