import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch

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
from src.core.path_utils import resolve_path, is_safe_path


class Test_MiniShell(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.create_test_structure()
        self.log_file = Path(self.test_dir) / "test_shell.log"

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        if os.name != 'nt':
            for attr in ['no_read_file', 'no_write_dir', 'no_access_dir']:
                if hasattr(self, attr):
                    item = getattr(self, attr)
                    if item.exists():
                        try:
                            item.chmod(0o755)
                        except (OSError, PermissionError):
                            pass
        shutil.rmtree(self.test_dir)

    def create_test_structure(self) -> None:
        (Path(self.test_dir) / "file1.txt").write_text("Hello World!\nLine 2")
        (Path(self.test_dir) / "file2.txt").write_text("Another file")
        (Path(self.test_dir) / "empty.txt").write_text("")
        (Path(self.test_dir) / "binary_file.bin").write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
        subdir = Path(self.test_dir) / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("Nested content")
        deepdir = subdir / "deep"
        deepdir.mkdir()
        (deepdir / "deep_file.txt").write_text("Very deep")

        if os.name != 'nt':
            # Файл без прав на чтение
            self.no_read_file = Path(self.test_dir) / "no_read.txt"
            self.no_read_file.write_text("secret")
            self.no_read_file.chmod(0o000)

            # Директория без прав на запись
            self.no_write_dir = Path(self.test_dir) / "no_write_dir"
            self.no_write_dir.mkdir()
            self.no_write_dir.chmod(0o555)

            # Директория без прав на доступ
            self.no_access_dir = Path(self.test_dir) / "no_access_dir"
            self.no_access_dir.mkdir()
            self.no_access_dir.chmod(0o000)

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
        self.assertTrue("ERROR" in str(result))

    def test_cd_relative(self) -> None:
        result = cd(["subdir"])
        self.assertIsNone(result)
        self.assertTrue(Path("nested.txt").exists())

    def test_cd_nonexistent(self) -> None:
        result = cd(["nonexistent_dir"])
        self.assertTrue("ERROR" in str(result))

    def test_cat_file(self) -> None:
        result = cat(["file1.txt"])
        self.assertIn("Hello World", result)

    def test_cat_nonexistent(self) -> None:
        result = cat(["nonexistent.txt"])
        self.assertTrue("ERROR" in str(result))

    def test_cat_directory(self) -> None:
        result = cat(["subdir"])
        self.assertTrue("ERROR" in str(result))

    def test_cat_no_args(self) -> None:
        result = cat([])
        self.assertTrue("ERROR" in str(result))

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
        self.assertTrue("ERROR" in str(result))

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
        self.assertTrue("ERROR" in str(result))

    def test_rm_nonexistent(self) -> None:
        result = rm(["nonexistent.txt"])
        self.assertTrue("ERROR" in str(result))

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

    def test_parse_command_with_quotes(self) -> None:
        """Тест парсинга команд с кавычками"""
        result = parse_command('ls -l "file with spaces"')
        self.assertEqual(result, ("ls", ["-l", "file with spaces"], 'ls -l "file with spaces"'))

    def test_parse_command_error(self) -> None:
        """Тест парсинга с ошибкой"""
        result = parse_command("ls 'unclosed quote")
        self.assertEqual(result[0], "error")
        self.assertIn("Parse error", result[1][0])

    def test_route_command_unknown(self) -> None:
        """Тест маршрутизации неизвестной команды"""
        parsed = ("unknown_cmd", [], "unknown_cmd")
        result = route_command(parsed)
        self.assertEqual(result, ("core", "unknown", [], "unknown_cmd"))

    def test_route_command_exit(self) -> None:
        """Тест маршрутизации команды exit"""
        parsed = ("exit", [], "exit")
        result = route_command(parsed)
        self.assertEqual(result, ("core", "exit", [], "exit"))

    def test_route_command_mai(self) -> None:
        """Тест маршрутизации команды mai"""
        parsed = ("mai", [], "mai")
        result = route_command(parsed)
        self.assertEqual(result, ("core", "mai", [], "mai"))

    def test_route_command_plugins(self) -> None:
        """Тест маршрутизации команд плагинов"""
        for cmd in ["zip", "unzip", "tar", "untar"]:
            parsed = (cmd, [], cmd)
            result = route_command(parsed)
            self.assertEqual(result, ("plugins", cmd, [], cmd))

    def test_cat_binary_file(self) -> None:
        """Тест cat с бинарным файлом"""
        result = cat(["binary_file.bin"])
        self.assertIn("BINARY FILE", result)

    def test_cat_permission_error(self) -> None:
        """Тест cat с файлом без прав доступа"""
        if os.name != 'nt':
            result = cat(["no_read.txt"])
            self.assertIn("ERROR", result)

    def test_cp_permission_error(self) -> None:
        """Тест cp с ошибкой прав доступа"""
        if os.name != 'nt':
            result = cp(["file1.txt", "no_write_dir/"])
            self.assertIn("ERROR", str(result))

    def test_cp_multiple_files(self) -> None:
        """Тест копирования нескольких файлов"""
        dest_dir = Path("dest_multi")
        dest_dir.mkdir()
        result = cp(["file1.txt", "file2.txt", "dest_multi"])
        self.assertEqual(result, "ERROR: Multiple sources require existing directory destination")
        self.assertFalse((dest_dir / "file1.txt").exists())
        self.assertFalse((dest_dir / "file2.txt").exists())

    def test_cp_invalid_args(self) -> None:
        """Тест cp с неверными аргументами"""
        result = cp([])
        self.assertIn("ERROR", str(result))

        result = cp(["-x", "file1.txt", "file2.txt"])
        self.assertIn("ERROR", str(result))

    def test_mv_permission_error(self) -> None:
        """Тест mv с ошибкой прав доступа"""
        if os.name != 'nt':
            result = mv(["file1.txt", "no_write_dir/"])
            self.assertIn("ERROR", str(result))

    def test_mv_invalid_args(self) -> None:
        """Тест mv с неверными аргументами"""
        result = mv([])
        self.assertIn("ERROR", str(result))

    def test_rm_cancel(self) -> None:
        """Тест отмены удаления директории"""
        with patch('builtins.input', return_value='n'):
            result = rm(["-r", "subdir"])
            self.assertIn("Cancelled", str(result))
            self.assertTrue(Path("subdir").exists())

    def test_zip_invalid_args(self) -> None:
        """Тест zip с неверными аргументами"""
        result = zippig([])
        self.assertIn("ERROR", result)

        result = zippig(["nonexistent", "archive.zip"])
        self.assertIn("ERROR", result)

    def test_unzip_invalid_args(self) -> None:
        """Тест unzip с неверными аргументами"""
        result = unzipping([])
        self.assertIn("ERROR", result)

        result = unzipping(["nonexistent.zip"])
        self.assertIn("ERROR", result)

    def test_tar_invalid_args(self) -> None:
        """Тест tar с неверными аргументами"""
        result = tarring([])
        self.assertIn("ERROR", result)

        result = tarring(["nonexistent", "archive.tar.gz"])
        self.assertIn("ERROR", result)

    def test_untar_invalid_args(self) -> None:
        """Тест untar с неверными аргументами"""
        result = untarring([])
        self.assertIn("ERROR", result)

        result = untarring(["nonexistent.tar.gz"])
        self.assertIn("ERROR", result)

    def test_path_utils_resolve_path(self) -> None:
        """Тест функции resolve_path"""
        result = resolve_path("file1.txt")
        self.assertEqual(result, Path(self.test_dir) / "file1.txt")

        result = resolve_path("nonexistent", must_be=False)
        self.assertIsNotNone(result)

        result = resolve_path("nonexistent", must_be=True)
        self.assertIsNone(result)

        result = resolve_path("~")
        self.assertEqual(result, Path.home())

    def test_path_utils_is_safe_path(self) -> None:
        """Тест функции is_safe_path"""
        self.assertTrue(is_safe_path(Path(self.test_dir)))

        # Корневая директория - небезопасна
        self.assertFalse(is_safe_path(Path("/")))

        # Родитель домашней директории - небезопасен
        self.assertFalse(is_safe_path(Path.home().parent))

    def test_route_command_error_parsing(self) -> None:
        """Тест маршрутизации ошибки парсинга"""
        parsed = ("error", ["Parse error"], "invalid input")
        result = route_command(parsed)
        self.assertEqual(result, ("core", "parse_error", ["Parse error"], "invalid input"))

    def test_ls_permission_error(self) -> None:
        """Тест ls с директорией без прав доступа"""
        if os.name != 'nt':
            result = ls(["no_access_dir"])
            self.no_access_dir.chmod(0o755)
            self.assertIn("ERROR", str(result))

    def test_cd_permission_error(self) -> None:
        """Тест cd с директорией без прав доступа"""
        if os.name != 'nt':
            result = cd(["no_access_dir"])
            self.no_access_dir.chmod(0o755)
            self.assertIn("ERROR", str(result))

    def test_cp_same_source_destination(self) -> None:
        """Тест копирования файла в самого себя"""
        result = cp(["file1.txt", "file1.txt"])
        self.assertIn("ERROR", str(result))

    def test_mv_same_source_destination(self) -> None:
        """Тест перемещения файла в самого себя"""
        result = mv(["file1.txt", "file1.txt"])
        self.assertIn("ERROR", str(result))

    def test_rm_safe_path(self) -> None:
        """Тест удаления системной директории"""
        result = rm(["-r", "/"])
        self.assertIn("ERROR", str(result))


if __name__ == "__main__":
    unittest.main(verbosity=2)


"""
pytest tests/test.py --cov=src --cov-report=term-missing
для запуска анализа покрытия тестами
"""

"""
python -m tests.test
для запуска тестов
"""
