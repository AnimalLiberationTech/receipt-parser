import os
from psycopg2 import connect
from psycopg2.extras import RealDictCursor, Json
from typing import Any, Dict, List, Self

from src.adapters.db.base import BaseDBAdapter
from src.schemas.common import EnvType, TableName


class PostgreSQLCoreAdapter(BaseDBAdapter):
    def __init__(self, env: EnvType, logger):
        super().__init__(env, logger)
        self.connection = connect(
            host=os.environ.get(f"{env.upper()}_POSTGRES_HOST", "localhost"),
            port=os.environ.get(f"{env.upper()}_POSTGRES_PORT", "5432"),
            database=os.environ.get(f"{env.upper()}_POSTGRES_DB", "postgres"),
            user=os.environ.get(f"{env.upper()}_POSTGRES_USER", "postgres"),
            password=os.environ.get(f"{env.upper()}_POSTGRES_PASSWORD", "postgres"),
        )
        self.connection.autocommit = True
        self.current_table = None
        self.current_db = None

    def use_db(self, db_name: str) -> Self:
        # In Postgres, switching DB usually requires reconnecting,
        # but here we might just be setting a schema or ignoring if DB is set in connection.
        # For simplicity, we assume the DB is set in connection, or we just track it.
        self.current_db = db_name
        return self

    def use_table(self, table_name: TableName) -> Self:
        self.current_table = table_name
        return self

    def create_one(self, data: Dict[str, Any]) -> str:
        if not self.current_table:
            raise ValueError("Table not selected. Use use_table() first.")

        _id = data.get("id")
        if not _id:
            # If ID is not provided, we might need to generate it or let DB generate it.
            # Assuming data should have an ID or we generate one.
            # For consistency with Cosmos adapter which returns ID.
            import uuid

            _id = str(uuid.uuid4())
            data["id"] = _id

        with self.connection.cursor() as cursor:
            query = f"INSERT INTO {self.current_table} (id, data) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING RETURNING id"
            cursor.execute(query, (_id, Json(data)))
            result = cursor.fetchone()
            return result[0] if result else _id

    def create_or_update_one(self, data: Dict[str, Any]) -> bool:
        if not self.current_table:
            raise ValueError("Table not selected. Use use_table() first.")

        _id = data.get("id")
        if not _id:
            raise ValueError("ID is required for create_or_update_one")

        with self.connection.cursor() as cursor:
            query = f"""
                INSERT INTO {self.current_table} (id, data) 
                VALUES (%s, %s) 
                ON CONFLICT (id) 
                DO UPDATE SET data = EXCLUDED.data
            """
            cursor.execute(query, (_id, Json(data)))
            return True

    def read_one(self, _id: str, **kwargs) -> Dict[str, Any] | None:
        if not self.current_table:
            raise ValueError("Table not selected. Use use_table() first.")

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"SELECT data FROM {self.current_table} WHERE id = %s"
            cursor.execute(query, (_id,))
            result = cursor.fetchone()
            if result:
                return result["data"]
            return None

    def read_many(
        self, where: Dict[str, Any] | None = None, limit: int | None = None, **kwargs
    ) -> List[Dict[str, Any]]:
        if not self.current_table:
            raise ValueError("Table not selected. Use use_table() first.")

        query = f"SELECT data FROM {self.current_table}"
        params = []

        if where:
            conditions = []
            for key, value in where.items():
                # Assuming simple equality check on JSON fields
                conditions.append(f"data->>%s = %s")
                params.extend([key, str(value)])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            return [row["data"] for row in results]

    def update_one(self, _id: str, data: Dict[str, Any]) -> bool:
        if not self.current_table:
            raise ValueError("Table not selected. Use use_table() first.")

        with self.connection.cursor() as cursor:
            # This is a full replacement of data for the given ID, similar to Cosmos replace
            query = f"UPDATE {self.current_table} SET data = %s WHERE id = %s"
            cursor.execute(query, (Json(data), _id))
            return cursor.rowcount > 0

    def delete_one(self, _id: str, **kwargs) -> bool:
        if not self.current_table:
            raise ValueError("Table not selected. Use use_table() first.")

        with self.connection.cursor() as cursor:
            query = f"DELETE FROM {self.current_table} WHERE id = %s"
            cursor.execute(query, (_id,))
            return cursor.rowcount > 0

    def create_table(self, table_name: TableName, **kwargs) -> Self:
        # Creating a table with id and jsonb data column
        with self.connection.cursor() as cursor:
            query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id TEXT PRIMARY KEY,
                    data JSONB
                )
            """
            cursor.execute(query)
        return self

    def drop_table(self, table_name: TableName) -> None:
        with self.connection.cursor() as cursor:
            query = f"DROP TABLE IF EXISTS {table_name}"
            cursor.execute(query)


def init_db_session(logger) -> PostgreSQLCoreAdapter:
    env_name = os.environ["ENV_NAME"]
    db_name = os.environ[f"{env_name.upper()}_POSTGRES_DB"]
    return PostgreSQLCoreAdapter(EnvType(env_name), logger).use_db(db_name)
