from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO
from PIL import Image
import time
import os

app = Flask(__name__)

# Ensure the uploads and results folders exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/results', exist_ok=True)

# Load the YOLO model
model = YOLO("best.pt")  # Replace with the correct path to your YOLO model

# Prediction function
def predict_pothole(image_path, img_name):
    try:
        # Open the image and resize it for the YOLO model (640x640 input size)
        with Image.open(image_path) as img:
            img = img.resize((640, 640))  # Resize to YOLO model input size

        # Define the path for saving the processed result
        img_result_path = os.path.join("static/results", img_name)

        # Perform prediction using the YOLO model
        results = model(image_path)

        # Convert the result to a PIL image and save it
        result_image = Image.fromarray(results[0].plot())
        result_image.save(img_result_path)

        return img_name  # Return the image name for display
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

@app.route('/')
def HOME():
    return render_template("index.html")

@app.route('/Prediction_Page')
def prediction_page():
    return render_template("prediction_page.html")

@app.route('/predict', methods=['POST'])
def predict():
    if 'r_image' not in request.files:
        return "No file part in the request.", 400

    img = request.files['r_image']

    if img.filename == '':
        return "No file selected for uploading.", 400

    # Save the uploaded image
    img_name = f"{int(time.time())}_{img.filename}"
    img_path = os.path.join("static/uploads", img_name)
    img.save(img_path)

    # Run the prediction
    prediction = predict_pothole(img_path, img_name)

    if prediction:
        result_image_path = url_for('static', filename=f'results/{prediction}')
        return render_template('prediction_result_page_.html', image=result_image_path)
    else:
        return "An error occurred during prediction. Please try again.", 500

if __name__ == "__main__":
    app.run(debug=True)