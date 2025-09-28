
document.addEventListener("DOMContentLoaded", function() {
    const csrftoken = document.getElementById('csrf-token').value;

    // تحديث الحالة
    document.querySelectorAll('.order-status').forEach(select => {
        select.addEventListener('change', function() {
            const orderId = this.dataset.orderId;
            const newStatus = this.value;

            fetch(`/orders/update-status/${orderId}/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json','X-CSRFToken': csrftoken},
                body: JSON.stringify({status: newStatus})
            }).then(res => res.json())
              .then(data => {
                if(data.status==='success'){
                    const badge = this.closest('td').querySelector('.badge');
                    badge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                    badge.className = 'badge ' + 
                        (newStatus==="pending" ? 'bg-warning' :
                         newStatus==="shipped" ? 'bg-info' :
                         newStatus==="delivered" ? 'bg-success' :
                         newStatus==="cancelled" ? 'bg-danger' :
                         newStatus==="paid" ? 'bg-paid' : '');
                } else { alert('Failed: '+(data.message||'')); }
              }).catch(err=>{console.error(err); alert('Error updating status');});
        });
    });

    // عرض التفاصيل
    document.querySelectorAll('.view-details').forEach(button=>{
        button.addEventListener('click', function(){
            const orderId = this.closest('tr').dataset.orderId;
            const modalBody = document.getElementById('modal-body-content');

            fetch(`/orders/details/${orderId}/`)
            .then(res=>res.json())
            .then(data=>{
                if(data.status==='success'){
                    const order = data.order;
                    let productsHtml = '<ul>';
                    order.products.forEach(p=>{
                        productsHtml += `<li>${p.name} - ${p.quantity} x ${p.price} = ${p.subtotal}</li>`;
                    });
                    productsHtml += '</ul>';
                    modalBody.innerHTML = `
                        <p><strong>Order ID:</strong> ${order.order_id}</p>
                        <p><strong>User:</strong> ${order.user}</p>
                        <p><strong>Total Price:</strong> ${order.total_price}</p>
                        <p><strong>Status:</strong> ${order.status}</p>
                        <p><strong>Created At:</strong> ${order.created_at}</p>
                        <p><strong>Products:</strong>${productsHtml}</p>
                    `;
                    new bootstrap.Modal(document.getElementById('orderModal')).show();
                } else { alert('Failed to load order details'); }
            }).catch(err=>{console.error(err); alert('Error loading details');});
        });
    });

    // إلغاء الطلب
    document.querySelectorAll('.cancel-order').forEach(button=>{
        button.addEventListener('click', function(){
            const row = this.closest('tr');
            const orderId = row.dataset.orderId;
            if(!confirm('Are you sure you want to cancel this order?')) return;
            fetch(`/orders/update-status/${orderId}/`, {
                method:'POST',
                headers:{'Content-Type':'application/json','X-CSRFToken':csrftoken},
                body:JSON.stringify({status:'cancelled'})
            }).then(res=>res.json())
              .then(data=>{
                if(data.status==='success'){
                    row.querySelector('.order-status').value='cancelled';
                    const badge = row.querySelector('.badge');
                    badge.textContent='Cancelled';
                    badge.className='badge bg-danger';
                } else { alert('Failed to cancel: '+(data.message||'')); }
              }).catch(err=>{console.error(err); alert('Error cancelling order');});
        });
    });

    // Print Invoice
    document.querySelectorAll('.print-invoice').forEach(btn=>{
        btn.addEventListener('click', function(){
            const orderId = this.closest('tr').dataset.orderId;
            window.open(`/orders/print-invoice/${orderId}/`, '_blank');
        });
    });

    // Send Email
    document.querySelectorAll('.send-email').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.closest('tr').dataset.orderId;

            fetch(`/orders/send-email/${orderId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({})
            })
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                if(data.status === 'success'){
                    alert(`✅ Email sent successfully for Order #${orderId}`);
                } else {
                    alert(`❌ Failed to send email for Order #${orderId}: ${data.message}`);
                }
            })
            .catch(err => {
                console.error(err);
                alert(`❌ Error sending email for Order #${orderId}`);
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("filter-form");
    const statusSelect = document.getElementById("status-select");
    const searchInput = document.getElementById("search-input");

    // فلترة مباشرة عند تغيير select
    statusSelect.addEventListener("change", function() {
        form.submit();
    });

    // فلترة مباشرة عند الكتابة بالبحث (مع تأخير 0.5 ثانية)
    let typingTimer;
    searchInput.addEventListener("keyup", function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            form.submit();
        }, 500);
    });
});

