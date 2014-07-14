debian: Makefile lwp.py
	sudo rm -rf build/
	mkdir -p build/etc/
	mkdir -p build/etc/lwp
	mkdir -p build/srv/lwp
	# copy files
	git describe --tags > build/srv/lwp/version
	cp -r lwp/ lxclite/ static/ templates/ lwp.py lwp.db CHANGELOG build/srv/lwp/
	cp lwp.example.conf build/etc/lwp/
	cp -r debian/files/* build/
	find build/ -name *.pyc -exec rm {} \;
	sudo chown -R root: build/srv
	sudo chown -R root: build/etc
	# copy and modify debian package info
	cp debian/control debian/debian-binary debian/postinst build/
	sed -i "s/SIZE/`du build/ | tail -1 | cut -f 1`/g" build/control
	sed -i "s/VERSION/`git describe --tags`/g" build/control
	sed -i "s/DATE/`date`/g" build/control
	# build the deb file
	tar cvzf build/data.tar.gz -C build srv etc
	tar cvzf build/control.tar.gz -C build control postinst
	cd build && ar rc lwp.deb debian-binary control.tar.gz data.tar.gz && cd ..
	mv build/lwp.deb gh-pages/lwp_`git describe --tags`.deb

clone:
	test -d gh-pages || git clone git@github.com:claudyus/LXC-Web-Panel.git gh-pages
	cd gh-pages; git checkout origin/gh-pages -b gh-pages || exit 0

site: bower clone debian
	make -C gh-pages/

bower:
	bower --version || sudo npm install -g bower
	bower install