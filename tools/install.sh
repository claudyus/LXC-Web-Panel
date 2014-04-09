#!/bin/bash
echo ' _     __   _______  __          __  _       _____                 _ '
echo '| |    \ \ / / ____| \ \        / / | |     |  __ \               | |'
echo '| |     \ V / |       \ \  /\  / /__| |__   | |__) |_ _ _ __   ___| |'
echo "| |      > <| |        \ \/  \/ / _ \ '_ \  |  ___/ _\` | '_ \ / _ \ |"
echo '| |____ / . \ |____     \  /\  /  __/ |_) | | |  | (_| | | | |  __/ |'
echo '|______/_/ \_\_____|     \/  \/ \___|_.__/  |_|   \__,_|_| |_|\___|_|'
echo -e '\n\nAutomatic installer\n'

if [[ "$UID" -ne "0" ]];then
	echo 'You must be root to install LXC Web Panel !'
	exit
fi

### BEGIN PROGRAM

INSTALL_DIR='/srv/lwp'

if [[ -d "$INSTALL_DIR" ]];then
	echo "You already have LXC Web Panel installed. You'll need to remove $INSTALL_DIR if you want to install"
	exit 1
fi

echo 'Installing requirement...'

apt-get update &> /dev/null

hash python &> /dev/null || {
	echo '+ Installing Python'
	apt-get install -y python > /dev/null
}

hash pip &> /dev/null || {
	echo '+ Installing Python pip'
	apt-get install -y python-pip > /dev/null
}

python -c 'import flask' &> /dev/null || {
	echo '| + Flask Python...'
	pip install flask==0.9 2> /dev/null
}

echo 'Cloning LXC Web Panel...'
hash git &> /dev/null || {
	echo '+ Installing Git'
	apt-get install -y git > /dev/null
}

git clone https://github.com/claudyus/LXC-Web-Panel.git "$INSTALL_DIR"

echo -e '\nInstallation complete!\n\n'


echo 'Adding /etc/init.d/lwp...'

cat > '/etc/init.d/lwp' <<EOF
#!/bin/bash
# Copyright (c) 2013 LXC Web Panel
# All rights reserved.
#
# Author: Elie Deloumeau
#
# /etc/init.d/lwp
#
### BEGIN INIT INFO
# Provides: lwp
# Required-Start: \$local_fs \$network
# Required-Stop: \$local_fs
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: LWP Start script
### END INIT INFO


WORK_DIR="$INSTALL_DIR"
SCRIPT="lwp.py"
DAEMON="/usr/bin/python \$WORK_DIR/\$SCRIPT"
PIDFILE="/var/run/lwp.pid"
USER="root"

function start () {
	echo -n 'Starting server...'
	/sbin/start-stop-daemon --start --pidfile \$PIDFILE \\
		--user \$USER --group \$USER \\
		-b --make-pidfile \\
		--chuid \$USER \\
		--chdir \$WORK_DIR \\
		--exec \$DAEMON
	echo 'done.'
	}

function stop () {
	echo -n 'Stopping server...'
	/sbin/start-stop-daemon --stop --pidfile \$PIDFILE --signal KILL --verbose
	echo 'done.'
}


case "\$1" in
	'start')
		start
		;;
	'stop')
		stop
		;;
	'restart')
		stop
		start
		;;
	*)
		echo 'Usage: /etc/init.d/lwp {start|stop|restart}'
		exit 0
		;;
esac

exit 0
EOF

chmod +x '/etc/init.d/lwp'
update-rc.d lwp defaults &> /dev/null
echo 'Done'
/etc/init.d/lwp start

echo 'Connect you on http://your-ip-address:5000/'
echo 'default username: admin'
echo 'default password: admin'