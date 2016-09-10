from flask import Flask
from flask_restful import Resource, Api
from database import init_db, db_session
from models import User, BaseGood, Producable

init_db()

app = Flask(__name__)
api = Api(app)

import pdb;pdb.set_trace()

class Server(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(Server, '/')

if __name__ == '__main__':
    app.run(debug=True)


@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

