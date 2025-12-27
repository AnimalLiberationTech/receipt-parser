from unittest import TestCase
from unittest.mock import MagicMock, patch, ANY

from src.migrations import migrate_db
from src.schemas.common import EnvType


class TestMigrations(TestCase):
    @patch("src.migrations.os.environ.get")
    @patch("src.migrations.CosmosDBCoreAdapter")
    def test_migrate_db(self, mock_cosmos_db_core_adapter, mock_os_environ_get):
        mock_os_environ_get.return_value = "DEV"

        mock_session = MagicMock()
        mock_cosmos_db_core_adapter.return_value = mock_session

        migrate_db()

        mock_os_environ_get.assert_called_once_with("ENV_NAME", EnvType.DEV)
        mock_cosmos_db_core_adapter.assert_called_once_with("DEV", ANY)
        mock_session.create_db.assert_called_once()
        self.assertEqual(mock_session.create_table.call_count, 6)
