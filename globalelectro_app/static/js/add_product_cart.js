// add_product_cart.js
document.addEventListener("DOMContentLoaded", () => {
    const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");

    addToCartButtons.forEach(button => {
        button.addEventListener("click", () => {
            const productId = button.dataset.productId;
            const quantityInput = document.querySelector(`#quantity-${productId}`);
            const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

            addToCart(productId, quantity);
        });
    });
});

function addToCart(productId, quantity) {
    fetch("/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")  // مهم لتجنب CSRF error
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();  // تحويل الاستجابة لـ JSON
    })
    .then(data => {
        if (data.success) {
            alert(data.message);  // ممكن تغيرها لإظهار رسالة على الصفحة بدل alert
        } else {
            console.error("Cart Error:", data.message);
            alert("Error: " + data.message);
        }
    })
    .catch(err => {
        console.error("Fetch Error:", err);
        alert("An error occurred while adding the product to cart.");
    });
}

// ===== Helper =====
// دالة لجلب CSRF Token من الكوكيز
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // تحقق من بداية الكوكيز
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
