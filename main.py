# pip3 install flask opencv-python
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2 #for importing and using opencv
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cjpg": 
            newFilename = f"static/{filename.split('.')[0]}.jpg" #splits the original filename at the dot and takes the first part. example image.png ---> first part 'image'
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng": 
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #cv2cvtColor is OpenCV function used to convert an image from one space to another
            #cv2.COLOR_BGR2GRAY: This specifies the conversion from BGR (Blue-Green-Red) color space to grayscale.
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            #imgProcessed variable holds processed grayscale image data
            return newFilename
        case "ccrop":
            height, width = img.shape[:2] #retrieves dimension
            #img.shape returns a tuple (height, width, channels) where channels represents the number of color channels (e.g., 3 for RGB)
            cropped_image = img[(int)(height/2)-150:(int)(height/2)+150, (int)(width/2)-150:(int)(width/2)+150]
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, cropped_image)
            return newFilename
        case "cresize1":
            imgResized = cv2.resize(img, (350, 350))
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgResized)
            return newFilename
        case "cresize2":
            imgResized = cv2.resize(img, (1000, 1000))
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgResized)
            return newFilename
        case "crotate1":
            imgRotated1 = cv2.flip(img, 0) #0 specify horizontal direction
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgRotated1)
            return newFilename
        case "crotate2":
            imgRotated2 = cv2.flip(img, 1) #1 specify vertical direction
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgRotated2)
            return newFilename
        case "cgblur":
            gaussian = cv2.GaussianBlur(img, (7, 7), 0) #cv2.GaussionBlur - OpenCV function
            #(7, 7) specifies the kernel size (width and height of the Gaussian kernel) as (7, 7). A larger kernel size results in more blur.
            #0 specifies the standard deviation of the Gaussian kernel in the x-direction.
            #"kernel" refers to a matrix (or a small window) of numbers that is applied to an image for various operations such as blurring, sharpening, edge detection, and more.
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, gaussian)
            return newFilename
        case "cmblur":
            median = cv2.medianBlur(img, 5) #(5,5) pixels, kernel size
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, median)
            return newFilename
        case "cbfilter":
            bilateral = cv2.bilateralFilter(img, 9, 75, 75) #9 - diameter of each pixel neighbour, larger means more distant pixels will influence each other
            # 75 and 75: The filter sigma values for color and space
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, bilateral)
            return newFilename
        case "cborder":
            border = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, value = 0) #cv2.BORDER_CONSTANT: Specifies the type of border to add.
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, border)
            return newFilename
        case "csketch":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Invert grayscale image and blurred image
            inverted = 255 - gray
            blurred = cv2.GaussianBlur(inverted, (31, 31), 0)
            inverted_blurred = 255 - blurred
            # Combine the grayscale image with the inverted blurred image using the Dodge blend mode
            sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
            newFilename = f"static/{filename.split('.')[0]}_sketch.jpg"
            cv2.imwrite(newFilename, sketch)
            return newFilename
    pass

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST": 
        operation = request.form.get("operation")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")

    return render_template("index.html")


app.run(debug=True)