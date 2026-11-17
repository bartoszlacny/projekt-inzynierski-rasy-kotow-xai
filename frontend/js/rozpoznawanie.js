const file_input  = document.getElementById("file");
const preview = document.getElementById("preview");
const recognize_button = document.getElementById("recognize_button");
const filename_text  = document.getElementById("filename_text");
const result = document.getElementById("result");
const breeds_list = document.getElementById("breeds_list");
const error_text = document.getElementById("error");
const upload_box = document.querySelector(".upload_box");
const again_button = document.getElementById("again_button");
const intro = document.querySelector(".breed_recognition");
let last_result = null;

const xai_descriptions = {
    gradcam: "Mapa ciepła pokazuje, które fragmenty zdjęcia miały największy wpływ na decyzję modelu. Im cieplejszy kolor, tym większy wpływ.",
    lime: "Zaznaczone obszary to fragmenty zdjęcia, które najbardziej przemawiały za wskazaną rasą."
};

file_input.addEventListener("change", function () {
    const selected_image = file_input.files[0];
    if (!selected_image) return;

    preview.src = URL.createObjectURL(selected_image);
    preview.classList.remove("hidden");
    recognize_button.disabled = false;
    filename_text.textContent = selected_image.name;
});


function fake_backend(image) {
    return new Promise(function (resolve) {
        setTimeout(function () {
            resolve({
                top3: [
                    { breed_result: "Maine Coon", probability: 0.62 },
                    { breed_result: "Norwegian Forest Cat", probability: 0.21 },
                    { breed_result: "Ragdoll", probability: 0.09 }
                ],
                gradcam: preview.src,
                lime: preview.src
            });
        }, 1000);
    });
}


recognize_button.addEventListener("click", function () {
    recognize_button.disabled = true;
    recognize_button.textContent = "Rozpoznaję...";
    error_text.classList.add("hidden");

    fake_backend(file_input.files[0])
    
        .then(function (data) {
            show_result(data);
        })
        .catch(function (error) {
            error_text.textContent = "Nie udało się rozpoznać zdjęcia: " + error.message;
            error_text.classList.remove("hidden");
        })
        .finally(function () {
            recognize_button.disabled = false;
            recognize_button.textContent = "Rozpoznaj";
        });
});


function show_result(data) {
    last_result = data;
    breeds_list.innerHTML = "";

    for (const breed of data.top3) {
    const percent = Math.round(breed.probability * 100);

        breeds_list.innerHTML += `
            <div class="breed">
                <p>${breed.breed_result} – ${percent}%</p>
                <div class="bar_background">
                    <div class="bar" style="width: ${percent}%"></div>
                </div>
            </div>`;
    }

    document.getElementById("img_orginal").src = preview.src;
    show_xai("gradcam");

    result.classList.remove("hidden");
    upload_box.classList.add("hidden");
    intro.classList.add("hidden");
}

function show_xai(name) {
    document.getElementById("img_xai").src = last_result[name];
    document.getElementById("xai_title").textContent = (name === "gradcam") ? "Grad-CAM" : "LIME";
    document.getElementById("xai_text").textContent = xai_descriptions[name];
    document.getElementById("gradcam_button").classList.toggle("active", name === "gradcam");
    document.getElementById("lime_button").classList.toggle("active", name === "lime");
}

document.getElementById("gradcam_button").addEventListener("click", function () {
    show_xai("gradcam");
});

document.getElementById("lime_button").addEventListener("click", function () {
    show_xai("lime");
});


again_button.addEventListener("click", function () {
    file_input.value = "";
    preview.classList.add("hidden");
    filename_text.textContent = "Nie wybrano pliku";
    recognize_button.disabled = true;

    result.classList.add("hidden");
    upload_box.classList.remove("hidden");
    intro.classList.remove("hidden");
});