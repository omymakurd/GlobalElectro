document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("category-form");
    const tableBody = document.getElementById("category-table-body");
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const nameInput = form.querySelector("input[name='name']");
        const name = nameInput.value.trim();
        if (!name) return;

        const formData = new FormData();
        formData.append("name", name);

        fetch("/categories/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${data.category_id}</td><td>${data.name}</td>`;
                tableBody.appendChild(tr);
                nameInput.value = "";
            } else {
                alert(data.message);
            }
        })
        .catch(err => console.error("Error:", err));
    });
});
