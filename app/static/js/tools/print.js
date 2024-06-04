function btPrint() {
    var SERVICE = '000018f0-0000-1000-8000-00805f9b34fb';
    var WRITE = '00002af1-0000-1000-8000-00805f9b34fb';

    var currentDate = new Date();

    // Get the current date components
    var year = currentDate.getFullYear();
    var month = currentDate.getMonth() + 1; // Adding 1 because getMonth() returns zero-based month (0 for January, 1 for February, etc.)
    var day = currentDate.getDate();

    // Format the date as needed (e.g., YYYY-MM-DD)
    var formattedDate = year + "-" + (month < 10 ? "0" + month : month) + "-" + (day < 10 ? "0" + day : day);
    console.log(formattedDate);

    var code_petani = document.getElementById("farmer_code").value;
    var nama_petani = document.getElementById("farmer_name").value;

    var DATA = ''
        + '\x1B' + '\x61' + '\x31'
        + '\x1D' + '\x21' + '\x00' + 'TRIPPER\nWE ADD VALUE AT ORIGIN\n\n'
        + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
        + 'Tanggal\t: ' + formattedDate
        + '\nID Petani\t: ' + code_petani
        + '\nNama\t: ' + nama_petani
        + '\n\n';

    var deviceHandle;
    navigator.bluetooth.requestDevice({filters: [{services: [SERVICE]}]}).then(device => {
        console.log(device);
        deviceHandle = device;
        return device.gatt.connect()
    }).then(server => {
        console.log(server);
        return server.getPrimaryService(SERVICE);
    }).then(service => {
        console.log(service);
        return service.getCharacteristic(WRITE);
    }).then(channel => {
        console.log(channel);
        return channel.writeValue(new TextEncoder("utf-8").encode(DATA));
    }).catch(error => {
        console.error(error)
    }).finally(() => {
        deviceHandle.gatt.disconnect();
    });
}

async function btPrint2() {
    var SERVICE = '000018f0-0000-1000-8000-00805f9b34fb';
    var WRITE = '00002af1-0000-1000-8000-00805f9b34fb';

    var currentDate = new Date();

    // Get the current date components
    var year = currentDate.getFullYear();
    var month = currentDate.getMonth() + 1; // Adding 1 because getMonth() returns zero-based month (0 for January, 1 for February, etc.)
    var day = currentDate.getDate();

    // Format the date as needed (e.g., YYYY-MM-DD)
    var formattedDate = year + "-" + (month < 10 ? "0" + month : month) + "-" + (day < 10 ? "0" + day : day);


    var code_petani = document.getElementById("farmer_code").value;
    var nama_petani = document.getElementById("farmer_name").value;
    let order_id = document.getElementById("purchase_order_id").value;
    let order_name = document.getElementById("purchase_order_name").value;
    let event_name = document.getElementById("purchase_event_id").value;
    let odoo_name = document.getElementById("purchase_order_odoo_id").value;
    let certification_status = document.getElementById("certification_status_id").value;
    const purchaseData = await fetchPurchaseData(order_id);
    // const purchaseData = [
    //   { product_name: "Kopi Arabica",price: 25000, quantity: 2, subtotal: 25000 },
    //   { product_name: "Beras Merah",price: 25000, quantity: 5, subtotal: 12000 },
    //   { product_name: "Gula Aren",price: 25000, quantity: 1, subtotal: 18000 }
    // ]
    const tableData = generateTable(purchaseData);
    const totalAmount = purchaseData.reduce((sum, item) => sum + item.quantity * item.price, 0);
    const formattedTotalAmount = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0
    }).format(totalAmount).replace(/Rp\s*/g, "");


    var DATA = ''
        + '\x1B' + '\x61' + '\x31'
        + '\x1D' + '\x21' + '\x00' + 'TRIPPER\nWE ADD VALUE AT ORIGIN\n\n'
        + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
        + `Order\t: ${order_name}`
        + '\nPE\t: ' + event_name
        + '\nPO\t: ' + odoo_name
        + '\nTanggal\t: ' + formattedDate
        + '\nID Petani\t: ' + code_petani
        + '\nNama\t: ' + nama_petani
        + '\nCertification Status\t: ' + certification_status
        + '\n'
        + `\x1B\x21\x01${tableData}`
        + `\nTotal\tRp.${formattedTotalAmount}\n\n\x1B\x21\x00 `
        + '\n\n'

    console.log(DATA)
    let deviceHandle;
    navigator.bluetooth.requestDevice({filters: [{services: [SERVICE]}]}).then(device => {
        deviceHandle = device;
        return device.gatt.connect()
    }).then(server => {
        return server.getPrimaryService(SERVICE);
    }).then(service => {
        return service.getCharacteristic(WRITE);
    }).then(channel => {
        const xhr = new XMLHttpRequest();
        const url = `/purchase/transaction/confirm2?purchase_order=${order_id}`;
        xhr.open("GET", url);
        xhr.send();
        return channel.writeValue(new TextEncoder("utf-8").encode(DATA));
    }).catch(error => {
    }).finally(() => {
        deviceHandle.gatt.disconnect();
        window.location.reload()
    });
}

function generateTable(purchaseData) {
    let table = "\n";
    for (const item of purchaseData) {
        const productName = item.product_name.substring(0, 25);

        // Format price and subtotal as IDR currency, remove Rp and spaces
        const formattedPrice = new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
            minimumFractionDigits: 0
        }).format(item.price).replace(/Rp\s*/g, ""); // Remove "Rp" and any spaces

        const formattedSubtotal = new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
            minimumFractionDigits: 0
        }).format(item.subtotal).replace(/Rp\s*/g, "");

        table += `\n${item.product_code}\n${productName}\nRp.${formattedPrice}\n${item.quantity}\nRp.${formattedSubtotal}\n`;
    }
    return table;
}

async function fetchPurchaseData(orderId) {
    try {
        const response = await fetch(`/purchase/transaction/items?purchase_order=${orderId}`);
        if (!response.ok) {
            throw new Error(`Error fetching purchase data: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching purchase data:", error);
        // Handle the error appropriately (e.g., display an error message to the user)
        return null; // Or return an empty array []
    }
}


async function fetchImageData(imgSrc) {
    try {
        const response = await fetch(imgSrc);
        const blob = await response.blob();
        const binaryData = await readBlobAsArrayBuffer(blob);
        return binaryData;
    } catch (error) {
        console.error('Error fetching image:', error);
        return null; // or handle the error as needed
    }
}

function readBlobAsArrayBuffer(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            resolve(reader.result);
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(blob);
    });
}