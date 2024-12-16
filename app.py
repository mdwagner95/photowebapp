from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configure processed folder
PROCESSED_FOLDER = 'static/processed'
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Helper function: Remove red filter
def remove_red(im, red_amount=0):
    width, height = im.size
    pixels = list(im.getdata())
    new_pixels = [(red_amount, g, b) for r, g, b in pixels]
    new_image = PILImage.new("RGB", (width, height))
    new_image.putdata(new_pixels)
    return new_image

# Route: Image processing
@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    if request.method == "POST":
        # Handle file upload for new image
        if "change_image" in request.form and "image" in request.files:
            file = request.files["image"]
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                image_url = filepath

        # Handle "Remove Red" filter
        if "remove_red" in request.form and "current_image" in request.form:
            current_image_path = request.form["current_image"]
            if os.path.exists(current_image_path):
                im = PILImage.open(current_image_path).convert("RGB")

                red_amount = int(request.form.get("red_amount", 0))
                processed_image = remove_red(im, red_amount)
                # Save the processed image
                processed_path = current_image_path.replace("uploads", "processed")
                processed_image.save(processed_path)
                image_url = processed_path

        # Handle "Reset Image"
        if "reset" in request.form and "current_image" in request.form:
            current_image_path = request.form["current_image"]
            if os.path.exists(current_image_path):
                image_url = current_image_path.replace("processed", "uploads")

        # Dummy filter buttons for future filters
        if "dummy_filter" in request.form:
            pass

    return render_template("index.html", image_url=image_url)

if __name__ == "__main__":
    # Use the PORT environment variable, or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)