from flask import Flask, request, jsonify, render_template, Response
from dicttoxml import dicttoxml
from flask_restful import Resource, Api, reqparse

import os

app = Flask(__name__)
api = Api(app)

def getEnvironmentVariables():
    return {key: value for key, value in os.environ.items()}

@app.route('/')
def hello():
    return "Hello World!!!"

class Environment(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('format', type=str, location='args', default='html')
        super(Environment, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        format = args['format'].lower()

        env_data = getEnvironmentVariables()

        if format == 'json':
            return jsonify(env_data)
        elif format == 'xml':
            xml_data = dicttoxml(env_data)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:
            rendered_html = render_template('environment.html', data=env_data)
            return Response(rendered_html, content_type='text/html; charset=utf-8')

api.add_resource(Environment, '/api/environment')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
