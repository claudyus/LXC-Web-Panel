
LXC-Web-Panel API draft
-----------------------

All APIs requires authentication. You need to pass a ``private_token`` parameter by url or header. If passed as header, the header name must be "private-token".

For example:
::

  curl http://host:5000/api/v1/containers?private_token=d41d8cd98f00b204e9800998ecf8427e
  or
  curl --header "private-token: d41d8cd98f00b204e9800998ecf8427e" http://host:5000/api/v1/containers


API list
^^^^^^^^

::

  GET /api/v1/containers

Returns lxc containers on the current machine and brief status information.

::

  GET /api/v1/container/<name>

Returns full information on the ``name`` container.

::

  POST /api/v1/container/<name>

Update a container status.
This api accept the following parameters in body request:
	- status: the new container statusm possible status are start, stop, freeze

::

	PUT /api/v1/container/

Create or clone a new lxc container.
This api accept the following parameters in body request:
  - name: the name container (mandatory)
  - template: the lxc template (mandatory if clone is not present)
  - clone: the name of lxc container to clone (mandatory if template is not present)
  - store: the appropriate backing store system (optional)


::

  DELETE /api/v1/container/<name>

Delete the ``name`` container.


::

  POST /api/v1/token

Add a new access token for the api
This api accept the following parameters in body request:
	- token: the new token to validate (mandatory)
	- description: an optional token description

::

  DELETE /api/v1/token/<private-token>

Revoke the given ``private-token``


Operation detail
^^^^^^^^^^^^^^^^
All operation over api are logged in ``syslog``
