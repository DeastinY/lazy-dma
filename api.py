from dataclasses import dataclass, asdict
from flask import Flask, jsonify
from flask_restful import reqparse, Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
CORS(app)
db = SQLAlchemy(app)
api = Api(app)

@dataclass
class Scene(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(60), unique=True, nullable=False)
    description: str = db.Column(db.String(120), unique=False, nullable=True)


@dataclass
class Light(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(60), unique=True, nullable=False)
    description: str = db.Column(db.String(120), unique=False, nullable=True)


@dataclass
class Sound(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(60), unique=True, nullable=False)
    description: str = db.Column(db.String(120), unique=False, nullable=True)


db.create_all()
db.session.commit()

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('description', type=str)
parser.add_argument('tags', type=str)
parser.add_argument('light', type=int, help="Light must be scene id (integer)")
parser.add_argument('sounds', type=int, help="sounds must be sound id (integer)", action="append")


class SceneList(Resource):
    def get(self):
        return [asdict(s) for s in Scene.query.all()]

    def post(self):
        args = parser.parse_args()
        scene = Scene(name=args["name"], description=args["description"])
        db.session.add(scene)
        db.session.commit()
        return asdict(scene)


class SceneSingle(Resource):
    def get(self, scene_id):
        return Scene.query.filter_by(id=scene_id).first()

    def patch(self, scene_id):
        return 404

    def delete(self, scene_id):
        return 404


api.add_resource(SceneList, "/scenes")
api.add_resource(SceneSingle, "/scenes/<string:scene_id>")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
