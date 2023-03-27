// Catch all the html elements
const uploadForm = document.getElementById("upload-form");
const inputFile = document.getElementById("input-file");
const uploadBtn = document.getElementById("upload-btn");
const convertBtn = document.getElementById("convert-btn");
const downloadBtn = document.getElementById("download-btn");
const statusMsg = document.getElementById("status-message");

const formData = new FormData();

let selectedFile = null;
let convertedFile = null;

// Set the initial status message
statusMsg.innerHTML = "Please upload a file.";

inputFile.addEventListener("change", (event) => {
  uploadBtn.disabled = false; // enable the upload button
  selectedFile = event.target.files[0];
  statusMsg.innerHTML = "File has been selected"; // update status message
});

// Listen for click events
uploadBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  // Append form data
  formData.append("file", selectedFile);
  // Send post request to the server
  const response = await fetch("/upload", {
    method: "POST",
    body: formData,
  });
  // Parse the response as JSON
  const json = await response.json();

  if (json.status === "success") {
    statusMsg.innerText = json.message;
    convertBtn.disabled = false;
    uploadBtn.disabled = true;
  } else {
    statusMsg.innerText = `Error: ${json.message}`;
  }
});

// Convert the uploaded file
convertBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  const response = await fetch("/convert", {
    method: "POST",
    body: formData,
  });
  const json = await response.json();
  if (json.status === "success") {
    statusMsg.innerText = json.message;
    convertBtn.disabled = true;
    downloadBtn.disabled = false;
    convertedFile = json.filepath;
  } else {
    statusMsg.innerText = `Error: ${json.message}`;
  }
});

downloadBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  if (convertedFile) {
    event.preventDefault();

    // Send request and get response from the server
    const response = await fetch(`/download?filepath=${convertedFile}`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(new Blob([blob]));

    // Create a new download link element
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "converted.xyz");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Reset the status message and form data
    statusMsg.innerText = "Please upload a file.";
    uploadBtn.disabled = true;
    convertBtn.disabled = true;
    downloadBtn.disabled = true;
    formData.delete("file");
    uploadForm.reset();

    // Reset the selected and converted file variables
    selectedFile = null;
    convertedFile = null;
  } else {
    statusMsg.innerText = "No file has been converted yet.";
  }
});
