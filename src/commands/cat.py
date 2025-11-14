from core.path_utils import resolve_path


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
        content = file_path.read_text(encoding="utf-8")
        return str(content)
    except Exception as err:
        return f"ERROR: {str(err)}"
