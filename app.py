from flask import Flask, jsonify, request, make_response
from uploader import ImageUploader

app = Flask(__name__)

img = ImageUploader()


@app.route("/")
def home():
    response = {
        "message": "Welcome to Image Uploader",
        "usage": "Docs at https://github.com/mohyour/ImageUploader"
    }
    return make_response(jsonify(response), 200)


@app.route("/upload", methods=["POST"])
def upload():
    data = request.form
    url = data.get("image_url")
    result = img.upload(url)
    response = {
        "message": "Image uploaded",
        "url": result
    }
    return make_response(jsonify(response), 200)


if __name__ == '__main__':
    app.run()
