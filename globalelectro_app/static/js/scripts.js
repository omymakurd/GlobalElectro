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

// Hero text fade-in
window.addEventListener("DOMContentLoaded", function () {
  const heroText = document.querySelector(".hero-text");
  setTimeout(() => {
    heroText.classList.add("show");
  }, 300);
});

// Category cards animation
document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".category-card");
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
      }
    });
  }, { threshold: 0.2 });

  cards.forEach((card) => observer.observe(card));
});

// Product details modal
document.addEventListener("DOMContentLoaded", function () {
  const detailButtons = document.querySelectorAll(".view-details-btn");
  const modal = new bootstrap.Modal(document.getElementById("productModal"));
  const modalEl = document.getElementById("productModal");

  detailButtons.forEach(button => {
    button.addEventListener("click", function () {
      // تحديث البيانات من attributes
      document.getElementById("modal-product-name").textContent = this.dataset.name;
      document.getElementById("modal-product-description").textContent = this.dataset.description;
      document.getElementById("modal-product-price").textContent = this.dataset.price;
      document.getElementById("modal-product-condition").textContent = this.dataset.condition;
      document.getElementById("modal-product-image").src = this.dataset.image;

      const stockSpan = document.getElementById("modal-product-stock");
      if (parseInt(this.dataset.stock) > 0) {
        stockSpan.innerHTML = '<span class="badge bg-success">In Stock</span>';
      } else {
        stockSpan.innerHTML = '<span class="badge bg-danger">Out of Stock</span>';
      }

      // عرض المودال
      modal.show();
    });
  });

  // عند إغلاق المودال، إعادة تعيين البيانات وإزالة backdrop
  modalEl.addEventListener("hidden.bs.modal", () => {
    document.getElementById("modal-product-name").textContent = "";
    document.getElementById("modal-product-description").textContent = "";
    document.getElementById("modal-product-price").textContent = "";
    document.getElementById("modal-product-condition").textContent = "";
    document.getElementById("modal-product-image").src = "";
    document.getElementById("modal-product-stock").innerHTML = "";

    // إزالة أي backdrop تبقى
    document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
  });
});
