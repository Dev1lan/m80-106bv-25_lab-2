from src.core.path_utils import resolve_path

def cat(args: list[str]) -> str:
    """
    Команда cat - вывод содержимого файла

    Вход:
        args: list[str] - список аргументов ['file.txt'] | ['/path/file.txt']

    Выход:
        str - содержимое файла | строка с ошибкой
    """

    if len(args) == 0:
        return "ERROR: 'cat' requires filename"

    file_path = resolve_path(args[0], must_be=True, must_file=True)

    if file_path is None:
        return f"ERROR: File '{args[0]}' does not exist or is not a file"

    try:
        content = file_path.read_text(encoding='utf-8')
        return content

    except UnicodeDecodeError:
        file_size = file_path.stat().st_size
        return f"BINARY FILE: {file_path.name} ({file_size} bytes)\nUse specialized tools to view binary files"

    except (PermissionError, IOError, OSError) as err:
        return f"ERROR: {str(err)}"
