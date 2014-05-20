all:
	python rst2html.py ../README.rst > site-src/pages/README.html
	cat ../CHANGELOG > site-src/pages/CHANGELOG.html
	md5sum *.deb > md5sum
	#build after any site-src modification
	cd site-src; cactus build; cd ..
	cp -r site-src/.build/* .

serve: all
	cd site-src/; cactus serve
