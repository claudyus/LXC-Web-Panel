# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import json

from flask import Blueprint, request, g, abort, jsonify

import lwp.lxclite as lxc
from lwp.utils import api_auth

# Flask module
mod = Blueprint('api', __name__)


@mod.route('/api/v1/container(s)?')
@api_auth()
def get_containers():
    """
    Returns lxc containers on the current machine and brief status information.
    """
    list_container = lxc.list_status()
    return json.dumps(list_container)


@mod.route('/api/v1/container(s)?/<name>')
@api_auth()
def get_container(name):
    return jsonify(lxc.info(name))


@mod.route('/api/v1/container(s)?/<name>', methods=['POST'])
@api_auth()
def post_container(name):
    data = request.get_json(force=True)
    if data is None:
        return jsonify(status="error", error="Bad request"), 400

    status = data['action']
    try:
        if status == "stop":
            lxc.stop(name)
            return jsonify(status="ok"), 200
        elif status == "start":
            lxc.start(name)
            return jsonify(status="ok"), 200
        elif status == "freeze":
            lxc.freeze(name)
            return jsonify(status="ok"), 200

        return jsonify(status="error", error="Bad request"), 400
    except lxc.ContainerDoesntExists:
        return jsonify(status="error", error="Container doesn' t exists"), 409


@mod.route('/api/v1/container(s)?/', methods=['PUT'])
@api_auth()
def add_container():
    data = request.get_json(force=True)
    if data is None:
        return jsonify(status="error", error="Bad request"), 400

    if (bool('template' not in data) != bool('clone' not in data)) | bool('name' not in data):
        return jsonify(status="error", error="Bad request"), 400

    print(data)
    if 'template' in data:
        # we want a new container
        if 'store' not in data:
            data.update(store=None)
        if 'xargs' not in data:
            data.update(xargs=None)

        try:
            lxc.create(data.name, data.template, data.store, data.xargs)
        except lxc.ContainerAlreadyExists:
            return jsonify(status="error", error="Container yet exists"), 409
    else:
        #we want to clone a container
        try:
            lxc.clone(data.clone, data.name)
        except lxc.ContainerAlreadyExists:
            return jsonify(status="error", error="Container yet exists"), 409
        finally:
            abort(500)
    return jsonify(status="ok"), 200


@mod.route('/api/v1/container(s)?/<name>', methods=['DELETE'])
@api_auth()
def delete_container(name):
    try:
        lxc.destroy(name)
        return jsonify(status="ok"), 200
    except lxc.ContainerDoesntExists:
        return jsonify(status="error", error="Container doesn' t exists"), 400


@mod.route('/api/v1/token(s)?/', methods=['POST'])
@api_auth()
def add_token():
    data = request.get_json(force=True)
    if data is None or 'token' not in data:
        return jsonify(status="error", error="Bad request"), 400

    if 'description' not in data:
        data.update(description="no description")
    g.db.execute('insert into api_tokens(description, token) values(?, ?)', [data['description'], data['token']])
    g.db.commit()
    return jsonify(status="ok"), 200


@mod.route('/api/v1/token(s)?/<token>', methods=['DELETE'])
@api_auth()
def delete_token(token):
    g.db.execute('delete from api_tokens where token=?', [token])
    g.db.commit()
    return jsonify(status="ok"), 200
