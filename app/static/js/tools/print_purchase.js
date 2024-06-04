// let progress = document.querySelector('#progress');
// let dialog = document.querySelector('#dialog');
// let message = document.querySelector('#message');
// let printButton = document.querySelector('#print');
let printCharacteristic;
let index = 0;
let data;

let image = document.querySelector('#sig-image');
// Use the canvas to get image data
let canvas = document.createElement('canvas');
// Canvas dimensions need to be a multiple of 40 for this printer
canvas.width = 360;
canvas.height = 190;
imageWidth = canvas.width / 2;
imageHeight = imageWidth / 966 * 950;
let context = canvas.getContext("2d");
let offsetX = (canvas.width - imageWidth) / 2 + 1;
context.drawImage(image, offsetX, 0, imageWidth, imageHeight);
let imageData = context.getImageData(0, 0, canvas.width, canvas.height).data;

function getDarkPixel(x, y) {
    // Return the pixels that will be printed black
    let red = imageData[((canvas.width * y) + x) * 4];
    let green = imageData[((canvas.width * y) + x) * 4 + 1];
    let blue = imageData[((canvas.width * y) + x) * 4 + 2];
    return (red + green + blue) > 0 ? 1 : 0;
}

function getImagePrintData() {
    if (imageData == null) {
        console.log('No image to print!');
        return new Uint8Array([]);
    }
    // Each 8 pixels in a row is represented by a byte
    let printData = new Uint8Array(canvas.width / 8 * canvas.height + 8);
    let offset = 0;
    // Set the header bytes for printing the image
    printData[0] = 29;  // Print raster bitmap
    printData[1] = 118; // Print raster bitmap
    printData[2] = 48; // Print raster bitmap
    printData[3] = 0;  // Normal 203.2 DPI
    printData[4] = canvas.width / 8; // Number of horizontal data bits (LSB)
    printData[5] = 0; // Number of horizontal data bits (MSB)
    printData[6] = canvas.height % 256; // Number of vertical data bits (LSB)
    printData[7] = canvas.height / 256;  // Number of vertical data bits (MSB)
    offset = 7;
    // Loop through image rows in bytes
    for (let i = 0; i < canvas.height; ++i) {
        for (let k = 0; k < canvas.width / 8; ++k) {
            let k8 = k * 8;
            //  Pixel to bit position mapping
            printData[++offset] = getDarkPixel(k8 + 0, i) * 128 + getDarkPixel(k8 + 1, i) * 64 +
                getDarkPixel(k8 + 2, i) * 32 + getDarkPixel(k8 + 3, i) * 16 +
                getDarkPixel(k8 + 4, i) * 8 + getDarkPixel(k8 + 5, i) * 4 +
                getDarkPixel(k8 + 6, i) * 2 + getDarkPixel(k8 + 7, i);
        }
    }
    return printData;
}

function handleError(error) {
    console.log(error);
    printCharacteristic = null;
}

function sendNextImageDataBatch(resolve, reject) {
    // Can only write 512 bytes at a time to the characteristic
    // Need to send the image data in 512 byte batches
    if (index + 512 < data.length) {
        printCharacteristic.writeValue(data.slice(index, index + 512)).then(() => {
            index += 512;
            sendNextImageDataBatch(resolve, reject);
        })
            .catch(error => reject(error));
    } else {
        // Send the last bytes
        if (index < data.length) {
            printCharacteristic.writeValue(data.slice(index, data.length)).then(() => {
                resolve();
            })
                .catch(error => reject(error));
        } else {
            resolve();
        }
    }
}


async function sendTextData(product) {
    // Get the bytes for the text
    let encoder = new TextEncoder("utf-8");
    // Add line feed + carriage return chars to text
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

    ;
    return printCharacteristic.writeValue(new TextEncoder("utf-8").encode(DATA))
}

async function addSpace(product) {
    let DATA = '\n\n\n'
    return printCharacteristic.writeValue(new TextEncoder("utf-8").encode(DATA))
}

async function sendImageData() {
    data = getImagePrintData();
    return new Promise(function (resolve, reject) {
        sendNextImageDataBatch(resolve, reject);
    });
}

function printDelivery(products) {
    if (printCharacteristic == null) {
        navigator.bluetooth.requestDevice({
            filters: [{
                services: ['000018f0-0000-1000-8000-00805f9b34fb']
            }]
        })
            .then(device => {
                console.log('> Found ' + device.name);
                console.log('Connecting to GATT Server...');
                return device.gatt.connect();
            })
            .then(server => server.getPrimaryService("000018f0-0000-1000-8000-00805f9b34fb"))
            .then(service => service.getCharacteristic("00002af1-0000-1000-8000-00805f9b34fb"))
            .then(characteristic => {
                // Cache the characteristic
                printCharacteristic = characteristic;
                processItem(products);
            })
            .catch(handleError);
    } else {
        processItem(products);
    }
};

function deliveryInfo() {
    let products = [1,2]

    products.forEach(product => {
    })
    printDelivery(products)

}

async function processItem(product) {
    return new Promise((resolve, reject) => {
        sendTextData(product)
            .then(() => sendImageData()).then(() => addSpace())
            .then(() => {
                resolve();
            })
            .catch(handleError);
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
        return null;
    }
}


