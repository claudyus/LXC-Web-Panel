
LXC-Web-Panel RestAPI
---------------------

Since version 0.6 LXC-Web-Panel support a set of RestAPI described in this documentation.

All APIs requires authentication. You need to pass a ``private_token`` parameter by url or header. If passed as header, the header name must be "private-token".

For example:
::

  curl http://host:5000/api/v1/containers?private_token=d41d8cd98f00b204e9800998ecf8427e
  or
  curl --header "private-token: d41d8cd98f00b204e9800998ecf8427e" http://host:5000/api/v1/containers


API list and description
^^^^^^^^^^^^^^^^^^^^^^^^

::

  GET /api/v1/containers/

Returns all lxc containers on the current machine and brief status information.

This api will return a json array like:

::

  [{"state": "running", "container": "base"}, {"state": "stopped", "container": "test"}]

------------

::

  GET /api/v1/containers/<name>

Returns full information about the ``name`` container.

This api will return a json object like:

::

  {
    "blkio_use": "7.66 MiB",
    "cpu_use": "0.67 seconds",
    "ip": "192.168.9.100",
    "kmem_use": "0 bytes",
    "link": "lxcbr0",
    "memory_use": "2.02 MiB",
    "name": "base",
    "pid": "4548",
    "rx_bytes": "81.08 KiB",
    "state": "RUNNING",
    "total_bytes": "81.08 KiB",
    "tx_bytes": "0 bytes"
  }

------------

::

  POST /api/v1/containers/<name>

Update a container status.

This api accept the following parameters in body request:

    - action: the new container status, possible status are start, stop and freeze

This api returns ``400`` if missed or mispelled json format, ``409`` if container *name* doesn't exist

------------

::

  PUT /api/v1/containers/

Create or clone a lxc container.

This api accept the following parameters in body request:

  - name: the name container (mandatory)
  - template: the lxc template (mandatory if clone is not present)
  - clone: the name of lxc container to clone (mandatory if template is not present)
  - store: the appropriate backing store system (optional)
  - xargs: optional xargs to be passed to lxc-create

------------

::

  DELETE /api/v1/containers/<name>

Delete the ``name`` container.

------------

::

  POST /api/v1/tokens

Add a new access token for the api
This api accept the following parameters in body request:

  - token: the new token to add (mandatory)
  - description: an optional token description

------------

::

  DELETE /api/v1/tokens/<private-token>

Revoke the given ``private-token``
