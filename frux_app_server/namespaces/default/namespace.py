"""Default namespace module."""

from flask_restx import Namespace, Resource

from .models import echo_model, echo_parser, hello_model

ns = Namespace("Default", description="Default operations")

ns.models[echo_model.name] = echo_model
ns.models[hello_model.name] = hello_model


@ns.route('')
class HelloWorldResource(Resource):
    @ns.doc('say_hello')
    @ns.marshal_with(hello_model)
    def get(self):
        """Say hello."""
        return {"Say": "Hello"}

    @ns.doc('echo')
    @ns.marshal_with(echo_model)
    @ns.expect(echo_parser)
    def post(self):
        """Echo message."""
        data = ns.payload
        return {"Echo": data.get("message")}
