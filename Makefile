all: static-build

static-build:
	python rst2html.py ../README.rst > site-src/pages/README.html
	python rst2html.py ../api.rst > site-src/pages/API.html
	#python rst2html.py ../CHANGELOG.rst > site-src/pages/changelog.html
	#build after any site-src modification
	cd site-src; cactus build; cd ..
	cp -r site-src/.build/* .

serve: just_web
	cd site-src/; cactus serve

just_web:
	cd site-src; cactus build; cd ..
	cp -r site-src/.build/* .
