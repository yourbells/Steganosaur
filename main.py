from flask import Flask, render_template
from static.video import video

UPLOAD_VIDEO_FOLDER = "static"

app = Flask(__name__)
app.secret_key = "hello"
app.config["UPLOAD_VIDEO_FOLDER"] = UPLOAD_VIDEO_FOLDER
app.register_blueprint(video, url_prefix="/video")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)