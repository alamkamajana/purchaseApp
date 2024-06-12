document.addEventListener("DOMContentLoaded", function () {
    const createDeliveryOrderBtn = document.getElementById("create-delivery-order-btn");
    const doList = document.getElementById("do-list");
    let pe_name = document.getElementById("purchase_event_name").value;
    let pe_id = document.getElementById("purchase_event_id").value;

    let isActiveRow = false; // Flag to track if there is an active row

    createDeliveryOrderBtn.addEventListener("click", function () {
        if (isActiveRow) {
            alert("Please complete the current row before adding a new one.");
            return;
        }

        const newRow = document.createElement("tr");
        isActiveRow = true; // Set the flag to true when a new row is added

        newRow.innerHTML = `
            <form id="delivery-order-form">
            <input type="hidden" name="pe" id="pe_id" class="form-control" value="${pe_id}" placeholder="Purchase Event">
            <td><input type="text" class="form-control" placeholder="DO Name" id="do-name" readonly></td>
            <td><input type="text" name="driver" class="form-control" placeholder="Driver" id="driver"></td>
            <td><input type="text" name="vehicle_number" class="form-control" placeholder="Vehicle" id="vehicle-number"></td>
            <td><input type="text" class="form-control" value="${pe_name}" placeholder="Purchase Event" id="purchase-event-id" readonly></td>
            <td>
                <button type="submit" class="btn btn-sm btn-success confirm-btn" id="">Confirm</button>
                <button type="button" class="btn btn-sm btn-danger btn-cancel">Cancel</button>
            </td>
        </form>
        `;
        doList.appendChild(newRow);

        const confirmBtn = newRow.querySelector(".confirm-btn");
        confirmBtn.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent the default form submission
            let driver_value = document.getElementById("driver").value;
            let vehicle_number = document.getElementById("vehicle-number").value;
            let pe = document.getElementById("pe_id").value;
            const params = new URLSearchParams({
                driver: driver_value,
                vehicle_number: vehicle_number,
                pe: pe
            });
            fetch(`/delivery/create?${params.toString()}`, {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status == 200) {
                        // Update the row with the confirmed data
                        newRow.innerHTML = `
                        <td>${data.do_name}</td>
                        <td>${driver_value}</td>
                        <td>${vehicle_number}</td>
                        <td>${pe_name}</td>
                        <td>
                            <button value="${data.new_id}" class="btn btn-sm btn-success btn-add-goods">
                                Add Goods
                            </button>
                        </td>
                    `;
                        isActiveRow = false; // Reset the flag when the row is confirmed
                    } else {
                        alert("Failed to create delivery order");
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert("Error occurred while creating delivery order");
                });
        });

        const cancelButton = newRow.querySelector(".btn-cancel");
        cancelButton.addEventListener("click", function () {
            newRow.remove();
            isActiveRow = false; // Reset the flag when the row is cancelled
        });
    });
});
