import shutil
from core.path_utils import resolve_path


def zippig(args: list[str]) -> str:
    """
    Команда zip - создание ZIP архива

    Вход:
        args: list[str] - список аргументов ["folder", "archive.zip"]

    Выход:
        str - строка результата или ошибки
    """

    if len(args) != 2:
        return "ERROR: zip requires folder and archive name"

    folder = args[0]
    archive_name = args[1]

    folder_path = resolve_path(folder, must_be=True, must_dir=True)
    if folder_path is None:
        return f"ERROR: Folder '{folder}' does not exist"

    if not archive_name.endswith(".zip"):
        archive_name += ".zip"

    archive_path = resolve_path(archive_name, must_be=False)
    if archive_path is None:
        return f"ERROR: Invalid archive path '{archive_name}'"

    try:
        shutil.make_archive(
            base_name=str(archive_path.with_suffix("")),
            format="zip",
            root_dir=folder_path.parent,
            base_dir=folder_path.name,
        )

        return f"Created archive: {archive_path}"

    except Exception as err:
        return f"ERROR: {str(err)}"


def unzipping(args: list[str]) -> str:
    """
    Команда unzip - распаковка ZIP архива

    Вход:
        args: list[str] - список аргументов ["archive.zip"]

    Выход:
        str - строка результата или ошибки
    """

    if len(args) != 1:
        return "ERROR: unzip requires archive name"

    archive_name = args[0]
    archive_path = resolve_path(archive_name, must_be=True, must_file=True)

    if archive_path is None:
        return f"ERROR: Archive '{archive_name}' does not exist"

    extract_dir = archive_path.parent / archive_path.stem

    try:
        shutil.unpack_archive(archive_path, extract_dir, "zip")
        return f"Extracted to: {extract_dir}"

    except Exception as err:
        return f"ERROR: {str(err)}"


def tarring(args: list[str]) -> str:
    """
    Команда tar - создание TAR.GZ архива

    Вход:
        args: list[str] - список аргументов ["folder", "archive.tar.gz"]

    Выход:
        str - строка результата или ошибки
    """

    if len(args) != 2:
        return "ERROR: tar requires folder and archive name"

    folder = args[0]
    archive_name = args[1]

    folder_path = resolve_path(folder, must_be=True, must_dir=True)
    if folder_path is None:
        return f"ERROR: Folder '{folder}' does not exist"

    if not archive_name.endswith(".tar.gz"):
        archive_name += ".tar.gz"

    archive_path = resolve_path(archive_name, must_be=False)
    if archive_path is None:
        return f"ERROR: Invalid archive path '{archive_name}'"

    try:
        shutil.make_archive(
            base_name=str(archive_path.with_suffix("").with_suffix("")),  # без .tar.gz
            format="gztar",
            root_dir=folder_path.parent,
            base_dir=folder_path.name,
        )

        return f"Created archive: {archive_path}"

    except Exception as err:
        return f"ERROR: {str(err)}"


def untarring(args: list[str]) -> str:
    """
    Команда untar - распаковка TAR.GZ архива

    Вход:
        args: list[str] - список аргументов ["archive.tar.gz"]

    Выход:
        str - строка результата или ошибки
    """
    if len(args) != 1:
        return "ERROR: untar requires archive name"

    archive_name = args[0]
    archive_path = resolve_path(archive_name, must_be=True, must_file=True)

    if archive_path is None:
        return f"ERROR: Archive '{archive_name}' does not exist"

    extract_dir = archive_path.parent / archive_path.name.replace(".tar.gz", "")

    try:
        shutil.unpack_archive(archive_path, extract_dir, "gztar")
        return f"Extracted to: {extract_dir}"

    except Exception as err:
        return f"ERROR: {str(err)}"
