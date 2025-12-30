import argparse
import os

from src.adapters.db.cosmos_db_core import CosmosDBCoreAdapter
from src.helpers.logging import set_logger
from src.schemas.common import EnvType, TableName, TablePartitionKey


def migrate_db():
    parser = argparse.ArgumentParser(description="Migrate CosmosDB database and tables")
    parser.add_argument("--env", type=str, help="[prod, dev, test]")
    parser.add_argument(
        "--appinsights", type=str, help="Azure application insights connection string"
    )

    args = parser.parse_args()
    try:
        env = EnvType(args.env.lower())
        app_insights = args.appinsights
    except AttributeError as exc:
        raise ValueError("Missing env or appinsights argument") from exc
    except ValueError as exc:
        raise ValueError(f"Invalid env: {args.env}") from exc

    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = app_insights

    session = CosmosDBCoreAdapter(env, set_logger())
    session.create_db()
    tables = {
        TableName.RECEIPT: TablePartitionKey.RECEIPT,
        TableName.RECEIPT_URL: TablePartitionKey.RECEIPT_URL,
        TableName.SHOP: TablePartitionKey.SHOP,
        TableName.SHOP_ITEM: TablePartitionKey.SHOP_ITEM,
        TableName.USER: TablePartitionKey.USER,
        TableName.USER_IDENTITY: TablePartitionKey.USER_IDENTITY,
        TableName.USER_SESSION: TablePartitionKey.USER_SESSION,
    }
    for table, partition_key in tables.items():
        session.create_table(table, partition_key=partition_key)


if __name__ == "__main__":
    migrate_db()
