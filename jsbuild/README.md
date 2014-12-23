About this directory
====================

In order to not pollute the root directory of this Python project with JS
build tool files, we use a directory "jsbuild" for this.

This just keeps the project a bit tidier and puts all frontend tools
in one place.

The npm node_modules and bower_components folders get created here.

npm, bower, and grunt are all executed from the fabfile.py

The fabfile.py is then invoked by the debian packaging process.
