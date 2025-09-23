document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const form = document.getElementById("product-form");
    const tableBody = document.getElementById("product-table-body");

    // نجيب بيانات الكاتيجوري من Django (جاية كـ JSON في صفحة المنتجات)
    const categoriesData = JSON.parse(document.getElementById("categories-data").textContent);

    // ========== Add / Update ==========

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        console.log("Form Data:", [...formData.entries()]); // 👈
        const productId = form.querySelector("#product_id").value;
        const url = productId ? `/products/${productId}/edit/` : "/products/";

        fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: formData,
        })
            .then(res => res.json())
            .then(data => {
                console.log("Response from server (ADD/EDIT):", data);

                if (data.status === "success") {
                    Swal.fire({
                        icon: "success",
                        title: productId ? "Updated" : "Added",
                        text: `Product ${productId ? "updated" : "added"} successfully!`
                    });

                    if (!productId) {
                        // إضافة صف جديد للجدول مباشرة
                        const row = document.createElement("tr");
                        row.setAttribute("data-id", data.product_id);
                        row.setAttribute("data-category-id", data.category_id);
                        row.innerHTML = `
                        <td>${data.product_id}</td>
                        <td class="product-name">${data.name}</td>
                        <td class="product-desc">${data.description}</td>
                        <td class="product-price">${data.price}</td>
                        <td class="product-cond">${data.condition}</td>
                        <td class="product-stock">${data.stock_quantity}</td>
                        <td>${data.image ? `<img src="${data.image}" width="50">` : "No Image"}</td>
                        <td class="product-category" data-category-id="${data.category_id}">${data.category_name}</td>
                        <td>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-warning edit-btn">Edit</button>
                                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
                            </div>
                        </td>
                    `;
                        tableBody.appendChild(row);
                        form.reset();
                    } else {
                        window.location.reload();
                    }
                } else {
                    Swal.fire("Error", data.message, "error");
                }
            });
    });

    // ========== Edit + Delete ==========
    tableBody.addEventListener("click", function (e) {
        const row = e.target.closest("tr");
        if (!row) return;

        const productId = row.dataset.id;
        const editBtn = e.target.closest(".edit-btn");
        const deleteBtn = e.target.closest(".delete-btn");

        // ---- Edit ----
        if (editBtn) {
            const currentData = {
                name: row.querySelector(".product-name").textContent,
                description: row.querySelector(".product-desc").textContent,
                price: row.querySelector(".product-price").textContent,
                condition: row.querySelector(".product-cond").textContent,
                stock: row.querySelector(".product-stock").textContent,
                category: row.querySelector(".product-category").dataset.categoryId,
                image: row.querySelector("img") ? row.querySelector("img").src : null
            };

            // خيارات الكاتيجوري
            let categoriesOptions = categoriesData.map(cat => {
                let isSelected = parseInt(currentData.category) === parseInt(cat.category_id) ? "selected" : "";
                return `<option value="${cat.category_id}" ${isSelected}>${cat.name}</option>`;
            }).join("");

            Swal.fire({
                title: "Edit Product",
                html: `
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <label>Name</label>
                            <input id="swal-name" class="form-control" value="${currentData.name}">
                        </div>
                        <div class="col-md-6 mb-2">
                            <label>Price</label>
                            <input id="swal-price" type="number" step="0.01" class="form-control" value="${currentData.price}">
                        </div>
                        <div class="col-md-12 mb-2">
                            <label>Description</label>
                            <textarea id="swal-description" class="form-control">${currentData.description}</textarea>
                        </div>
                        <div class="col-md-6 mb-2">
                            <label>Condition</label>
                            <input id="swal-condition" class="form-control" value="${currentData.condition}">
                        </div>
                        <div class="col-md-6 mb-2">
                            <label>Stock</label>
                            <input id="swal-stock" type="number" class="form-control" value="${currentData.stock}">
                        </div>
                        <div class="col-md-12 mb-2">
                            <label>Category</label>
                            <select id="swal-category" class="form-control">
                                ${categoriesOptions}
                            </select>
                        </div>
                        <div class="col-md-12 mb-2">
                            <label>Image</label><br>
                            ${currentData.image ? `<img src="${currentData.image}" alt="Product" width="80" class="mb-2"><br>` : ""}
                            <input id="swal-image" type="file" class="form-control">
                        </div>
                    </div>
                `,
                width: "600px",
                showCancelButton: true,
                confirmButtonText: "Save",
                preConfirm: () => {
                    const formData = new FormData();
                    formData.append("name", document.getElementById("swal-name").value);
                    formData.append("description", document.getElementById("swal-description").value);
                    formData.append("price", document.getElementById("swal-price").value);
                    formData.append("condition", document.getElementById("swal-condition").value);
                    formData.append("stock_quantity", document.getElementById("swal-stock").value);
                    formData.append("category", document.getElementById("swal-category").value);

                    const newImage = document.getElementById("swal-image").files[0];
                    if (newImage) {
                        formData.append("image", newImage);
                    }

                    return fetch(`/products/${productId}/edit/`, {
                        method: "POST",
                        headers: { "X-CSRFToken": csrftoken },
                        body: formData,
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success") {
                                return data;
                            } else {
                                Swal.showValidationMessage(data.message || "Update failed");
                            }
                        });
                }
            }).then(result => {
                if (result.isConfirmed) {
                    Swal.fire("Updated!", "Product updated successfully!", "success")
                        .then(() => window.location.reload());
                }
            });
        }

        // ---- Delete ----
        if (deleteBtn) {
            Swal.fire({
                title: "Are you sure?",
                text: "This action cannot be undone!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Yes, delete it!",
                cancelButtonText: "Cancel"
            }).then(result => {
                if (result.isConfirmed) {
                    fetch(`/products/${productId}/delete/`, {
                        method: "POST",
                        headers: { "X-CSRFToken": csrftoken },
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success") {
                                row.remove();
                                Swal.fire("Deleted!", "Product removed successfully!", "success");
                            } else {
                                Swal.fire("Error", data.message, "error");
                            }
                        });
                }
            });
        }
    });
});
