// scripts.js
document.addEventListener("DOMContentLoaded", () => {

    // ========== عناصر أساسية ==========
    const productModal = document.getElementById("productModal");
    const modal = productModal ? new bootstrap.Modal(productModal) : null;

    const modalProductImage = document.getElementById("modal-product-image");
    const modalProductName = document.getElementById("modal-product-name");
    const modalProductDescription = document.getElementById("modal-product-description");
    const modalProductCondition = document.getElementById("modal-product-condition");
    const modalProductStock = document.getElementById("modal-product-stock");
    const modalProductPrice = document.getElementById("modal-product-price");
    const modalProductQuantity = document.getElementById("modal-product-quantity");
    const modalAddToCartBtn = document.getElementById("modal-add-to-cart-btn");

    // ========== فتح المودال عند الضغط على تفاصيل المنتج ==========
    const detailButtons = document.querySelectorAll(".view-details-btn");
    detailButtons.forEach(button => {
        button.addEventListener("click", () => {
            const productId = button.dataset.id;
            const name = button.dataset.name;
            const description = button.dataset.description;
            const price = button.dataset.price;
            const condition = button.dataset.condition;
            const stock = button.dataset.stock;
            const image = button.dataset.image;

            if (modalProductName) modalProductName.textContent = name;
            if (modalProductDescription) modalProductDescription.textContent = description;
            if (modalProductCondition) modalProductCondition.textContent = condition;
            if (modalProductStock) {
                modalProductStock.textContent = stock > 0 ? "In Stock" : "Out of Stock";
                modalProductStock.className = stock > 0 ? "text-success" : "text-danger";
            }
            if (modalProductPrice) modalProductPrice.textContent = price;
            if (modalProductImage) modalProductImage.src = image;

            if (modalAddToCartBtn) modalAddToCartBtn.dataset.productId = productId;

            if (modal) modal.show();
        });
    });

    // ========== زر الإضافة من داخل المودال ==========
    if (modalAddToCartBtn) {
        modalAddToCartBtn.addEventListener("click", () => {
            const productId = modalAddToCartBtn.dataset.productId;
            const quantity = parseInt(modalProductQuantity.value) || 1;
            addToCart(productId, quantity);
            if (modal) modal.hide();
        });
    }

    // ========== زر الإضافة المباشر (من الكارد) ==========
    const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");
    addToCartButtons.forEach(button => {
        button.addEventListener("click", () => {
            const productId = button.dataset.productId;
            addToCart(productId, 1);
        });
    });

    // ========== دالة الإضافة إلى السلة ==========
    function addToCart(productId, quantity) {
        fetch("/cart/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // تحديث عداد الكارت
                    const cartCountElement = document.getElementById("cart-count");
                    if (cartCountElement) {
                        let currentCount = parseInt(cartCountElement.textContent) || 0;
                        cartCountElement.textContent = currentCount + quantity;
                    }
                    Swal.fire({
                        icon: "success",
                        title: "Success",
                        text: data.message,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                    if (modal) modal.hide();
                    // إزالة أي backdrop متبقي
                    document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
                    document.body.classList.remove("modal-open");
                    document.body.style = "";
                });

                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message
                    })
                }
            })
            .catch(err => {
                console.error("Fetch Error:", err);
                alert("An error occurred while adding the product to cart.");
            });
    }

    // ========== دالة جلب CSRF ==========
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

});
