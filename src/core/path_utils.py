from pathlib import Path

def resolve_path(path_arg: str, must_be: bool = True, must_dir: bool = False, must_file: bool = False):
    """
    Универсальная функция разрешения путей

    Вход:
        path_arg: str | None - строка пути или None
        must_be: bool - должен ли путь существовать (по умолчанию True)
        must_dir: bool - должен ли быть директорией (по умолчанию False)
        must_file: bool - должен ли быть файлом (по умолчанию False)

    Выход:
        Path | None - Path объект или None если путь невалидный
    """

    if isinstance(path_arg, Path):
        path = path_arg
    if path_arg is None:
        path = Path.cwd()
    elif path_arg == "~":
        path = Path.home()
    elif path_arg.startswith("~/"):
        path = Path.home() / path_arg[2:]
    else:
        path = Path(path_arg)

    if not path.is_absolute():
        path = Path.cwd() / path

    if must_be and not path.exists():
        return None

    if must_dir and not path.is_dir():
        return None

    if must_file and not path.is_file():
        return None

    return path


def is_safe_path(path: Path) -> bool:
    """
    Проверка безопасности пути (не система)

    Вход:
        path: Path - путь для проверки

    Выход:
        bool - True если путь безопасен, False если системный
    """

    safe_path = path.resolve()
    forbidden_paths = [Path("/"), Path.home().parent]
    return safe_path not in forbidden_paths
