import time
import soco
import pyaudio
from phue import Bridge

from dataclasses import dataclass, asdict
from flask import Flask, Response
from flask_restful import reqparse, Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
CORS(app)
db = SQLAlchemy(app)
api = Api(app)

bridge = Bridge("192.168.178.33")
bridge.connect()
LAMPS = ["Ceiling", "Desk Richard", "Desk Spot"]

device = soco.discovery.any_soco()
zone = device.group.coordinator

@dataclass
class Scene(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(20), unique=True, nullable=False)
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


class LightList(Resource):
    def get(self):
        return [asdict(l) for l in Light.query.all()]

    def post(self):
        args = parser.parse_args()
        light = Light(name=args["name"], description=args["description"])
        db.session.add(light)
        db.session.commit()
        return asdict(light)


class LightSingle(Resource):
    def get(self, light_id):
        return asdict(Light.query.filter_by(id=light_id).first())

    def patch(self, light_id):
        args = parser.parse_args()
        light = Light.query.filter_by(id=light_id).first()
        light.name = args["name"]
        light.description = args["description"]
        db.session.commit()
        return asdict(light)

    def delete(self, light_id):
        db.session.delete(Light.query.filter_by(id=light_id).first())
        db.session.commit()


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
        return asdict(Scene.query.filter_by(id=scene_id).first())

    def patch(self, scene_id):
        args = parser.parse_args()
        scene = Scene.query.filter_by(id=scene_id).first()
        scene.name = args["name"]
        scene.description = args["description"]
        db.session.commit()
        return asdict(scene)

    def delete(self, scene_id):
        db.session.delete(Scene.query.filter_by(id=scene_id).first())
        db.session.commit()


class ActivateScene(Resource):
    def post(self, scene_id):
        bridge.set_light(LAMPS, "on", False)
        time.sleep(1)
        bridge.set_light(LAMPS, "on", True)
        zone.play_uri("https://bigsoundbank.com/UPLOAD/mp3/1631.mp3")
        return 202


class SoundList(Resource):
    def get(self):
        return [asdict(s) for s in Sound.query.all()]

    def post(self):
        args = parser.parse_args()
        sound = Sound(name=args["name"], description=args["description"])
        db.session.add(sound)
        db.session.commit()
        return asdict(sound)


class SoundSingle(Resource):
    def get(self, sound_id):
        return asdict(Sound.query.filter_by(id=sound_id).first())

    def patch(self, sound_id):
        args = parser.parse_args()
        sound = Sound.query.filter_by(id=sound_id).first()
        sound.name = args["name"]
        sound.description = args["description"]
        db.session.commit()
        return asdict(sound)

    def delete(self, sound_id):
        db.session.delete(Sound.query.filter_by(id=sound_id).first())
        db.session.commit()


class LampList(Resource):
    def get(self):
        return [bridge.get_light(l) for l in LAMPS]


@app.route("/audio")
def audio():
    def generate():
        with open("sounds/test.mp3", "rb") as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)

    return Response(generate(), mimetype="audio/x-wav")


api.add_resource(LampList, "/lamps")

api.add_resource(SceneList, "/scenes")
api.add_resource(SceneSingle, "/scenes/<string:scene_id>")

api.add_resource(LightList, "/lights")
api.add_resource(LightSingle, "/lights/<string:light_id>")

api.add_resource(SoundList, "/sounds")
api.add_resource(SoundSingle, "/sounds/<string:sound_id>")

api.add_resource(ActivateScene, "/scenes/<string:scene_id>/activate")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
