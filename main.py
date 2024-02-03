from subprocess import run
from re import match
from platform import system
from sys import exit


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
        # encoding key argument is required because of Windows
        res: str = str(run(comm.split(), capture_output=True, text=True, encoding='cp437'))
    except FileNotFoundError:
        raise CommandNotFoundError(f"Command not found.\nMake sure the command is available and written correctly.") \
            from None
    return res


def update_ip(updated_content: list, loc: str, ip: str):
    server_name_regex: str = r"^ServerName .*"
    server_name_found: bool = False
    listen_regex: str = r"^Listen .*"
    listen_found: bool = False

    for index, row in enumerate(updated_content):
        if match(server_name_regex, row) and not server_name_found:
            updated_content[index] = f"ServerName {ip}:80\n"

        if match(listen_regex, row) and not listen_found:
            updated_content[index] = f"Listen {ip}:80\n"

    with open(loc, "w") as f:
        f.writelines(updated_content)


def adapt_to_the_os() -> dict:
    os: str = system()
    if os == "Linux":
        return {
            "command": "ifconfig",
            "ipPattern": r"^inet 192\.168\..*",
            "confFileLoc": "./httpd.conf",
            "seperator": "\\n        ",
            "ipIndex": 1,
            "successful": True
        }
    elif os == "Windows":
        return {
            "command": "ipconfig",
            "ipPattern": r"^IPv4 Address .* 192\.168\..*",
            "confFileLoc": "\\xampp\\apache\\conf\\httpd.conf",
            "seperator": "\\n   ",
            "ipIndex": 13,
            "successful": True
        }
    else:
        return {"successful": False}


if __name__ == '__main__':
    setupData: dict = adapt_to_the_os()
    localIp: str = ""

    with open(setupData['confFileLoc'], "r") as file:
        fileContent: list = file.readlines()

    if not setupData['successful']:
        # Raise an error if user's OS is not supported
        raise OSNotSupportedError("Your operating system is not supported.")

    if input("Do you want to set Localhost as ip? (y/n) ").lower().startswith('y'):
        # Set the ip to Localhost.
        localIp = "Localhost"
        update_ip(fileContent, setupData['confFileLoc'], localIp)
        exit()

    result = execute_command(setupData['command'])
    lines: list = result.split(setupData['seperator'])

    for line in lines:
        # Look for line containing local ip.
        if match(setupData['ipPattern'], line):
            # When found save local ip
            localIp = line.split(" ")[setupData['ipIndex']]

    if not localIp:
        raise LocalIpNotFoundError("Local IP has not been found.\nAre you sure you're using the right command?")

    create_backup(fileContent)

    update_ip(fileContent, setupData['confFileLoc'], localIp)
