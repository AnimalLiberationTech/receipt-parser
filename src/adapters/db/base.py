from abc import ABC, abstractmethod
from typing import Any, Dict, Self, List

from src.schemas.common import EnvType, TableName


class BaseDBAdapter(ABC):
    @abstractmethod
    def __init__(self, env: EnvType, logger):
        self.env = env
        self.logger = logger

    @abstractmethod
    def use_db(self, db_name: str) -> Self:
        pass

    @abstractmethod
    def use_table(self, table_name: TableName) -> Self:
        pass

    @abstractmethod
    def create_one(self, data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def create_or_update_one(self, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def read_one(self, _id: str, **kwargs) -> Dict[str, Any] | None:
        pass

    @abstractmethod
    def read_many(
        self, where: Dict[str, Any] | None = None, limit: int | None = None, **kwargs
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_one(self, _id: str, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def delete_one(self, _id: str, **kwargs) -> bool:
        pass

    @abstractmethod
    def create_db(self) -> Self:
        pass

    @abstractmethod
    def create_table(self, table_name: TableName, **kwargs) -> Self:
        pass

    @abstractmethod
    def drop_table(self, table_name: TableName) -> None:
        pass

    @abstractmethod
    def drop_db(self) -> None:
        pass
