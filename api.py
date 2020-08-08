from flask import Flask, request
from flask_restful import reqparse, Resource, Api

app = Flask(__name__)
api = Api(app)

SCENES = {
    "scene1": {"light": 1, "sounds": [1, 2, 3]},
    "scene2": {"light": 2, "sounds": [4]}
}

parser = reqparse.RequestParser()
parser.add_argument('light')
parser.add_argument('sounds')


class SceneList(Resource):
    def get(self):
        return SCENES

    def post(self):
        scene_id = int(max(SCENES.keys()).lstrip("scene")) + 1
        scene_id = f"scene{scene_id}"
        args = parser.parse_args()
        SCENES[scene_id] = {"light": args["light"], "sounds": args["sounds"]}
        return SCENES[scene_id], 201


class Scene(Resource):
    def get(self, scene_id):
        return SCENES[scene_id]

    def patch(self, scene_id):
        args = parser.parse_args()
        SCENES[scene_id] = {"light": args["light"], "sounds": args["sounds"]}
        return {scene_id: SCENES[scene_id]}, 201

    def delete(self, scene_id):
        del SCENES[f"scene{scene_id}"]
        return "", 204


api.add_resource(SceneList, "/scenes")
api.add_resource(Scene, "/scenes/<string:scene_id>")

if __name__ == '__main__':
    app.run(debug=True)
