import requests
from flask import Flask, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__, template_folder='templates')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get the API key from the environment variable
STABLE_DIFFUSION_V3_API_KEY = os.getenv('STABLE_DIFFUSION_V3_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    if 'prompt' in request.form and 'style' in request.form:
        prompt = request.form['prompt']
        style = request.form['style']

        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "authorization": f"Bearer {STABLE_DIFFUSION_V3_API_KEY}",  # Use v3 API key
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "style": style,  # Include style if provided
                "output_format": "jpeg",
            },
        )

        if response.status_code == 200:
            filename = secure_filename(f"generated_{prompt}.jpeg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure the 'uploads' folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            print(filepath)  # Debug print statement
            with open(filepath, 'wb') as file:
                file.write(response.content)

            return render_template('result.html', image_path=url_for('uploaded_file', filename=filename))
        else:
            return f"Error generating image: {response.json()}"
    else:
        return "Please provide a prompt and style"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)