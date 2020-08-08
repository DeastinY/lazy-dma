import sqlite3
from flask import g, Flask
from flask_restful import reqparse, Resource, Api

app = Flask(__name__)
api = Api(app)

DATABASE = 'lazy-dma.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, check_same_thread=False)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

with app.app_context():
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS SCENES (ID INTEGER PRIMARY KEY, NAME TEXT, TAGS TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS SOUNDS (ID INTEGER PRIMARY KEY, NAME TEXT, TAGS TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS LIGHTS (ID INTEGER PRIMARY KEY, NAME TEXT, TAGS TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS SCENES_SOUNDS (SCENE_ID INTEGER, SOUND_ID INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS SCENES_LIGHTS (SCENE_ID INTEGER UNIQUE, LIGHT_ID INTEGER)")
    conn.commit()

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('tags', type=str)
parser.add_argument('light', type=int, help="Light must be scene id (integer)")
parser.add_argument('sounds', type=int, help="sounds must be sound id (integer)", action="append")


class SceneList(Resource):
    def get(self):
        c = get_db().cursor()
        c.execute("SELECT * FROM SCENES;")
        return c.fetchall()

    def post(self):
        conn = get_db()
        c = conn.cursor()
        args = parser.parse_args()
        c.execute("INSERT INTO SCENES (NAME, TAGS) VALUES (?, ?)", [args["name"], args["tags"]])
        for sid in args["sounds"]:
            c.execute("INSERT INTO SCENES_SOUNDS (SCENE_ID, SOUND_ID) VALUES (?, ?)", [c.lastrowid, sid])
        c.execute("INSERT INTO SCENES_LIGHTS (SCENE_ID, LIGHT_ID) VALUES (?, ?)", [c.lastrowid, args["light"]])
        conn.commit()
        return c.lastrowid, 201


class Scene(Resource):
    def get(self, scene_id):
        c = get_db().cursor()
        c.execute("SELECT * FROM SCENES WHERE ID=?", [scene_id])
        return c.fetchone()

    def patch(self, scene_id):
        conn = get_db()
        c = conn.cursor()
        args = parser.parse_args()
        c.execute("UPDATE SCENES SET NAME=?, TAGS=? WHERE ID=?", [args["name"], args["tags"], scene_id])
        c.execute("DELETE FROM SCENES_SOUNDS WHERE SCENE_ID=?", [scene_id])
        for sid in args["sounds"]:
            c.execute("INSERT INTO SCENES_SOUNDS (SCENE_ID, SOUND_ID) VALUES (?, ?)", [c.lastrowid, sid])
        c.execute("DELETE FROM SCENES_LIGHTS WHERE SCENE_ID=?", [scene_id])
        c.execute("INSERT INTO SCENES_LIGHTS (SCENE_ID, LIGHT_ID) VALUES (?, ?)", [c.lastrowid, args["light"]])
        conn.commit()
        return 201

    def delete(self, scene_id):
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM SCENES_SOUNDS WHERE SCENE_ID=?", [scene_id])
        c.execute("DELETE FROM SCENES_LIGHTS WHERE SCENE_ID=?", [scene_id])
        c.execute("DELETE FROM SCENES WHERE ID=?", [scene_id])
        conn.commit()
        return "", 204


api.add_resource(SceneList, "/scenes")
api.add_resource(Scene, "/scenes/<string:scene_id>")


@app.teardown_appcontext
def close_connection(exception):
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
