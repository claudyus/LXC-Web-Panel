#!/bin/bash
echo ' _     __   _______  __          __  _       _____                 _ '
echo '| |    \ \ / / ____| \ \        / / | |     |  __ \               | |'
echo '| |     \ V / |       \ \  /\  / /__| |__   | |__) |_ _ _ __   ___| |'
echo "| |      > <| |        \ \/  \/ / _ \ '_ \  |  ___/ _\` | '_ \ / _ \ |"
echo '| |____ / . \ |____     \  /\  /  __/ |_) | | |  | (_| | | | |  __/ |'
echo '|______/_/ \_\_____|     \/  \/ \___|_.__/  |_|   \__,_|_| |_|\___|_|'
echo -e '\n\nAutomatic updater\n'

if [[ "$UID" -ne "0" ]];then
	echo 'You must be root to update LXC Web Panel !'
	exit
fi

### BEGIN PROGRAM

INSTALL_DIR='/srv/lwp'

if [[ -d "$INSTALL_DIR" && $(< $INSTALL_DIR/version) == '0.2' ]]; then

	/etc/init.d/lwp stop

	tmp=$(mktemp -d)

	echo 'Backuping database...'
	[[ -f "$INSTALL_DIR/lwp.db" ]] && cp "$INSTALL_DIR/lwp.db" "$tmp" || echo "Can't backup the database!"

	echo 'Removing old version...'
	rm -rf $INSTALL_DIR/* $INSTALL_DIR/.* &> /dev/null

	echo 'Installing LXC Web Panel v0.2...'
	git clone https://github.com/claudyus/LXC-Web-Panel.git "$INSTALL_DIR"

	echo 'Restore database...'
	cp "$tmp/lwp.db" "$INSTALL_DIR/lwp.db"
	rm -R "$tmp"

	/etc/init.d/lwp start

	echo -e '\nUpdate complete!\n\n'

else
	echo 'Unable to find previous installation...'
	exit 1
fi