import shutil
from src.core.path_utils import resolve_path, is_safe_path


def rm(args: list[str]) -> None | str:
    """
    Команда rm - удаление файлов и директорий

    Вход:
        args: list[str] - список аргументов ["file"] | ["-r", "dir"] | ["-r", "file1", "file2"]

    Выход:
        None | str - None при успехе, строка с ошибкой при fail
    """

    if len(args) == 0:
        return "ERROR: 'rm' requires at least one argument"

    recursive = False
    purposes = []

    for arg in args:
        if arg.startswith("-"):
            if "-r" == arg:
                recursive = True
            else:
                return f"ERROR: Incorrect option {arg}"
        else:
            purposes.append(arg)

    if not purposes:
        return "ERROR: No targets specified"

    errors = []
    for target in purposes:
        result = _remove_item(target, recursive)
        if result is not None:
            errors.append(result)

    if errors:
        return "\n".join(errors)
    return None


def _remove_item(target: str, recursive: bool) -> None | str:
    """
    Удаляет один элемент (файл или директорию)

    Вход:
        target: str - цель для удаления
        recursive: bool - флаг рекурсивного удаления

    Выход:
        None | str - None при успехе, строка с ошибкой при fail
    """

    goal_path = resolve_path(target, must_be=True)

    if goal_path is None:
        return f"ERROR: '{target}' does not exist"

    if not is_safe_path(goal_path):
        return f"ERROR: Cannot remove system directory '{target}'"

    if goal_path.is_dir():
        if not recursive:
            return f"ERROR: '{target}' is a directory (use -r)"

        if not _confirm_deletion(target):
            return f"Cancelled: '{target}'"

    try:
        if goal_path.is_file():
            goal_path.unlink()
        elif goal_path.is_dir():
            if recursive:
                shutil.rmtree(goal_path)
            else:
                return f"ERROR: '{target}' is a directory (use -r)"
        else:
            return f"ERROR: '{target}' is not a file or directory"

    except Exception as err:
        return f"ERROR: {str(err)}"

    return None


def _confirm_deletion(target_name: str) -> bool:
    """
    Запрашивает подтверждение удаления директории

    Вход:
        target_name: str - имя цели для удаления

    Выход:
        bool - True если подтверждено, False если отменено
    """

    print(f"Remove directory '{target_name}'? (y/n): ", end="", flush=True)

    try:
        response = input().strip().lower()
        return response in ["y", "yes"]
    except (EOFError, KeyboardInterrupt):
        print("\nCancel")
        return False
