document.addEventListener("DOMContentLoaded", function() {
    let form = document.getElementById("productForm");

    form.addEventListener("submit", function(e){
        e.preventDefault(); // منع الريفرش

        let formData = new FormData(form);

        fetch("", {   // يرسل لنفس URL الحالي
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                let tbody = document.querySelector("table tbody");
                let row = `
                    <tr>
                        <td>${data.id}</td>
                        <td>${data.name}</td>
                        <td>${data.description}</td>
                        <td>${data.price}</td>
                        <td>${data.condition}</td>
                        <td>${data.stock}</td>
                        <td>${data.image_url ? `<img src="${data.image_url}" width="50">` : "No Image"}</td>
                        <td>${data.category}</td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
                form.reset(); // تصفير الفورم بعد الإضافة
            } else {
                alert(data.message);
            }
        });
    });
});

// دالة لجلب CSRF Token من الكوكيز
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
