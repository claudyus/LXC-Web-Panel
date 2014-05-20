all:
	python rst2html.py ../README.rst > site-src/pages/README.html
	cat ../CHANGELOG > site-src/pages/CHANGELOG.html
	md5sum *.deb > site-src/static/md5sum
	python md52json.py site-src/static/md5sum > site-src/static/md5sum.json
	#build after any site-src modification
	cd site-src; cactus build; cd ..
	cp -r site-src/.build/* .

serve: all
	cd site-src/; cactus serve
