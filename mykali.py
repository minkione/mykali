#!/usr/bin/env python

import json
import argparse
from subprocess import Popen
from sys import exit
from os import chdir, path
from shutil import copy2

class Logger:

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    
    @staticmethod
    def info(message):
        print "[%s*%s] %s" % (Logger.BLUE, Logger.ENDC, message)

    @staticmethod
    def success(message):
        print "[%s+%s] %s" % (Logger.GREEN, Logger.ENDC, message)
    
    @staticmethod
    def failure(message):
        print "[%s-%s] %s" % (Logger.RED, Logger.ENDC, message)

'''
Load the config.json config file in as a dictionary.
'''
def load_config(directory):
	Logger.info("Loading config from %s" % directory)
        if not path.isdir(directory):
            Logger.failure("Directory does not exist, please check and try again.")
            exit(1)
	config_file = open(path.join(directory, 'config.json'), 'r')
	config = json.load(config_file)
	Logger.success("Config loaded successfully!")
        config_file.close()
        config["directory"] = directory
	return config

'''
Check that the Kali linux sources have been set in /etc/apt/sources.list (as when you install from CD, they are not).
'''
def check_kali_sources(config):
    Logger.info("Checking sources file...")
    sources_file_path = config["kali-sources"]["sources-file"]
    if not path.isfile(sources_file_path):
        Logger.failure("Failed.")
        Logger.failure("Configured sources file does not exist, please check the config and try again.")
    sources_file = open(sources_file_path, 'a+')
    kali_repo = config["kali-sources"]["repo"]
    repo_configured = False
    for line in sources_file:
        if kali_repo in line and "#" not in line:
            repo_configured = True
            Logger.success("Already configured.")
            break
    if not repo_configured:
        sources_file.write(kali_repo)
        Logger.success("Repo added.")
    sources_file.close()

'''
Update the Kali distribution using apt-get.
'''
def update_kali(config):
	Logger.info("Updating Kali")
        process = Popen("apt-get update && apt-get full-upgrade -y", shell = True)
        process.wait()
        if process.returncode == 0:
            Logger.success("Done!")
        else:
            Logger.failure("Failed.")
            exit(1)

'''
Install any packages that are required by this script (such as git).
'''
def install_requirements(config):
    Logger.info("Installing requirements...")
    package_list = ' '.join(map(str, config["requirements"])) 
    process = Popen("apt-get install -y %s" % package_list, shell = True)
    process.wait()
    if process.returncode == 0:
        Logger.success("Done!")
    else:
        Logger.failure("Failed to install: %s" % package)
        exit(2)
    Logger.info("Adding Git SSH keys to known hosts...")
    for site in config["git"]["ssh_keyscans"]:
        process = Popen("ssh-keyscan %s >> ~/.ssh/known_hosts" % site, shell = True)
        process.wait()
        if process.returncode != 0:
            Logger.failure("Failed to add ssh key to known hosts for %s..." % site)
            exit(3)
    Logger.success("Done!")

'''
If the machine is a VMWare VM then install VMWare Tools.
'''
def handle_vm(config):
    if "vm" in config and config["vm"]["is_vmware"]:
        Logger.info("Installing VMWare tools...")
        process = Popen("apt-get install -y open-vm-tools open-vm-tools-desktop", shell = True)
        process.wait()
        if process.returncode == 0:
            raw_input("Please 'insert' the VMWare tools CD and Press [Enter] to continue...")
            process = Popen("mount /dev/cdrom /mnt && mkdir /tmp/vmware && cp /mnt/* /tmp/vmware && cd /tmp/vmware && gunzip VMwareTools-* && tar -xvf VMwareTools-* && ./vmware-tools-distrib/vmware-install.pl", shell = True)
            process.wait()
            if process.returncode == 0:
                Logger.succes("Done!")
        else:
            Logger.failure("Failed.")
            exit(12)


'''
Install any user defined packages.
'''
def install_packages(config):
    if len(config["packages"]) > 0:
        Logger.info("Installing packages...")
        package_list = ' '.join(map(str, config["packages"])) 
        process = Popen("apt-get install -y %s" % package_list, shell = True)
        process.wait()
        if process.returncode == 0:
            Logger.success("Done!")
        else:
            Logger.failure("Failed.")
            exit(4)


'''
Install any user defined pip packages.
'''
def install_pip_packages(config):
    if len(config["pip_installs"]) > 0:
        Logger.info("Installing pip packages...")
        package_list = ' '.join(map(str, config["pip_installs"]))
        process = Popen("pip install %s" % package_list, shell = True)
        process.wait()
        if process.returncode == 0:
            Logger.success("Done!")
        else:
            Logger.failure("Failed.")
            exit(5)


'''
Run any user defined additional commands.
'''
def run_user_commands(config):
    if len(config["cmds"]) > 0:
        Logger.info("Running user defined commands...")
        for cmd in config["cmds"]:
            process = Popen(cmd, shell = True)
            process.wait()
            if process.returncode == 0:
                Logger.success("Executed: %s%s%s" % (Logger.BLUE, cmd, Logger.ENDC))
            else:
                Logger.failure("Command Failed: '%s'" % cmd)
                exit(6)

