## Image Uploader

Takes the url to an image file url as input, caches image, uploads to the server and sends back a new Url to reach the uploaded file.

#### Starting app
- Create virtual env
- Install requirements
- Create .env with configs
```
export GOOGLE_APPLICATION_CREDENTIALS=<path to google service key file>
export REDIS_PASSWORD=<redis url>
```
- Run `python app.py`

#### Enpoints

| Methods | Endpoints | Description      |
| ------- | --------- | ---------------- |
| GET     | /         | Welcome message  |
| POST    | /upload   | Upload image url |

#### To post data:
- key: image_url:
- value: <link to image url>
