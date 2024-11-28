
// Handle form submission
document.getElementById('studentForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(this);

    fetch('/admin/add_student', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        alert('Student information has been added successfully!');
        this.reset(); // Reset form after successful submission
    })
    .catch(error => {
        console.error('Error adding student:', error);
    });
});

//document.getElementById('studentForm').addEventListener('submit', function(event) {
     
    //alert('Student information has been added successfully!');
    // Optional: reset form after alert
    //this.reset();
//});

// Handle file upload
document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');

    // Make sure fileInput and fileNameDisplay exist
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener("change", function () {
            // Display the selected file name, or leave it blank if no file is chosen
            fileNameDisplay.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : "";
        });
    } else {
        console.error("File input or file name display element not found!");
    }
});



