import shlex


def parse_command(user_input: str) -> tuple[str, list[str], str] | None:
    """
    Основной метод парсинга пользовательского ввода

    Вход:
        user_input: str - строка ввода от пользователя

    Выход:
        tuple[str, list[str], str] | None - кортеж (команда, аргументы, оригинальный ввод)
        или None при пустом вводе
    """

    if not user_input or not user_input.strip():
        return None

    raw_input = user_input.strip()

    try:
        parts = shlex.split(raw_input)
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        return (command, args, raw_input)

    except ValueError as err:
        return ("error", [f"Parse error: {err}"], raw_input)


def route_command(
    parsed_data: tuple[str, list[str], str],
) -> tuple[str, str, list[str], str]:
    """
    Маршрутизатор команд - определяет модуль для выполнения команды

    Вход:
        parsed_data: tuple[str, list[str], str] - разобранные данные (команда, аргументы, оригинальный ввод)

    Выход:
        tuple[str, str, list[str], str] - кортеж (имя_модуля, команда, аргументы, оригинальный ввод)
    """

    command, args, raw_input = parsed_data

    if command == "error":
        return ("core", "parse_error", args, raw_input)

    match command:
        case "ls" | "cd" | "cat" | "cp" | "mv" | "rm":
            return ("file_ops", command, args, raw_input)

        case "zip" | "unzip" | "tar" | "untar":
            return ("plugins", command, args, raw_input)

        case "exit" | "EXIT":
            return ("core", "exit", args, raw_input)

        case "mai" | "MAI":
            return ("core", "mai", args, raw_input)

        case _:
            return ("core", "unknown", args, raw_input)
