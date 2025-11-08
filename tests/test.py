import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from commands.ls import ls
from commands.cd import cd
from commands.cat import cat
from commands.cp import cp
from commands.mv import mv
from commands.rm import rm
from commands.zip_tar import zippig, unzipping, tarring, untarring
from core.parser import parse_command, route_command
from core.logger import setup_logging, log_command


class Test_MiniShell(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.create_test_structure()
        self.log_file = Path(self.test_dir) / "test_shell.log"

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_test_structure(self):
        (Path(self.test_dir) / "file1.txt").write_text("Hello World!\nLine 2")
        (Path(self.test_dir) / "file2.txt").write_text("Another file")
        (Path(self.test_dir) / "empty.txt").write_text("")
        subdir = Path(self.test_dir) / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("Nested content")
        deepdir = subdir / "deep"
        deepdir.mkdir()
        (deepdir / "deep_file.txt").write_text("Very deep")

    def test_parse_command_basic(self):
        result = parse_command("ls -l /home")
        self.assertEqual(result, ("ls", ["-l", "/home"], "ls -l /home"))

    def test_parse_command_empty(self):
        self.assertIsNone(parse_command(""))
        self.assertIsNone(parse_command("   "))

    def test_route_command(self):
        parsed = ("ls", ["-l"], "ls -l")
        result = route_command(parsed)
        self.assertEqual(result, ("file_ops", "ls", ["-l"], "ls -l"))

    def test_ls_current_dir(self):
        result = ls([])
        self.assertIn("file1.txt", result)
        self.assertIn("file2.txt", result)
        self.assertIn("subdir", result)

    def test_ls_with_path(self):
        result = ls(["subdir"])
        self.assertIn("nested.txt", result)
        self.assertIn("deep", result)

    def test_ls_detailed(self):
        result = ls(["-l"])
        lines = result.split('\n')
        self.assertTrue(any("file1.txt" in line for line in lines))

    def test_ls_nonexistent(self):
        result = ls(["nonexistent"])
        self.assertTrue("ERROR" in result)

    def test_cd_relative(self):
        result = cd(["subdir"])
        self.assertIsNone(result)
        self.assertTrue(Path("nested.txt").exists())

    def test_cd_nonexistent(self):
        result = cd(["nonexistent_dir"])
        self.assertTrue("ERROR" in result)

    def test_cat_file(self):
        result = cat(["file1.txt"])
        self.assertIn("Hello World", result)

    def test_cat_nonexistent(self):
        result = cat(["nonexistent.txt"])
        self.assertTrue("ERROR" in result)

    def test_cat_directory(self):
        result = cat(["subdir"])
        self.assertTrue("ERROR" in result)

    def test_cat_no_args(self):
        result = cat([])
        self.assertTrue("ERROR" in result)

    def test_cp_file(self):
        result = cp(["file1.txt", "file1_copy.txt"])
        self.assertIsNone(result)
        self.assertTrue(Path("file1_copy.txt").exists())
        self.assertEqual(Path("file1.txt").read_text(), Path("file1_copy.txt").read_text())

    def test_cp_directory_with_r(self):
        result = cp(["-r", "subdir", "subdir_copy"])
        self.assertIsNone(result)
        self.assertTrue(Path("subdir_copy").exists())
        self.assertTrue(Path("subdir_copy/nested.txt").exists())

    def test_cp_directory_without_r(self):
        result = cp(["subdir", "subdir_copy"])
        self.assertTrue("ERROR" in result)

    def test_mv_rename_file(self):
        result = mv(["file1.txt", "renamed.txt"])
        self.assertIsNone(result)
        self.assertFalse(Path("file1.txt").exists())
        self.assertTrue(Path("renamed.txt").exists())

    def test_mv_move_file(self):
        result = mv(["file1.txt", "subdir/"])
        self.assertIsNone(result)
        self.assertFalse(Path("file1.txt").exists())
        self.assertTrue(Path("subdir/file1.txt").exists())

    def test_rm_file(self):
        result = rm(["file1.txt"])
        self.assertIsNone(result)
        self.assertFalse(Path("file1.txt").exists())

    def test_rm_directory_with_r(self):
        import unittest.mock
        with unittest.mock.patch('builtins.input', return_value='y'):
            result = rm(["-r", "subdir"])
            self.assertIsNone(result)
        self.assertFalse(Path("subdir").exists())

    def test_rm_directory_without_r(self):
        result = rm(["subdir"])
        self.assertTrue("ERROR" in result)

    def test_rm_nonexistent(self):
        result = rm(["nonexistent.txt"])
        self.assertTrue("ERROR" in result)

    def test_zip_creation(self):
        result = zippig(["subdir", "test.zip"])
        self.assertIn("Created archive", result)
        self.assertTrue(Path("test.zip").exists())

    def test_unzip(self):
        zippig(["subdir", "test.zip"])
        result = unzipping(["test.zip"])
        self.assertIn("Extracted to", result)
        self.assertTrue(Path("test").exists())

    def test_tar_creation(self):
        result = tarring(["subdir", "test.tar.gz"])
        self.assertIn("Created archive", result)
        self.assertTrue(Path("test.tar.gz").exists())

    def test_untar(self):
        tarring(["subdir", "test.tar.gz"])
        result = untarring(["test.tar.gz"])
        self.assertIn("Extracted to", result)
        self.assertTrue(Path("test").exists())

    def test_logging(self):
        """Test that logging functions don't crash"""
        try:
            setup_logging(str(self.log_file))
            log_command("test command")
            log_command("error command", False, "test error")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Logging failed with exception: {e}")

    def test_integration_workflow(self):
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

    def test_cd_home(self):
        """Тест cd с домашней директорией"""
        result = cd(["~"])
        self.assertIsNone(result)

    def test_cd_no_args(self):
        """Тест cd без аргументов"""
        result = cd([])
        self.assertIsNone(result)

    def test_mv_multiple_files(self):
        """Тест перемещения нескольких файлов"""
        dest_dir = Path("destination")
        dest_dir.mkdir()
        result = mv(["file1.txt", "file2.txt", "destination/"])
        self.assertIsNone(result)
        self.assertTrue((dest_dir / "file1.txt").exists())
        self.assertTrue((dest_dir / "file2.txt").exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)


#pytest tests/test.py --cov=src --cov-report=term-missing
#для запуска анализа покрытия тестами
