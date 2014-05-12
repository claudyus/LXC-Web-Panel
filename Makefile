debian: Makefile lwp.py
	sudo rm -rf build/
	mkdir -p build/etc/
	mkdir -p build/etc/lwp
	mkdir -p build/srv/lwp
	# copy files
	cp -r lwp/ lxclite/ static/ templates/ lwp.py CHANGELOG build/srv/lwp/
	cp lwp.example.conf build/etc/lwp/
	cp -r debian/files/* build/
	find build/ -name *.pyc -exec rm {} \;
	sudo chown -R root: build/srv
	sudo chown -R root: build/etc
	# copy and modify debian package info
	cp debian/control debian/debian-binary build/
	sed -i "s/SIZE/`du build/ | tail -1 | cut -f 1`/g" build/control
	sed -i "s/VERSION/`git describe --tags`/g" build/control
	sed -i "s/DATE/`date`/g" build/control
	# build the deb file
	tar cvzf build/data.tar.gz -C build srv etc
	tar cvzf build/control.tar.gz -C build control
	cd build && ar rc lwp.deb debian-binary control.tar.gz data.tar.gz && cd ..
	mv build/lwp.deb gh-pages/lwp_`git describe --tags`.deb

site: debian
	make -C gh-pages/
