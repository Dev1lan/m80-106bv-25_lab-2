import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.commands.ls import ls
from src.commands.cd import cd
from src.commands.cat import cat
from src.commands.cp import cp
from src.commands.mv import mv
from src.commands.rm import rm
from src.commands.zip_tar import zippig, unzipping, tarring, untarring
from src.core.parser import parse_command, route_command
from src.core.logger import setup_logging, log_command


class Test_MiniShell(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.create_test_structure()
        self.log_file = Path(self.test_dir) / "test_shell.log"

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_test_structure(self) -> None:
        (Path(self.test_dir) / "file1.txt").write_text("Hello World!\nLine 2")
        (Path(self.test_dir) / "file2.txt").write_text("Another file")
        (Path(self.test_dir) / "empty.txt").write_text("")
        subdir = Path(self.test_dir) / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("Nested content")
        deepdir = subdir / "deep"
        deepdir.mkdir()
        (deepdir / "deep_file.txt").write_text("Very deep")

    def test_parse_command_basic(self) -> None:
        result = parse_command("ls -l /home")
        self.assertEqual(result, ("ls", ["-l", "/home"], "ls -l /home"))

    def test_parse_command_empty(self) -> None:
        self.assertIsNone(parse_command(""))
        self.assertIsNone(parse_command("   "))

    def test_route_command(self) -> None:
        parsed = ("ls", ["-l"], "ls -l")
        result = route_command(parsed)
        self.assertEqual(result, ("file_ops", "ls", ["-l"], "ls -l"))

    def test_ls_current_dir(self) -> None:
        result = ls([])
        self.assertIn("file1.txt", result)
        self.assertIn("file2.txt", result)
        self.assertIn("subdir", result)

    def test_ls_with_path(self) -> None:
        result = ls(["subdir"])
        self.assertIn("nested.txt", result)
        self.assertIn("deep", result)

    def test_ls_detailed(self) -> None:
        result = ls(["-l"])
        lines = result.split("\n")
        self.assertTrue(any("file1.txt" in line for line in lines))

    def test_ls_nonexistent(self) -> None:
        result = ls(["nonexistent"])
        self.assertTrue("ERROR" in result)

    def test_cd_relative(self) -> None:
        result = cd(["subdir"])
        self.assertIsNone(result)
        self.assertTrue(Path("nested.txt").exists())

    def test_cd_nonexistent(self) -> None:
        result = cd(["nonexistent_dir"])
        self.assertTrue("ERROR" in result)

    def test_cat_file(self) -> None:
        result = cat(["file1.txt"])
        self.assertIn("Hello World", result)

    def test_cat_nonexistent(self) -> None:
        result = cat(["nonexistent.txt"])
        self.assertTrue("ERROR" in result)

    def test_cat_directory(self) -> None:
        result = cat(["subdir"])
        self.assertTrue("ERROR" in result)

    def test_cat_no_args(self) -> None:
        result = cat([])
        self.assertTrue("ERROR" in result)

    def test_cp_file(self) -> None:
        result = cp(["file1.txt", "file1_copy.txt"])
        self.assertIsNone(result)
        self.assertTrue(Path("file1_copy.txt").exists())
        self.assertEqual(
            Path("file1.txt").read_text(), Path("file1_copy.txt").read_text()
        )

    def test_cp_directory_with_r(self) -> None:
        result = cp(["-r", "subdir", "subdir_copy"])
        self.assertIsNone(result)
        self.assertTrue(Path("subdir_copy").exists())
        self.assertTrue(Path("subdir_copy/nested.txt").exists())

    def test_cp_directory_without_r(self) -> None:
        result = cp(["subdir", "subdir_copy"])
        self.assertTrue("ERROR" in result)

    def test_mv_rename_file(self) -> None:
        result = mv(["file1.txt", "renamed.txt"])
        self.assertIsNone(result)
        self.assertFalse(Path("file1.txt").exists())
        self.assertTrue(Path("renamed.txt").exists())

    def test_mv_move_file(self) -> None:
        result = mv(["file1.txt", "subdir/"])
        self.assertIsNone(result)
        self.assertFalse(Path("file1.txt").exists())
        self.assertTrue(Path("subdir/file1.txt").exists())

    def test_rm_file(self) -> None:
        result = rm(["file1.txt"])
        self.assertIsNone(result)
        self.assertFalse(Path("file1.txt").exists())

    def test_rm_directory_with_r(self) -> None:
        import unittest.mock

        with unittest.mock.patch("builtins.input", return_value="y"):
            result = rm(["-r", "subdir"])
            self.assertIsNone(result)
        self.assertFalse(Path("subdir").exists())

    def test_rm_directory_without_r(self) -> None:
        result = rm(["subdir"])
        self.assertTrue("ERROR" in result)

    def test_rm_nonexistent(self) -> None:
        result = rm(["nonexistent.txt"])
        self.assertTrue("ERROR" in result)

    def test_zip_creation(self) -> None:
        result = zippig(["subdir", "test.zip"])
        self.assertIn("Created archive", result)
        self.assertTrue(Path("test.zip").exists())

    def test_unzip(self) -> None:
        zippig(["subdir", "test.zip"])
        result = unzipping(["test.zip"])
        self.assertIn("Extracted to", result)
        self.assertTrue(Path("test").exists())

    def test_tar_creation(self) -> None:
        result = tarring(["subdir", "test.tar.gz"])
        self.assertIn("Created archive", result)
        self.assertTrue(Path("test.tar.gz").exists())

    def test_untar(self) -> None:
        tarring(["subdir", "test.tar.gz"])
        result = untarring(["test.tar.gz"])
        self.assertIn("Extracted to", result)
        self.assertTrue(Path("test").exists())

    def test_logging(self) -> None:
        """Test that logging functions don't crash"""
        try:
            setup_logging(str(self.log_file))
            log_command("test command")
            log_command("error command", False, "test error")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Logging failed with exception: {e}")

    def test_integration_workflow(self) -> None:
        Path("data.txt").write_text("test data")
        result = cp(["data.txt", "backup.txt"])
        self.assertIsNone(result)
        result = mv(["backup.txt", "renamed.txt"])
        self.assertIsNone(result)
        archive_dir = Path("archive_src")
        archive_dir.mkdir()
        (archive_dir / "file.txt").write_text("archive content")
        result = zippig(["archive_src", "project.zip"])
        self.assertIn("Created archive", result)
        self.assertTrue(Path("project.zip").exists())

    def test_cd_home(self) -> None:
        """Тест cd с домашней директорией"""
        result = cd(["~"])
        self.assertIsNone(result)

    def test_cd_no_args(self) -> None:
        """Тест cd без аргументов"""
        result = cd([])
        self.assertIsNone(result)

    def test_mv_multiple_files(self) -> None:
        """Тест перемещения нескольких файлов"""
        dest_dir = Path("destination")
        dest_dir.mkdir()
        result = mv(["file1.txt", "file2.txt", "destination/"])
        self.assertIsNone(result)
        self.assertTrue((dest_dir / "file1.txt").exists())
        self.assertTrue((dest_dir / "file2.txt").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)


"""pytest tests/test.py --cov=src --cov-report=term-missing
для запуска анализа покрытия тестами
"""

"""
python -m tests.test
для запуска тестов
"""
