# import ImageUtil

import urllib.request
import uuid
from PIL import Image
from io import BytesIO
from google.cloud import storage
from datetime import datetime
import redis
import os

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_client = redis.StrictRedis(host=redis_host, port=redis_port)

# r = redis.Redis(host=redis_host, port=redis_port, db=0)


class ImageUploader():

    def __init__(self):
        self.dimension = [0, 0]

    def cacheImageInMemory(self, imageFile, image_url):
        redis_client.set(imageFile, image_url)

    def uploadToServers(self, imageFile):
        client = storage.Client()
        bucket = client.get_bucket("minesimgbucket")
        filename = "image_{}_{}".format(str(uuid.uuid4())[:8],
                                        str(datetime.utcnow()))
        blob = bucket.blob(filename)
        with urllib.request.urlopen(imageFile) as response:
            # check if URL contains an image
            info = response.info()
            if(info.get_content_type().startswith("image")):
                blob.upload_from_string(response.read(),
                                        content_type=info.get_content_type())
                print("Uploaded image from: " + imageFile)
            else:
                print("Could not upload image. No image data type in URL")
        blob.make_public()
        url = blob.public_url

        self.cacheImageInMemory(imageFile, url)

        return url

    def upload(self, imageFile, maxWidth=10000, maxHeight=10000):
        upload_size = {}
        upload_size["maxWidth"] = maxWidth
        upload_size["maxHeight"] = maxHeight
        if not self.validate(imageFile, upload_size):
            return "not valid"
        url = redis_client.get(imageFile)
        if not url:
            url = self.uploadToServers(imageFile)
        return url.decode("utf-8")

    def dimensionIsValid(self, dimension, maxDimension):
        if dimension <= maxDimension and dimension > 1:
            return True
        return False

    def validate(self, imageFile, upload_size):
        # imageFile needs to be valid
        file = BytesIO(urllib.request.urlopen(imageFile).read())
        image = Image.open(file)
        width, height = image.size
        if imageFile:
            self.dimension[0] = width
            self.dimension[1] = height

            maxWidth = upload_size.get("maxWidth")  # maxWidth
            maxHeight = upload_size.get("maxHeight")  # maxHeight
            imageWidth = self.dimension[0]
            imageHeight = self.dimension[1]

            if imageWidth > 0:
                isValidWidth = self.dimensionIsValid(imageWidth, maxWidth)
            else:
                raise Exception("Invalid width")

            if imageHeight > 0:
                isValidHeight = self.dimensionIsValid(imageHeight, maxHeight)
            else:
                raise Exception("Invalid height")

            return isValidWidth and isValidHeight
        else:
            raise Exception("imageFile is null")


img = ImageUploader()
# print(img.upload("http://getwallpapers.com/wallpaper/full/b/8/d/32803.jpg"))
# print(img.upload("http://getwallpapers.com/wallpaper/full/b/8/d/32803.jpg"))

# print(img.upload("http://getwallpapers.com/wallpaper/full/b/8/d/32803.jpg"))
