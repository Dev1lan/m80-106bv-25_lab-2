import shutil
from typing import Optional, Union, Tuple, List
from src.core.path_utils import resolve_path


def _parse_cp_args(args: list[str]) -> Union[Tuple[List[str], str, bool], str]:
    """
    Парсинг аргументов команды cp

    Вход:
        args: list[str] - список аргументов

    Выход:
        tuple[list[str], str, bool] | str - (sources, destination, recursive) или строка с ошибкой
    """

    sources: list[str] = []
    recurs = False
    destination = None

    for arg in args:
        if arg.startswith("-"):
            if arg == "-r":
                recurs = True
            else:
                return f"ERROR: Incorrect option {arg}"
        else:
            if destination is None and sources:
                destination = arg
            else:
                sources.append(arg)

    if not sources or destination is None:
        return "ERROR: 'cp' requires source and destination"

    return sources, destination, recurs


def cp(args: list[str]) -> Optional[str]:
    """
    Команда cp - копирование файлов и директорий

    Вход:
        args: list[str] - список аргументов ["source", "dest"] | ["-r", "source", "dest"]

    Выход:
        None | str - None при успехе; строка с ошибкой при fail
    """

    if len(args) < 2:
        return "ERROR: 'cp' requires source and destination"

    parsed_args = _parse_cp_args(args)
    if isinstance(parsed_args, str):
        return parsed_args

    sources, destination, recurs = parsed_args

    if len(sources) > 1:
        destination_path = resolve_path(destination, must_be=True, must_dir=True)
        if destination_path is None:
            return "ERROR: Multiple sources require existing directory destination"

    errors = []
    for source in sources:
        result = _copy_item(source, destination, recurs)
        if result is not None:
            errors.append(result)

    if errors:
        return "\n".join(errors)
    return None


def _copy_item(source: str, destination: str, recursive: bool) -> Optional[str]:
    """
    Копирует один элемент (файл или директорию)

    Вход:
        source: str - путь к источнику
        destination: str - путь к назначению
        recursive: bool - флаг рекурсивного копирования

    Выход:
        None | str - None при успехе; строка с ошибкой при fail
    """

    source_path = resolve_path(source, must_be=True)
    destination_path = resolve_path(destination, must_be=False)

    if source_path is None:
        return f"ERROR: Source '{source}' does not exist"

    if destination_path is None:
        return f"ERROR: Invalid destination path '{destination}'"

    if destination_path.exists() and destination_path.is_dir():
        destination_path = destination_path / source_path.name

    if source_path == destination_path:
        return "ERROR: Source and destination are the same"

    if recursive and source_path.is_dir():
        try:
            if destination_path.is_relative_to(source_path):
                return "ERROR: Cannot copy directory into itself"
        except ValueError:
            pass

    try:
        if source_path.is_file():
            shutil.copy2(source_path, destination_path)
        elif source_path.is_dir():
            if recursive:
                shutil.copytree(source_path, destination_path)
            else:
                return f"ERROR: '{source}' is a directory (use -r)"
        else:
            return f"ERROR: '{source}' is not a file or directory"

    except (shutil.Error, OSError, IOError, PermissionError) as err:
        return f"ERROR: {str(err)}"

    return None
