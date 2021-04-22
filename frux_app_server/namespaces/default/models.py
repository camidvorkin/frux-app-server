"""Default namespace models module."""

from flask_restx import Model, fields, reqparse

hello_model = Model(
    "Hello model",
    {"Say": fields.String(required=True, description="The message said.")},
)

echo_model = Model(
    "Echo model",
    {"Echo": fields.String(required=True, description="The echo message.")},
)

echo_parser = reqparse.RequestParser()
echo_parser.add_argument(
    "message", type=str, location="json", help="Message to be echoed."
)
