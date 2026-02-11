from unittest import TestCase
from unittest.mock import MagicMock, patch, call

from migrations import (
    migrate_db,
    migrate_cosmos_db,
    migrate_postgres_up,
    migrate_postgres_down,
    run_alembic_command,
)
from src.schemas.common import EnvType


class TestMigrations(TestCase):
    @patch(
        "sys.argv",
        [
            "db_migration.py",
            "--env",
            "dev",
            "--db",
            "cosmos",
            "--appinsights",
            "test_connection_string",
        ],
    )
    @patch("migrations.CosmosDBCoreAdapter")
    def test_migrate_cosmos_db(self, mock_cosmos_db_adapter):
        mock_session = MagicMock()
        mock_cosmos_db_adapter.return_value = mock_session

        migrate_db()

        mock_cosmos_db_adapter.assert_called_once()
        mock_session.create_db.assert_called_once()
        self.assertEqual(mock_session.create_table.call_count, 7)

    def test_migrate_cosmos_db_function(self):
        logger = MagicMock()
        with patch("migrations.CosmosDBCoreAdapter") as mock_adapter:
            mock_session = MagicMock()
            mock_adapter.return_value = mock_session

            migrate_cosmos_db(EnvType.DEV, logger)

            mock_adapter.assert_called_once_with(EnvType.DEV, logger)
            mock_session.create_db.assert_called_once()
            self.assertEqual(mock_session.create_table.call_count, 7)
            logger.info.assert_called_with("CosmosDB migration completed successfully.")

    @patch("migrations.run_alembic_command")
    @patch("migrations.cleanup_old_backups")
    @patch("migrations.create_backup")
    def test_migrate_postgres_up_with_backup(
        self, mock_create_backup, mock_cleanup, mock_alembic
    ):
        mock_alembic.return_value = 0

        migrate_postgres_up("dev", "head", backup=True)

        mock_create_backup.assert_called_once_with("dev")
        mock_cleanup.assert_called_once_with(keep=10, env="dev")
        mock_alembic.assert_called_once_with(["upgrade", "head"], "dev")

    @patch("migrations.run_alembic_command")
    @patch("migrations.create_backup")
    def test_migrate_postgres_up_without_backup(self, mock_create_backup, mock_alembic):
        mock_alembic.return_value = 0

        migrate_postgres_up("dev", "head", backup=False)

        mock_create_backup.assert_not_called()
        mock_alembic.assert_called_once_with(["upgrade", "head"], "dev")

    @patch("migrations.run_alembic_command")
    @patch("migrations.cleanup_old_backups")
    @patch("migrations.create_backup")
    def test_migrate_postgres_down_with_backup(
        self, mock_create_backup, mock_cleanup, mock_alembic
    ):
        mock_alembic.return_value = 0

        migrate_postgres_down("dev", "-1", backup=True)

        mock_create_backup.assert_called_once_with("dev")
        mock_cleanup.assert_called_once_with(keep=10, env="dev")
        mock_alembic.assert_called_once_with(["downgrade", "-1"], "dev")

    @patch("subprocess.run")
    def test_run_alembic_command(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        result = run_alembic_command(["upgrade", "head"], "dev")

        self.assertEqual(result, 0)
        mock_run.assert_called_once()
