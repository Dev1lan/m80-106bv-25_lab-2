from pathlib import Path
from core.path_utils import resolve_path, is_safe_path


def mv(args: list[str]) -> None | str:
    """
    Команда mv - перемещение или переименование файлов/каталогов

    Вход:
        args: list[str] - список аргументов ["source", "dest"] | ["file1", "file2", "dest_dir"]

    Выход:
        None | str - None при успехе, строка с ошибкой при fail
    """

    if len(args) < 2:
        return "ERROR: 'mv' requires source and destination"

    sources = args[:-1]
    destination = args[-1]

    if len(sources) > 1:
        destination_path = resolve_path(destination, must_be=True, must_dir=True)
        if destination_path is None:
            return "ERROR: Multiple sources require existing directory destination"

    errors = []
    for source in sources:
        result = _move_item(source, destination)
        if result is not None:
            errors.append(result)

    if errors:
        return "\n".join(errors)
    return None


def _move_item(source: str, destination: str) -> None | str:
    """
    Перемещает один элемент (файл или директорию)

    Вход:
        source: str - путь к источнику
        destination: str - путь к назначению

    Выход:
        None | str - None при успехе, строка с ошибкой при fail
    """

    source_path = resolve_path(source, must_be=True)
    destination_path = resolve_path(destination, must_be=False)

    if source_path is None:
        return f"ERROR: Source '{source}' does not exist"

    if not is_safe_path(source_path):
        return f"ERROR: Cannot move system directory '{source}'"

    if destination_path.exists() and destination_path.is_dir():
        destination_path = destination_path / source_path.name

    if source_path == destination_path:
        return "ERROR: Source and destination are the same"

    if source_path.is_dir():
        try:
            if destination_path.is_relative_to(source_path):
                return "ERROR: Cannot move directory into itself"
        except ValueError:
            pass

    parent_dir = resolve_path(str(destination_path.parent), must_be=True, must_dir=True)
    if parent_dir is None:
        return f"ERROR: Destination directory '{destination_path.parent}' does not exist"

    try:
        if destination_path.exists():
            if source_path.is_file() and destination_path.is_file():
                destination_path.unlink()
                source_path.rename(destination_path)
            elif source_path.is_dir() and destination_path.is_dir():
                _recurs_merge_directories(source_path, destination_path)
            else:
                return f"ERROR: Cannot overwrite {destination_path.name} with different type"
        else:
            source_path.rename(destination_path)

    except Exception as e:
        return f"ERROR: {str(e)}"

    return None


def _recurs_merge_directories(source_dir: Path, dest_dir: Path) -> None:
    """
    Рекурсивно объединяет две директории

    Вход:
        source_dir: Path - исходная директория
        dest_dir: Path - целевая директория
    """

    for item in source_dir.iterdir():
        destination_item = dest_dir / item.name

        if item.is_file():
            if destination_item.exists():
                destination_item.unlink()
            item.rename(destination_item)
        elif item.is_dir():
            if not destination_item.exists():
                destination_item.mkdir()
            _recurs_merge_directories(item, destination_item)

    source_dir.rmdir()
