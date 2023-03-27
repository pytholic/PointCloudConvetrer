import os

import open3d as o3d
from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath("./uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.mkdir(app.config["UPLOAD_FOLDER"])

ALLOWED_EXTENSIONS = {"ply"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Conversion function
def convert(filepath):
    # Load the input point cloud
    pcd = o3d.io.read_point_cloud(filepath)

    # Convert to numpy array and extract xyz
    xyz = pcd.points

    # Create new point cloud with only xyz
    new_pcd = o3d.geometry.PointCloud()
    new_pcd.points = o3d.utility.Vector3dVector(xyz)

    # Save the new point cloud as .xyz file
    new_file = os.path.splitext(filepath)[0] + ".xyz"
    o3d.io.write_point_cloud(new_file, new_pcd, write_ascii=True)

    return new_file


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    # Check if a file was included in the request
    if "file" not in request.files:
        return jsonify({"status": "failed", "message": "No file uploaded"}), 400

    # Get the file from the request
    file = request.files["file"]
    filename = file.filename

    # Check if the file has a filename
    if filename == "":
        return jsonify({"status": "failed", "message": "No file selected"}), 400

    # Check if the file has an allowed extension
    if not allowed_file(filename):
        return jsonify({"status": "failed", "message": "Invalid file extension"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    # Save the file to the server's UPLOAD_FOLDER
    file.save(file_path)

    # Return a success response with a message indicating that the file was uploaded
    return jsonify({"status": "success", "message": "File uploaded successfully"}), 200


@app.route("/convert", methods=["POST"])
def convert_file():
    file = request.files["file"]
    # Get the uploaded file path
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Read the file as a point cloud
    output_file = convert(filepath)

    # Return the path to the converted file
    return (
        jsonify(
            {
                "status": "success",
                "message": "File converted successfully",
                "filepath": output_file,
            }
        ),
        200,
    )


@app.route("/download")
def download_file():
    filepath = request.args.get("filepath", type=str)

    if not os.path.exists(filepath):
        return jsonify({"status": "failed", "message": "File not found"}), 400

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
