import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from db_backup import (
    get_db_config,
    create_backup,
    list_backups,
    cleanup_old_backups,
)


class TestDbBackup(TestCase):
    def test_get_db_config(self):
        with patch.dict(
            os.environ,
            {
                "DEV_POSTGRES_HOST": "testhost",
                "DEV_POSTGRES_PORT": "5433",
                "DEV_POSTGRES_DB": "testdb",
                "DEV_POSTGRES_USER": "testuser",
                "DEV_POSTGRES_PASSWORD": "testpass",
            },
        ):
            config = get_db_config("dev")
            self.assertEqual(config["host"], "testhost")
            self.assertEqual(config["port"], "5433")
            self.assertEqual(config["database"], "testdb")
            self.assertEqual(config["user"], "testuser")
            self.assertEqual(config["password"], "testpass")

    def test_get_db_config_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = get_db_config("dev")
            self.assertEqual(config["host"], "localhost")
            self.assertEqual(config["port"], "5432")
            self.assertEqual(config["database"], "postgres")
            self.assertEqual(config["user"], "postgres")
            self.assertEqual(config["password"], "postgres")

    @patch("subprocess.run")
    def test_create_backup(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(
                os.environ,
                {
                    "DEV_POSTGRES_HOST": "localhost",
                    "DEV_POSTGRES_PORT": "5432",
                    "DEV_POSTGRES_DB": "testdb",
                    "DEV_POSTGRES_USER": "testuser",
                    "DEV_POSTGRES_PASSWORD": "testpass",
                },
            ):
                backup_file = create_backup("dev", backup_dir=tmpdir)
                self.assertTrue(backup_file.startswith(tmpdir))
                self.assertTrue(backup_file.endswith(".sql"))
                mock_run.assert_called_once()

    def test_list_backups(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test backup files
            Path(tmpdir, "testdb_dev_20260101_120000.sql").touch()
            Path(tmpdir, "testdb_dev_20260102_120000.sql").touch()
            Path(tmpdir, "testdb_prod_20260101_120000.sql").touch()

            all_backups = list_backups(tmpdir)
            self.assertEqual(len(all_backups), 3)

            dev_backups = list_backups(tmpdir, env="dev")
            self.assertEqual(len(dev_backups), 2)

            prod_backups = list_backups(tmpdir, env="prod")
            self.assertEqual(len(prod_backups), 1)

    def test_list_backups_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backups = list_backups(tmpdir)
            self.assertEqual(len(backups), 0)

    def test_list_backups_nonexistent_dir(self):
        backups = list_backups("/nonexistent/path")
        self.assertEqual(len(backups), 0)

    def test_cleanup_old_backups(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test backup files
            files = [
                "testdb_dev_20260101_120000.sql",
                "testdb_dev_20260102_120000.sql",
                "testdb_dev_20260103_120000.sql",
                "testdb_dev_20260104_120000.sql",
                "testdb_dev_20260105_120000.sql",
            ]
            for f in files:
                Path(tmpdir, f).touch()

            # Keep only 2 backups
            cleanup_old_backups(tmpdir, keep=2, env="dev")

            remaining = list_backups(tmpdir, env="dev")
            self.assertEqual(len(remaining), 2)
            # Should keep the most recent ones
            self.assertTrue(remaining[0].endswith("20260105_120000.sql"))
            self.assertTrue(remaining[1].endswith("20260104_120000.sql"))
