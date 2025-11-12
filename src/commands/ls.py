import datetime
from pathlib import Path
from core.path_utils import resolve_path


def _parse_ls_args(args: list[str]) -> tuple[bool, str | None] | str:
    """
    Парсинг аргументов команды ls

    Вход:
        args: list[str] - список аргументов

    Выход:
        tuple[bool, str | None] | str - (detailed, path) или строка с ошибкой
    """

    detailed = False
    path = None

    for arg in args:
        if arg.startswith('-'):
            if arg == '-l':
                detailed = True
            else:
                return f"ERROR: Incorrect option {arg}"
        else:
            path = arg

    return detailed, path


def ls(args: list[str]) -> str:
    """
    Главная функция команды ls

    Вход:
        args: list[str] - список аргументов ["-l", "/path"] | [".."] | []

    Выход:
        str - отформатированная строка для вывода
    """

    parsed_args = _parse_ls_args(args)
    if isinstance(parsed_args, str):
        return parsed_args

    detailed, path = parsed_args

    goal_path = resolve_path(path, must_be=True, must_dir=True)
    if goal_path is None:
        return "ERROR: Path does not exist or is not a directory"

    try:
        items = list(goal_path.iterdir())
        items.sort(key=lambda x: x.name.lower())
    except PermissionError:
        return "ERROR: Permission denied"

    if detailed:
        return _format_detailed_list(items)
    else:
        return _format_simple_list(items)


def _format_simple_list(items: list[Path]) -> str:
    """
    Простой формат вывода: каждое имя с новой строки

    Вход:
        items: list[Path] - список элементов для вывода

    Выход:
        str - отформатированная строка с именами
    """

    names = [item.name for item in items]
    return "\n".join(names)


def _format_detailed_list(items: list[Path]) -> str:
    """
    Подробный формат: тип, размер, дата, имя

    Вход:
        items: list[Path] - список элементов для вывода

    Выход:
        str - отформатированная строка с детальной информацией
    """

    lines = []
    for item in items:
        stat_info = item.stat()
        file_type = "d" if item.is_dir() else "-"
        size = stat_info.st_size
        mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime)
        date_str = mtime.strftime("%Y-%m-%d %H:%M")
        name = item.name

        if item.is_dir():
            name = name + "/"

        lines.append(f"{file_type} {size:8} {date_str} {name}")

    return "\n".join(lines)
