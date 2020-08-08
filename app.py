from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

scenes = {}


class Scenes(Resource):
    def get(self, scene_id):
        return {scene_id: scenes[scene_id]}

    def put(self, scene_id):
        scenes[scene_id] = request.form["data"]
        return {scene_id: scenes[scene_id]}


api.add_resource(Scenes, "/<string:scene_id>")

if __name__ == '__main__':
    app.run(debug=True)
