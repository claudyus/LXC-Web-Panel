all:
	python rst2html.py ../README.rst > site-src/pages/README.html
	python rst2html.py ../CHANGELOG.rst > site-src/pages/CHANGELOG.html
	cd site-src; cactus build; cd ..
	md5sum *.deb > site-src/static/md5sum
	python md52json.py site-src/static/md5sum > site-src/static/md5sum.json
	cp -r site-src/.build/* .

serve: all
	cd site-src/; cactus serve
