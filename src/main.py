import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from core.parser import parse_command, route_command
from core.logger import setup_logging, log_command
from commands.ls import ls
from commands.zip_tar import zippig, unzipping, tarring, untarring
from commands.cd import cd
from commands.cat import cat
from commands.cp import cp
from commands.mv import mv
from commands.rm import rm


def main() -> None:
    """
    Главная функция мини-оболочки
    """
    setup_logging()

    print("<<< Dev1lan's Shell >>>\n")
    print("Доступные команды: ls, cd, cat, cp, mv, rm")
    print("Для выхода введите 'exit'")
    print("~" * 20)

    none_data_input_count = 0

    while True:
        try:
            user_input = input("\033[92mdev-1-lan:~₽\033[0m ").strip()
            parsed_data = parse_command(user_input)

            if parsed_data is None:
                none_data_input_count += 1
                if none_data_input_count == 20:
                    print("Хватит уже просто нажимать на Enter!!!")
                    none_data_input_count = 0
                    continue
                else:
                    continue

            else:
                none_data_input_count = 0
                command_pass, args_pass, raw_input = parsed_data
                log_command(raw_input)
                module, cmd_name, cmd_args, orig_input = route_command(parsed_data)

                if cmd_name == "exit":
                    print("Выход из мини-оболочки")
                    break

                if cmd_name == "mai":
                    koteki()

                result = do_command(module, cmd_name, cmd_args, orig_input)

                if result is not None:
                    print(result)

        except Exception as err:
            err_msg = f"Критическая ошибка: {err}"
            print(err_msg)
            if "raw_input" in locals():
                log_command(raw_input, False, err_msg)


def do_command(module: str, command: str, args: list[str], raw_input: str) -> str | None:
    """
    Выполнение команды

    Вход:
        module: str - имя модуля для выполнения
        command: str - название команды
        args: list[str] - список аргументов команды
        raw_input: str - оригинальная строка ввода

    Выход:
        str | None - результат выполнения команды или None
    """

    commands_map = {
        "ls": lambda: ls(args),
        "cat": lambda: cat(args),
        "cd": lambda: cd(args),
        "cp": lambda: cp(args),
        "mv": lambda: mv(args),
        "rm": lambda: rm(args),
        "zip": lambda: zippig(args),
        "unzip": lambda: unzipping(args),
        "tar": lambda: tarring(args),
        "untar": lambda: untarring(args),
    }

    error_log_commands = {"cd", "cp", "mv", "rm"}

    if command in commands_map:
        result = commands_map[command]()

        if command in error_log_commands and result is not None:
            log_command(raw_input, False, result)

        return str(result) if result is not None else None

    elif module == "core" and command == "unknown":
        err_msg = f"Неизвестная команда: {raw_input.split()[0]}"
        log_command(raw_input, False, err_msg)
        return err_msg

    return None


def koteki() -> None:
    """
    Функция для воспроизведения видео cats.mp4
    """
    video_path = "cats.mp4"
    cap = cv2.VideoCapture(video_path)
    print("Воспроизведение видео cats.mp4. \nНажмите 'q' для выхода.")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Cats Video", frame)
            if cv2.waitKey(25) & 0xFF == ord("q"):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
    # со звуком не смог запустить, но если что могу в лс скинуть видео


if __name__ == "__main__":
    main()
