# import ImageUtil

import urllib.request
import redis
import os
import uuid
from PIL import Image
from io import BytesIO
from google.cloud import storage
from datetime import datetime

# Connect to Redis
redis_client = redis.from_url(os.environ.get("REDISCLOUD_URL"))


class ImageUploader():
    """
    Image Uploader Class: Uploads image to server and returns new url to store
    the image
    """

    def __init__(self):
        self.dimension = [0, 0]

    def cache_image_in_memory(self, image_file, image_url):
        """
        Cache image in memory using redis

        Parameters:
            image_file: Image file to be uploaded
            image_url: Resulting url from server
        Returns:
            None
        """

        redis_client.set(image_file, image_url)

    def uploadToServers(self, image_file):
        """
        Upload image file to google storage server and caches it

        Parameters:
            image_file(string): Image file to be uploaded
        Returns:
            url(string): Resulting url from server
        """

        client = storage.Client()
        bucket = client.get_bucket("minesimgbucket")
        filename = "image_{}_{}".format(str(uuid.uuid4())[:8],
                                        str(datetime.utcnow()))
        blob = bucket.blob(filename)
        with urllib.request.urlopen(image_file) as response:
            # check if URL contains an image
            info = response.info()
            if(info.get_content_type().startswith("image")):
                blob.upload_from_string(response.read(),
                                        content_type=info.get_content_type())
                print("Uploaded image from: " + image_file)
            else:
                print("Could not upload image. No image data type in URL")
        blob.make_public()
        url = blob.public_url

        self.cache_image_in_memory(image_file, url)

        return url

    def upload(self, image_file, max_width=10000, max_height=10000):
        """
        Returns the uploaded image url

        Parameters:
            image_file: image file uploaded
            max_width(int): Max width of image to be uploaded
            max_height(int): Max height of image to be uploaded
        Returns:
            url(string): Resulting url from server
        """

        upload_size = {}
        upload_size["max_width"] = max_width
        upload_size["max_height"] = max_height
        if not self.validate(image_file, upload_size):
            return "not valid"
        url = redis_client.get(image_file)
        if not url:
            url = self.uploadToServers(image_file)
        return url.decode("utf-8")

    def dimension_is_valid(self, dimension, max_dimension):
        """
        Check if dimension is a valid one

        Parameters:
            dimension(int): Value dimension to check
            max_dimension(int): maximum value of dimension to check

        Returns:
            True(bool): If dimension is valid
            False(bool): If dimension is not valid
        """
        if dimension <= max_dimension and dimension > 1:
            return True
        return False

    def validate(self, image_file, upload_size):
        """
        Validate if image sizes

        Parameters:
            image_file(string): Image file url to validate
            uploade_size(int): Image upload size

        Returns:
            True(bool) if image size is valid
        """

        file = BytesIO(urllib.request.urlopen(image_file).read())
        image = Image.open(file)
        width, height = image.size
        if image_file:
            self.dimension[0] = width
            self.dimension[1] = height

            max_width = upload_size.get("max_width")
            max_height = upload_size.get("max_height")
            imageWidth = self.dimension[0]
            imageHeight = self.dimension[1]

            if imageWidth > 0:
                isValidWidth = self.dimension_is_valid(imageWidth, max_width)
            else:
                raise Exception("Invalid width")

            if imageHeight > 0:
                isValidHeight = self.dimension_is_valid(imageHeight,
                                                        max_height)
            else:
                raise Exception("Invalid height")

            return isValidWidth and isValidHeight
        else:
            raise Exception("image_file is null")
