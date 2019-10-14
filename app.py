from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from uploader import ImageUploader

app = Flask(__name__)
api = Api(app)

img = ImageUploader()


class Images(Resource):
    def post(self):
        ohhh = request.get_json()
        url = ohhh.get("image_url")
        result = img.upload(url)
        response = {
            "message": "Image uploaded",
            "url": result
        }
        return make_response(jsonify(response), 200)


api.add_resource(Images, "/upload")
app.run(debug=True)
