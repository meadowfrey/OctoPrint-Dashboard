from flask import current_app
from flask_restful import fields, marshal
from flask_socketio import disconnect, join_room, emit
from jwt import DecodeError, ExpiredSignature

from octoprint_dashboard.app import socketio
from octoprint_dashboard.model import User, Config
from octoprint_dashboard.services import LoginService


@socketio.on('join')
def on_join(data):
    if current_app.config["AUTH"] == Config.NONE:
        user = User("Gandalf", superadmin=True)
    else:
        token = data.get('jwt')
        if not token:
            disconnect()
            return

        try:
            payload = LoginService.parse_api_token_direct(token)
        except DecodeError:
            disconnect()
            return
        except ExpiredSignature:
            disconnect()
            return
        user = User.query.filter_by(username=payload["username"]).scalar()
    printers = user.get_accessible_printers()

    for printer in printers:
        join_room(str(printer.id))

    datatype = {
        'id': fields.Integer,
        'name': fields.String,
        'group': fields.List(
            fields.Nested({
                'name': fields.String
            })
        )
    }
    emit("printers", marshal(printers, datatype))
