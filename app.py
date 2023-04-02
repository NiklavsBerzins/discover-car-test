from flask import Flask, request, jsonify, render_template, Response
from dicttoxml import dicttoxml
from flask_restful import Resource, Api, reqparse
from logging.handlers import RotatingFileHandler

import os, re, logging

app = Flask(__name__)
api = Api(app)

def getEnvironmentVariables():
    return {key: value for key, value in os.environ.items()}
def getRequestHeaders(request):
    return {key: value for key, value in request.headers.items()}

@app.route('/')
def hello():
    return "Hello World!!!"

class Headers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('format', type=str, location='args', default='html')
        super(Headers, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        format = args['format'].lower()

        headers_data = getRequestHeaders(request)

        if format == 'json':
            return jsonify(headers_data)
        elif format == 'xml':
            xml_data = dicttoxml(headers_data)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:
            rendered_html = render_template('headers.html', data=headers_data)
            return Response(rendered_html, content_type='text/html; charset=utf-8')

class Environment(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('format', type=str, location='args', default='html')
        super(Environment, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        format = args['format'].lower()

        env_data = getEnvironmentVariables()

        bgcolor = os.environ.get('BGCOLOR', '#FFFFFF')
        fgcolor = os.environ.get('FGCOLOR', '#000000')

        if not re.fullmatch(r'#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?', bgcolor):
            bgcolor = '#FFFFFF'
        if not re.fullmatch(r'#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?', fgcolor):
            fgcolor = '#000000'

        if format == 'json':
            return jsonify(env_data)
        elif format == 'xml':
            xml_data = dicttoxml(env_data)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:
            rendered_html = render_template('environment.html', data=env_data, bgcolor=bgcolor, fgcolor=fgcolor)
            return Response(rendered_html, content_type='text/html; charset=utf-8')

class PostData(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('format', type=str, location='args', default='html')
        super(PostData, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        format = args['format'].lower()

        post_data = request.form.to_dict()

        if format == 'json':
            return jsonify(post_data)
        elif format == 'xml':
            xml_data = dicttoxml(post_data)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:
            rendered_html = render_template('post.html', data=post_data)
            return Response(rendered_html, content_type='text/html; charset=utf-8')

    def get(self):
        return "Method not allowed", 405

    def put(self):
        return "Method not allowed", 405

    def delete(self):
        return "Method not allowed", 405

api.add_resource(Environment, '/api/environment')
api.add_resource(Headers, '/api/headers')
api.add_resource(PostData, '/api/post')

if __name__ == '__main__':
    # Configure logging
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Add handler to log messages to console (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)

    app.run(debug=True, host='0.0.0.0', port=3000)

