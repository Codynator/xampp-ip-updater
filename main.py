from subprocess import run
from re import match
from platform import system


class CommandNotFoundError(Exception):
    pass


class LocalIpNotFoundError(Exception):
    pass


class OSNotSupportedError(Exception):
    pass


def create_backup(data_to_save: list, backup_loc: str = "./httpd_copy.conf") -> None:
    with open(backup_loc, "w") as f:
        f.writelines(data_to_save)


def execute_command(comm: str) -> str:
    try:
        res: str = str(run(comm.split(), capture_output=True, text=True))
    except FileNotFoundError:
        raise CommandNotFoundError(f"Command not found.\nMake sure the command is available and written correctly.") \
            from None
    return res


def update_ip(updated_content: list, loc: str, ip: str, reset_ip: bool = False):
    server_name_regex: str = r"^ServerName .*"
    server_name_found: bool = False
    listen_regex: str = r"^Listen .*"
    listen_found: bool = False

    for index, row in enumerate(updated_content):
        if match(server_name_regex, row) and not server_name_found:
            updated_content[index] = f"ServerName {ip}:80\n" if not reset_ip else "ServerName Localhost:80"

        if match(listen_regex, row) and not listen_found:
            updated_content[index] = f"Listen {ip}:80\n" if not reset_ip else "Listen Localhost:80"

    with open(loc, "w") as f:
        f.writelines(updated_content)


def adapt_to_the_os() -> dict:
    os: str = system()
    if os == "Linux":
        return {
            "command": "ifconfig",
            "ipPattern": r"^inet 192\.168\..*",
            "confFileLoc": "./httpd.txt",
            "successful": True
        }
    elif os == "Windows":
        return {
            "command": "ipconfig",
            "ipPattern": r"^IPv4 Address .* 192\.168\..*",
            "confFileLoc": "\\xampp\\apache\\conf\\httpd.conf",
            "successful": True
        }
    else:
        return {"successful": False}


if __name__ == '__main__':
    setupData: dict = adapt_to_the_os()

    if not setupData['successful']:
        raise OSNotSupportedError("Your operating system is not supported.")

    localIp: str = ""
    fileContent: list = []

    result = execute_command(setupData['command'])

    lines: list = result.split("\\n        ")

    for line in lines:
        # Look for line containing local ip
        matches = match(setupData['ipPattern'], line)

        if matches:
            # When found save local ip
            localIp = line.split(" ")[1]

    if not localIp:
        raise LocalIpNotFoundError("Local IP has not been found.\nAre you sure you're using the right command?")

    with open(setupData['confFileLoc'], "r") as file:
        fileContent = file.readlines()

    create_backup(fileContent)

    update_ip(fileContent, setupData['confFileLoc'], localIp)
