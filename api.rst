LXC-Web-Panel API draft
-----------------------

All APIs requires authentication. You need to pass a ``private_token`` parameter by url or header. If passed as header, the header name must be "X-private-token".

API list
^^^^^^^^

GET /api/v1/containers
	Returns lxc containers on the current machine end brief status information.

GET /api/v1/container/<name>
	Returns full information on the ``name``d container.

POST 

DELETE /api/v1/container/<name>
	Delete the ``name``d container.