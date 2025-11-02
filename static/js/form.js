document.addEventListener("DOMContentLoaded", () => {
  const numberInput = document.getElementById("id_number");
  const csvWrapper = document.getElementById("csv-upload-wrapper");
  const csvInput = document.getElementById("id_csv_file");

  // Show CSV upload when number is 8 digits
  numberInput.addEventListener("input", () => {
    if (numberInput.value.length === 8) {
      csvWrapper.classList.remove("hidden");
    } else {
      csvWrapper.classList.add("hidden");
    }
  });

  // Display selected file name
  const fileNameDisplay = document.createElement("p");
  fileNameDisplay.className = "text-sm text-gray-700 mt-2";
  csvWrapper.appendChild(fileNameDisplay);

  csvInput.addEventListener("change", () => {
    if (csvInput.files.length > 0) {
      fileNameDisplay.textContent = `Selected file: ${csvInput.files[0].name}`;
    } else {
      fileNameDisplay.textContent = "";
    }
  });
});
