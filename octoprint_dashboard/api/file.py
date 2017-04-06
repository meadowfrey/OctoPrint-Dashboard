from werkzeug.datastructures import FileStorage
from flask_restful import Resource, reqparse, marshal_with, fields
from flask import request, g
import requests

from octoprint_dashboard.login import login_required
from octoprint_dashboard.model import Printer
from octoprint_dashboard.services import OctoprintService

parser = reqparse.RequestParser()
parser.add_argument('printerId', type=int, required=True, help='Id can\'t be converted', action='append')
parser.add_argument('file', type=FileStorage, required=True, help='No file given', location='files')
parser.add_argument('print', type=bool, help='Print can\'t be converted')

deleteArgs = reqparse.RequestParser()
deleteArgs.add_argument('origin', type=str, required=True, help='Origin can\'t be converted')
deleteArgs.add_argument('name', type=str, required=True, help='Name can\'t be converted')
deleteArgs.add_argument('send', type=bool, help='Send can\'t be converted', location="json")

sendArgs = reqparse.RequestParser()
sendArgs.add_argument('printerId', type=list, required=True, help='PrinterID can\'t be converted', location="json")


class FileApi(Resource):
    @login_required
    def post(self):
        if not request.files["file"]:
            return "", 400
        args = parser.parse_args()
        filename = args["file"].filename
        contents = args["file"].read()
        printers = g.user.get_accessible_printers_id(args["printerId"])
        for printer in printers:
            try:
                response = OctoprintService.send_file(printer, filename, contents, args['print'])
                print(response)
            except RuntimeError:
                return None, 400
        return None, 200


class FileIdApi(Resource):
    @login_required
    @marshal_with({
        "name": fields.String,
        "type": fields.String,
        "origin": fields.String
    })
    def get(self, printer_id):
        printer = Printer.query.get(printer_id)
        try:
            files = OctoprintService.get_files(printer)
        except requests.ConnectionError:
            return [], 200
        return files["files"]

    @login_required
    def delete(self, printer_id):
        args = deleteArgs.parse_args()
        printer = Printer.query.get(printer_id)
        if OctoprintService.delete_file(printer, args["origin"], args["name"]):
            return None, 204

        return None, 409

    @login_required
    def post(self, printer_id):
        args = deleteArgs.parse_args()
        printer = Printer.query.get(printer_id)
        if args["send"]:
            body = sendArgs.parse_args()
            printers = g.user.get_accessible_printers_id(body["printerId"])
            content = OctoprintService.get_file_contents(printer, args["origin"], args["name"])
            for dest_printer in printers:
                OctoprintService.send_file(dest_printer, args["name"], content, False)
            return None, 200
        else:
            if OctoprintService.print(printer, args["origin"], args["name"]):
                return None, 200

            return None, 409
