import os
from pathlib import Path
from core.path_utils import resolve_path


def cd(args: list[str]) -> None | str:
    """
    Команда cd - смена рабочей директории

    Вход:
        args: list[str] - список аргументов ['/path'] | ['..'] | ['~'] | []

    Выход:
        None | str - None при успехе; строка с ошибкой при fail
    """

    if len(args) == 0:
        goal_path = Path.cwd()
    else:
        goal_path = resolve_path(args[0], must_be=True, must_dir=True)

    if goal_path is None:
        return "ERROR: Directory does not exist or is not a directory"

    try:
        os.chdir(goal_path)
        return None
    except Exception as err:
        return f"ERROR: {str(err)}"
