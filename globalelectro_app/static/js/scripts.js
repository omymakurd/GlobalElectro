// Navbar scroll effect
window.addEventListener("scroll", function () {
  const navbar = document.querySelector(".custom-navbar");
  if (window.scrollY > 50) {
    navbar.classList.add("navbar-scrolled");
  } else {
    navbar.classList.remove("navbar-scrolled");
  }
});

// Dark mode toggle
const toggleBtn = document.getElementById("darkModeToggle");
toggleBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  const icon = toggleBtn.querySelector("i");
  if (document.body.classList.contains("dark-mode")) {
    icon.classList.replace("bi-moon", "bi-sun");
  } else {
    icon.classList.replace("bi-sun", "bi-moon");
  }
});
window.addEventListener("DOMContentLoaded", function () {
  const heroText = document.querySelector(".hero-text");
  setTimeout(() => {
    heroText.classList.add("show");
  }, 300); // تأخير بسيط عشان يبين بشكل ناعم
});


  document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".category-card");

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show");
        }
      });
    }, { threshold: 0.2 });

    cards.forEach((card) => {
      observer.observe(card);
    });
  });
  document.addEventListener("DOMContentLoaded", function () {
    const detailButtons = document.querySelectorAll(".view-details-btn");
    const modal = new bootstrap.Modal(document.getElementById("productModal"));

    detailButtons.forEach(button => {
      button.addEventListener("click", function () {
        // ناخد الداتا من attributes
        const name = this.dataset.name;
        const description = this.dataset.description;
        const price = this.dataset.price;
        const condition = this.dataset.condition;
        const stock = this.dataset.stock;
        const image = this.dataset.image;

        // نحدث المودال
        document.getElementById("modal-product-name").textContent = name;
        document.getElementById("modal-product-description").textContent = description;
        document.getElementById("modal-product-price").textContent = price;
        document.getElementById("modal-product-condition").textContent = condition;
        document.getElementById("modal-product-image").src = image;

        const stockSpan = document.getElementById("modal-product-stock");
        if (parseInt(stock) > 0) {
          stockSpan.innerHTML = '<span class="badge bg-success">In Stock</span>';
        } else {
          stockSpan.innerHTML = '<span class="badge bg-danger">Out of Stock</span>';
        }

        // نعرض المودال
        modal.show();
      });
    });
  });