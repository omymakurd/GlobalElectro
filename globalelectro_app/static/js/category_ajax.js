document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const form = document.getElementById("category-form");
    const tableBody = document.getElementById("category-table-body");

    // ========== Add ==========
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const nameInput = form.querySelector("input[name='name']");
        const name = nameInput.value.trim();
        if (!name) return;

        const formData = new FormData();
        formData.append("name", name);

        fetch("/categories/", {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: formData,
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    const row = document.createElement("tr");
                    row.setAttribute("data-id", data.category_id);
                    row.innerHTML = `
                        <td>${data.category_id}</td>
                        <td class="category-name">${data.name}</td>
                        <td>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-warning edit-btn">Edit</button>
                                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
                            </div>
                        </td>
                    `;
                    tableBody.appendChild(row);
                    nameInput.value = "";

                    Swal.fire({
                        icon: "success",
                        title: "Added",
                        text: "Category added successfully!"
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message
                    });
                }
            });
    });

    // ========== Edit + Delete ==========
    tableBody.addEventListener("click", function (e) {
        const row = e.target.closest("tr");
        if (!row) return;
        const id = row.dataset.id;

        const editButton = e.target.closest(".edit-btn");
        const deleteButton = e.target.closest(".delete-btn");

        // ---- Edit ----
        if (editButton) {
            const currentName = row.querySelector(".category-name").textContent;
            Swal.fire({
                title: "Edit Category",
                input: "text",
                inputValue: currentName,
                showCancelButton: true,
                confirmButtonText: "Save",
            }).then((result) => {
                if (result.isConfirmed && result.value.trim()) {
                    const formData = new FormData();
                    formData.append("name", result.value.trim());

                    fetch(`/categories/${id}/edit/`, {
                        method: "POST",
                        headers: { "X-CSRFToken": csrftoken },
                        body: formData,
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success") {
                                row.querySelector(".category-name").textContent = data.name;
                                Swal.fire({
                                    icon: "success",
                                    title: "Updated",
                                    text: "Category updated successfully!"
                                });
                            } else {
                                Swal.fire({
                                    icon: "error",
                                    title: "Error",
                                    text: data.message
                                });
                            }
                        });
                }
            });
        }

        // ---- Delete ----
        if (deleteButton) {
            Swal.fire({
                title: "Are you sure?",
                text: "This action cannot be undone!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Yes, delete it!",
                cancelButtonText: "Cancel"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/categories/${id}/delete/`, {
                        method: "POST",
                        headers: { "X-CSRFToken": csrftoken },
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success") {
                                row.remove();
                                Swal.fire({
                                    icon: "success",
                                    title: "Deleted",
                                    text: "Category removed successfully!"
                                });
                            } else {
                                Swal.fire({
                                    icon: "error",
                                    title: "Error",
                                    text: data.message
                                });
                            }
                        });
                }
            });
        }
    });
});
