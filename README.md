# mykali

**This is a WIP, it's not even at version 1.0 yet!**

## Linux setup tool for Kali Linux.

Are you tired of configuring and reconfiguring your Kali box across computers? Or getting things back "just the way you like it" after a VM dies or your hard-drive is wiped? Then maybe this is the tool for you!

*mykali*  is a Kali linux configuration tool for quickly getting the box up to scratch just the way you like it. 

All you have to do is keep the **config.json** up to date with your desired configuration and you can run it quickly and easily on other boxes to get them up to scratch.

So far it has the capability to:

- Set up the **/etc/apt/sources.list** to check a source is configured.
- Fully update and upgrade Kali.
- Install VMWare tools if in a VMWare VM.
- Install a user configured list of `apt` packages.
- Install a user configured list of python `pip` packages.
- Run custom user shell commands.
- Clone a user configured set of Git repositories to a folder (such as */opt*).
- Run install commands on those repositories (such as `pip install`, `./install.sh` etc.).
- Copy saved configuration files to a specified location (such as **.bashrc** files etc.).

The tool can also be used to update Kali along with all the pip/Git tools.

There's also a roadmap of upcoming features at the bottom of the readme. Feel free to create issues for bugs/suggestions or and pull requests are welcome.

## Example

An example **config.json** is provided, in addition to a barebones copy at **bare-config.json**. This file installs and configures an install of Kali, and expects a *config_files* directory in the same directory as the **config.json** containing the configuration files to be copied, in this case .zshrc, .vimrc etc.

## Configuration

The idea here is you have a google drive/dropbox/git/whatever repository with your dotfiles etc. and a **config.json**. On a fresh build you can then grab that repository, clnoe this tool and then run it, pointing at that directory and it will configure the Kali box accordingly. 

The **config.json** is broken down into multiple sections **which are applied in the following order**:

* **kali-sources** - The location of the `apt` sources file and the repository URL to add.
* **requirements** - `apt` packages to install that are required my the script.
* **vm** - Virtual Machine configuration, such as VMWare Tools.
* **packages** - User defined apt packages to install.
* **pip installs** - User defined python pip packages to install.
* **cmds** - User defined additional commands to run.
* **git** - Git repositories to install. Includes configuration for the parent install directory (defaults to */opt*), any hosts to `ssh-keyscan`, the repository install directory, repository URL and any install commands for that repository (such as `pip install`, `gem install` etc.).
* **config_files** - Any files to copy from the *config_files* and where to. The configuration is in the form of the target directory and then a list of files to place in that directory.

## Running

To get help run the script without args or with the `-h` or `--help` option:
```
# ./mykali.py
usage: mykali.py [-h] [-r | -u | -c] [-d DIRECTORY]

A Kali Linux configuration tool

optional arguments:
  -h, --help            show this help message and exit
  -r, --run             run the setup with the current configuration
  -u, --update          just update existing configuration. Updates Kali, pip
                        installs and Git repositories/installations. The
                        update command assumes the run command has been
                        completed successfully at least once.
  -c, --config          display the current configuration file
  -d DIRECTORY, --directory DIRECTORY
                        specify the directory containing the config.json file
                        and config_files directory.

```

To view the current config, run the script with `-c` or `--config`:

```
# ./mykali.py --config
{
	"kali-sources" : {
		"sources-file" : "/etc/apt/sources.list",
		"repo" : "deb http://http.kali.org/kali kali-rolling main contrib non-free"
	},
	"requirements" : [
		"git"
	],
	"vm" : {
		"is_vmware" : true
	},
	"packages" : [
		"arp-scan",
		"gdb",
	  	"gobuster",
		"hashcat",
	  	"zsh"
	],
	"pip_installs" : [
		"powerline-status"
	],
	"cmds" : [
		"ln -s /usr/share/wordlists /wordlists",
		"byobu-enable",
		"passwd"
	],
	"git" : {
		"install_dir": "/opt",
		"ssh_keyscans" : [
			"github.com"

		],
		"repos" : [
			{
				"directory" : "aquatone",
				"url" : "https://github.com/michenriksen/aquatone.git",
				"install_cmds" : [
					"gem install aquatone"
				]
			},
			{
				"directory" : "discover",
				"url" : "https://github.com/leebaird/discover.git",
				"install_cmds" : [
					"./update.sh"
				]
			},
			{
				"directory" : "linenum",
				"url" : "https://github.com/rebootuser/LinEnum.git"
			}
		]
	},
		"config_files" : [
			{
				"~" : [
					".zshrc"
				]
			}
	]
}

```

To run the script with the current configuration in the script's directory use the `-r` or `--run` option:
```
./mykali.py --run
```

To run the script and specify the directory holding the *config.json* and *config_files* directory, use the `-d` or `--directory` option:

```
./mykali.py --run --directory ~/Downloads/config
```

To just have the script update Kali plus the installed pip tools and Git repositories, use the `-u` or `--update` option:

```
./mykali.py --update --directory ~/Downloads/config
```

## Roadmap

- [x] Have the script check the */etc/apt/sources.list* is up to date (in case install from CD)
- [x] Have the script update Kali 
- [x] Have the script clone a configurable list of git repos 
- [x] Have the script install tools from the distro repos
- [x] Have the script run any necessary extra install commands for the git repos, such as pip/setup/extra linking
- [x] Have the script take a directory parameter for backed up config directories
- [x] It's a bit daft we need an install script to install stuff so remove that
- [x] Have the script be able to run custom commands from the configuration file
- [x] Have the script be able to manage installing config files (.zshrc, .bashrc etc)
- [x] Install pip packages
- [x] `ssh-keyscan` repository sites (Github etc.)
- [x] If a VM install VMware tools (currently only VMWare)
- [x] Another tool for mass updating git repositories 
- [ ] Have the script handle environment variables for paths etc.
- [ ] Create a secondary tool for looping through an existing /opt directory (or wherever) and adding the repos to the config.json
- [ ] Set the resolution (Currently possible via a command.)
- [ ] Install a background/wallpaper (very important!) (Currently possible via a command.)
- [ ] Look into a host script for VMs which will configure the VM appropriately (bridged/NAT'd etc)
- [ ] Set shell (Currently possible via a command.)
- [ ] Change root password (from prompt, not **config.json**! Currently possible via a command.)
