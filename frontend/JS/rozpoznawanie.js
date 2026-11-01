const file_input  = document.getElementById("file");
const preview = document.getElementById("preview");
const recognize_button = document.getElementById("recognize_button");
const filename_text  = document.getElementById("filename_text");


file_input.addEventListener("change", function () {
    const selected_image = file_input.files[0];
    if (!selected_image) return;

    preview.src = URL.createObjectURL(selected_image);
    preview.classList.remove("hidden");
    recognize_button.disabled = false;
    filename_text.textContent = selected_image.name;
});


