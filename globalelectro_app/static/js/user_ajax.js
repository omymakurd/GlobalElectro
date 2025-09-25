$(document).ready(function () {
    const form = $("#user-form");
    const tableBody = $("#users-table-body");

    // ========== Add User ==========
    form.on("submit", function (e) {
        e.preventDefault();

        let formData = new FormData(this);

        $.ajax({
            url: "/users/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.status === "success") {
                    // إضافة الصف الجديد
                    tableBody.append(`
                        <tr id="user-${response.user_id}">
                            <td>${response.user_id}</td>
                            <td>${response.first_name}${response.last_name}</td>
                            <td>${response.email}</td>
                            <td>${response.role}</td>
                            <td>${response.phone}</td>
                            <td>${response.address}</td>
                            <td>
                                <button class="btn btn-sm btn-warning edit-user" data-id="${response.user_id}">Edit</button>
                                <button class="btn btn-sm btn-danger delete-user" data-id="${response.user_id}">Delete</button>
                            </td>
                        </tr>
                    `);

                    // ✅ alert النجاح
                    Swal.fire({
                        icon: "success",
                        title: "User Added",
                        text: "The user has been added successfully!",
                        showConfirmButton: false,
                        timer: 2000
                    });

                    // reset للفورم
                    form[0].reset();
                } else {
                    // ✅ alert الخطأ
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: response.message,
                    });
                }
            },
            error: function () {
                Swal.fire({
                    icon: "error",
                    title: "Server Error",
                    text: "Something went wrong! Please try again later.",
                });
            }
        });
    });

    // ========== Delete User ==========
    tableBody.on("click", ".delete-user", function () {
        let userId = $(this).data("id");

        Swal.fire({
            title: "Are you sure?",
            text: "This user will be deleted permanently!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Yes, delete it!"
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/users/delete/${userId}/`,
                    type: "POST",
                    data: { csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val() },
                    success: function (response) {
                        if (response.status === "success") {
                            $(`#user-${userId}`).remove();

                            Swal.fire({
                                icon: "success",
                                title: "Deleted!",
                                text: "User has been deleted.",
                                showConfirmButton: false,
                                timer: 2000
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Error",
                                text: response.message,
                            });
                        }
                    },
                    error: function () {
                        Swal.fire({
                            icon: "error",
                            title: "Server Error",
                            text: "Something went wrong!",
                        });
                    }
                });
            }
        });
    });

});
