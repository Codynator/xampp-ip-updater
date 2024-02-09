from subprocess import run
from re import match
from platform import system
from sys import exit
from yaml import safe_load


class CommandNotFoundError(Exception):
    pass


class LocalIpNotFoundError(Exception):
    pass


class OSNotSupportedError(Exception):
    pass


def create_backup(data_to_save: list, backup_loc: str = "./httpd_copy.conf") -> None:
    with open(backup_loc, "w") as f:
        f.writelines(data_to_save)


def check_and_create_backup(data_to_save: list) -> None:
    if not settings['create_backup']:
        return

    if not settings['ask_for_backup']:
        create_backup(data_to_save)
        return

    if input("Do you want to create a backup? (y/n) ").lower().startswith('y'):
        create_backup(data_to_save)


def execute_command(comm: str) -> str:
    try:
        # Encoding key argument is required because of Windows 10.
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
            "confFileLoc": "/opt/lampp/etc/httpd.conf",
            "seperator": "\\n        ",
            "ipIndex": 1,
            "successful": True
        }
    elif os == "Windows":
        return {
            "command": "ipconfig",
            "ipPattern": r"^IPv4 Address.*192\.168\..*",
            "confFileLoc": "c://xampp/apache/conf/httpd.conf",
            "seperator": "\\n   ",
            "ipIndex": 13,
            "successful": True
        }
    else:
        return {"successful": False}


def read_yaml_conf_file() -> dict:
    try:
        with open('settings.yaml', 'r') as f:
            return safe_load(f)['settings']
    except FileNotFoundError:
        return {
            'create_backup': True,
            'ask_for_backup': False,
            'show_server_url': False
        }


def check_and_return_url(ip: str) -> str:
    if not settings['return_server_url']:
        return ""

    return f"Server's url: {ip}/"


if __name__ == '__main__':
    setupData: dict = adapt_to_the_os()
    settings: dict = read_yaml_conf_file()
    localIp: str = ""

    with open(setupData['confFileLoc'], "r") as file:
        fileContent: list = file.readlines()

    if not setupData['successful']:
        # Raise an error if user's OS is not supported.
        raise OSNotSupportedError("Your operating system is not supported.")

    if input("Do you want to set localhost as IP? (y/n) ").lower().startswith('y'):
        # Set the ip to Localhost and exit the program.
        localIp = "localhost"

        check_and_create_backup(fileContent)
        update_ip(fileContent, setupData['confFileLoc'], localIp)
        print(check_and_return_url(localIp))

        input('\n\nPress ENTER to exit the program.')
        exit()

    result = execute_command(setupData['command'])
    lines: list = result.split(setupData['seperator'])

    for line in lines:
        # Look for line containing local ip.
        if match(setupData['ipPattern'], line):
            # When found save local ip.
            localIp = line.split(" ")[setupData['ipIndex']]

    if not localIp:
        raise LocalIpNotFoundError("Local IP has not been found.\nAre you sure you're using the right command?")
    else:
        print(f"\nThe IP address found is: {localIp}\n")

    check_and_create_backup(fileContent)
    update_ip(fileContent, setupData['confFileLoc'], localIp)
    print(check_and_return_url(localIp))

    input('\n\nPress ENTER to exit the program.')
