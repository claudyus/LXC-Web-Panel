all: static-build scanpkg

static-build:
	python rst2html.py ../README.rst > site-src/pages/README.html
	python rst2html.py ../api.rst > site-src/pages/API.html
	cd ..; git log --pretty=format:'%ci;%h;%s' | grep -v Merge > gh-pages/changelog.csv
	md5sum *.deb > md5sum
	#build after any site-src modification
	cd site-src; cactus build; cd ..
	cp -r site-src/.build/* .

scanpkg:
	dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
	# deb http://claudyus.github.io/LXC-Web-Panel/ ./

serve: all
	cd site-src/; cactus serve
