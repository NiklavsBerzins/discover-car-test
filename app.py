from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from dicttoxml import dicttoxml
from flask_restful import Resource, Api, reqparse

import os, re, datetime

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db/discover-cars'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    user_agent = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()

def getEnvironmentVariables():
    return {key: value for key, value in os.environ.items()}
def getRequestHeaders(request):
    return {key: value for key, value in request.headers.items()}

@app.before_request
def log_request_info():
    timestamp = datetime.datetime.now()
    ip_address = request.remote_addr
    method = request.method
    path = request.path
    user_agent = request.user_agent.string

    access_log = AccessLog(
        timestamp=timestamp,
        ip_address=ip_address,
        method=method,
        path=path,
        user_agent=user_agent
    )
    db.session.add(access_log)
    db.session.commit()

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
    app.run(debug=True, host='0.0.0.0', port=3000)