'''
Install any user defined git repositories.
'''
def install_git_repos(config):
    if "repos" in config["git"] and len(config["git"]["repos"]) > 0:
        errored = False
        Logger.info("Cloning and configuring git repositories...")
        install_dir = config["git"]["install_dir"]
        if not path.isdir(install_dir):
            Logger.failure("Git install directory does not exist: %s" % install_dir)
            Logger.failure("Please check the configuration and try again.")
            exit(7)
        for repo in config["git"]["repos"]:
            chdir(install_dir)
            url = repo["url"]
            directory = repo["directory"]
            Logger.info("Cloning: %s into %s%s%s" % (url, Logger.BLUE, directory, Logger.ENDC))

            if path.isdir(directory):
                Logger.info("The directory exists, is it already installed?")
                configure_git_repo(repo)
                continue
            
            process = Popen("git clone %s %s" % (url, directory), shell = True)
            process.wait()

            if process.returncode == 0:
                Logger.success("Complete.") 
                configure_git_repo(repo)
            else:
                Logger.failure("Failed.")
                errored = True

        # Once all is done, log a message depending on if any errored
        if errored:
            Logger.success("Git cloning complete, but with some errors.")
        else:
            Logger.success("Git cloning complete")

'''
Updates any installed git repositories.
'''
def update_git_repos(config):
    if "repos" in config["git"] and len(config["git"]["repos"]) > 0:
        errored = False
        Logger.info("Updating git repositories...")
        install_dir = config["git"]["install_dir"]
        if not path.isdir(install_dir):
            Logger.failure("Git install directory does not exist: %s" % install_dir)
            Logger.failure("Please check the configuration and try again.")
            exit(7)
        for repo in config["git"]["repos"]:
            directory = repo["directory"]
            chdir(path.join(install_dir, directory))
            Logger.info("Updating: %s%s%s" % (Logger.BLUE, directory, Logger.ENDC))

            process = Popen("git pull", shell = True)
            process.wait()
            chdir(install_dir)
            if process.returncode == 0:
                Logger.success("Complete.") 
                configure_git_repo(repo)
            else:
                Logger.failure("Failed.")
                errored = True

        # Once all is done, log a message depending on if any errored
        if errored:
            Logger.success("Git updating complete, but with some errors.")
        else:
            Logger.success("Git updating complete")

'''
Configure/install the git repos if require - e.g. run pip install or setup scripts. The exact commands are defined in the config file. 
'''
def configure_git_repo(repo):
    if "install_cmds" in repo and len(repo["install_cmds"]) > 0:
        Logger.info("Running repo setup scripts...")
        chdir(repo["directory"])
        for cmd in repo["install_cmds"]:
            process = Popen(cmd, shell = True)
            process.wait()

            if process.returncode == 0:
                Logger.success("Complete.") 
            else:
                Logger.failure("Failed.")
                break

'''
Copies any user config files from the configuration directory to the specified location
'''
def install_config_files(config):
    if len(config["config_files"]) > 0:
        Logger.info("Copying configuration files...")
        config_file_dir = path.join(config["directory"], 'config_files')
        if path.isdir(config_file_dir):
            path.chdir(config_file_dir)
        else:
            Logger.failure("config_files directory does not exist")
            exit(10)
        for target in config["config_files"]:
            for file in config["config_files"][target]:
                if path.isfile(path.join(config_file_dir, file)):
                    try:
                        copy2(file, target)
                    except (IOError, os.error) as why:
                        Logger.failure("Failed to copy %s to %s: %s" % (file, target, str(why)))
                        exit(11)
                else:
                    Logger.failure("Target config file doesn't exist in the config_files directory: %s" % file)


'''
Create an arg parser for handling the program arguments.
'''
def create_arg_parser():
    parser = argparse.ArgumentParser(description = 'A Kali Linux configuration tool')
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument("-r", "--run", help = "run the setup with the current configuration", action="store_true")
    exclusive.add_argument("-u", "--update", help = "just update existing configuration. Updates Kali, pip installs and Git repositories/installations. The update command assumes the run command has been completed successfully at least once.", action="store_true")
    exclusive.add_argument("-c", "--config", help = "display the current configuration file", action="store_true")
    parser.add_argument("-d", "--directory", help = "specify the directory containing the config.json file and config_files directory.")
    return parser

'''
Main method.
'''
def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    directory = path.dirname(path.realpath(__file__)) 

    if args.directory is not None:
        directory = args.directory
        if not path.isdir(directory):
            Logger.failure("%s does not exist, please check and try again." % directory)
            exit(9)

    if args.config:
        print open(path.join(directory, 'config.json'), 'r').read()
        exit(0)

    if args.run:
        Logger.info("***** mykali Kali setup script by m0rv4i *****\n\n")
        config = load_config(directory)
        check_kali_sources(config)
        update_kali(config)
        install_requirements(config)
        handle_vm(config)
        install_packages(config)
        install_pip_packages(config)
        run_user_commands(config)
        install_git_repos(config)
        install_config_files(config)
        exit(0)
   
    if args.update:
        Logger.info("***** mykali Kali update script by m0rv4i *****\n\n")
        config = load_config(directory)
        update_kali(config)
        install_pip_packages(config)
        update_git_repos(config)
        exit(0)
        
    parser.print_help()

# Entry point
if __name__ == "__main__":
	main()
