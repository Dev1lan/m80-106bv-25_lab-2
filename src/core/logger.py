import logging
from pathlib import Path


def setup_logging(log_file: str = "shell.log") -> None:
    """
    Настройка системы логирования

    Вход:
        log_file: str - путь к файлу лога (по умолчанию "shell.log")
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def log_command(command: str, success: bool = True, error_msg: str = "") -> None:
    """
    Логирование команды пользователя

    Вход:
        command: str - команда для логирования
        success: bool - успех выполнения (по умолчанию True)
        error_msg: str - сообщение об ошибке (по умолчанию "")
    """

    if success:
        logging.info(command)
    else:
        logging.error(f"{command} - ERROR: {error_msg}")
