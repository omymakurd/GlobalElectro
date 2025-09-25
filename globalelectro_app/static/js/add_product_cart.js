document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    // كل زر Add to Cart في البطاقات
    document.querySelectorAll(".product-card .btn-warning").forEach(btn => {
        btn.addEventListener("click", function () {
            const productCard = this.closest(".product-card");
            const productId = productCard.dataset.id;

            fetch("/cart/add/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ product_id: productId, quantity: 1 })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    Swal.fire("Added!", "Product added to cart successfully!", "success");
                } else {
                    Swal.fire("Error", data.message || "Could not add to cart", "error");
                }
            });
        });
    });

    // التعامل مع View Details لفتح المودال
    document.querySelectorAll(".view-details-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const modal = new bootstrap.Modal(document.getElementById("productModal"));
            
            document.getElementById("modal-product-image").src = this.dataset.image;
            document.getElementById("modal-product-name").textContent = this.dataset.name;
            document.getElementById("modal-product-description").textContent = this.dataset.description;
            document.getElementById("modal-product-condition").textContent = this.dataset.condition;
            document.getElementById("modal-product-stock").textContent = this.dataset.stock > 0 ? "In Stock" : "Out of Stock";
            document.getElementById("modal-product-price").textContent = this.dataset.price;

            // ضبط الـ data-id لزر Add to Cart في المودال
            const modalAddBtn = document.getElementById("modal-add-to-cart");
            modalAddBtn.dataset.id = this.dataset.id;

            modal.show();
        });
    });

    // زر Add to Cart في المودال
    const modalAddBtn = document.getElementById("modal-add-to-cart");
    if(modalAddBtn){
        modalAddBtn.addEventListener("click", function(){
            const productId = this.dataset.id;
            const quantity = parseInt(document.getElementById("modal-product-quantity").value) || 1;

            fetch("/cart/add/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ product_id: productId, quantity: quantity })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === "success"){
                    Swal.fire("Added!", "Product added to cart successfully!", "success");
                } else {
                    Swal.fire("Error", data.message || "Could not add to cart", "error");
                }
            });
        });
    }
});
