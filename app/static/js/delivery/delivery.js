$(document).ready(function () {
    const createDeliveryOrderForm = document.getElementById('create-delivery-order-form');

    createDeliveryOrderForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(createDeliveryOrderForm);
        const formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });

        fetch('/delivery/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formObject)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status == 200) {
                    window.location.reload()
                }
                // Handle the response data as needed
                // You can show a success message or redirect to another page
            })
            .catch(error => {
                console.error('Error:', error);
                // Handle the error as needed
            });
    });
});
