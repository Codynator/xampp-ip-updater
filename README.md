# XAMPP IP Updater

Primitive terminal based program that automates the process of setting up local IP instead of Localhost in Apache's httpd.conf file.

## Usage

1. On `Windows`, it’s recommended to run the program from the terminal. First, open cmd then change the current directory to where the `main.py` file is located (alternatively, open the directory immediately in the terminal from the explorer level). Then use the `py main.py` command.  

2. On `Linux`, make sure that you’ve installed `net-tools`, which provides the `ifconfig` command. Open the directory where `main.py` is located and use the following command `sudo python3 main.py` (you can skip the `sudo` if you’ve changed the owner and permissions of the `httpd.conf` file).  

3. There's no support for MacOS.  

In either case the program always creates a backup of the previous version of the `httpd.conf` file (if you do not wish to create backup, you can comment the `create_backup()` line in `main.py`).

## Known issues

- Sometimes after running the program, there's no result. In that case try to run it again. On `Linux` try to use `sudo` if you haven't done it before.  

> I'm aware that the program is very basic and can be unintuitive to use but it has started as personal project for my own needs and wasn't meant to be published.
