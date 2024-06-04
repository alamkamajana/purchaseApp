
// let progress = document.querySelector('#progress');
// let dialog = document.querySelector('#dialog');
// let message = document.querySelector('#message');
// let printButton = document.querySelector('#print');
let printCharacteristic;
let index = 0;
let data;
let poName = document.getElementById('po_name').innerHTML.trim()
let poPartner = document.getElementById('po_partner').innerHTML.trim()
let eventName = document.getElementById('event_name').value
let orderName = document.getElementById('order_name').value
let orderDriver = document.getElementById('order_driver').innerHTML.trim()
let orderVehicle = document.getElementById('order_vehicle').value
let orderOrigin = document.getElementById('order_origin').value
let orderDestination = document.getElementById('order_destination').value
let orderDate = document.getElementById('order_date').value
let receivedDate = document.getElementById('received_date').value
let doId = document.getElementById('do_id').innerHTML.trim()

let image = document.querySelector('#tripper-logo-black');
// Use the canvas to get image data
let canvas = document.createElement('canvas');
// Canvas dimensions need to be a multiple of 40 for this printer
canvas.width = 360;
canvas.height = 60;
imageWidth = canvas.width/2;
imageHeight = imageWidth/966*277;
let context = canvas.getContext("2d");
let offsetX = (canvas.width - imageWidth) / 2 + 10;
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

function sendImageData() {
    index = 0;
    data = getImagePrintData();
    return new Promise(function (resolve, reject) {
        sendNextImageDataBatch(resolve, reject);
    });
}

function sendTextData(product) {
    // Get the bytes for the text
    let encoder = new TextEncoder("utf-8");
    // Add line feed + carriage return chars to text
    let text = ''
    + '\x1B' + '\x61' + '\x31'                                              
    + '\x1D' + '\x21' + '\x00' + 'SURAT JALAN PT. TRIPPER NATURE\n'
    + eventName + '/' + orderName + '\n'
    + 'PRODUK\n'+product.name+'\n'
    + 'CERTIFIED ORGANIC BY CONTROL UNION\n\n'
    + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    + 'Nama Sopir\t: '+orderDriver
    + '\nJenis Kendaraan & No. Polisi: \n'+orderVehicle 
    + '\nAlamat Asal\t: '+orderOrigin
    + '\nDikirim Ke\t: '+orderDestination
    + '\nTgl Kirim\t: '+ orderDate
    + '\nTgl Sampai\t: '+ receivedDate
    + '\n'
    + '\nNomor CU\t: '
    + '\nNomor PO\t: '+ poName
    + '\nNomor LOT\t: '
    + '\nKode Petani\t: '+ poPartner
    + '\nJumlah Box\t: '+ product.amount
    + '\nBerat Barang: '+ product.qty
    + '\n--------------------------------\n'

    // + '\x1B' + '\x61' + '\x31'                                              
    // + '\x1D' + '\x21' + '\x00' + 'KRITERIA PENGIRIMAN\n'
    // + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    // + 'Dicek oleh pengirim :'
    // + '\nProduk sesuai standar Tripper( )'
    // + '\nLabel lengkap dan tertempel  ( )\npada kemasan'
    // + '\nProduk dibungkus kemasan yang( )\ndisetujui, bersih dan bebas\ndari benda asing'
    // + '\nTruk bersih dan bebas dari   ( )\nsegala resiko kontaminasi'
    // + '\nHanya material tersertifikasi( )\n/NFC yang di dalam truk/kontainer'
    // + '\n\n'
    // + 'Dicek oleh penerima:'
    // + '\nProduk sesuai standar Tripper( )'
    // + '\nLabel lengkap dan tertempel  ( )\npada kemasan'
    // + '\nProduk dibungkus kemasan yang( )\ndisetujui, bersih dan bebas\ndari benda asing'
    // + '\nTruk bersih dan bebas dari   ( )\nsegala resiko kontaminasi'
    // + '\nHanya material tersertifikasi( )\n/NFC yang di dalam truk/kontainer'
    // + '\n\n\n'
    ;    
    return printCharacteristic.writeValue(new TextEncoder("utf-8").encode(text))
}

  function sendTextKriteria1() {
    // Get the bytes for the text
    let encoder = new TextEncoder("utf-8");
    // Add line feed + carriage return chars to text
    let text = ''
    // + '\x1B' + '\x61' + '\x31'                                              
    // + '\x1D' + '\x21' + '\x00' + 'SURAT JALAN PT. TRIPPER NATURE\n'
    // + 'PRODUK\n'+product.name+'\n'
    // + 'CERTIFIED ORGANIC BY CONTROL UNION\n\n'
    // + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    // + 'Nama Sopir\t: '+orderDriver
    // + '\nNomor Polisi: '+orderVehicle 
    // + '\nAlamat Asal\t: '
    // + '\nDikirim Ke\t: '+orderDestination
    // + '\nTgl Kirim\t: '+ orderDate
    // + '\n'
    // + '\nNomor CU\t: '
    // + '\nNomor PO\t: '+ poName
    // + '\nNomor LOT\t: '
    // + '\nKode Petani\t: '+ poPartner
    // + '\nJumlah Box\t: '+ product.amount
    // + '\nBerat Barang: '+ product.qty
    // + '\n--------------------------------\n'
    + '\x1B' + '\x61' + '\x31'                                              
    + '\x1D' + '\x21' + '\x00' + 'KRITERIA PENGIRIMAN\n'
    + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    + 'Dicek oleh pengirim :'
    + '\n(  )Produk sesuai standar\n    Tripper'
    + '\n(  )Label lengkap dan tertempel\n    pada kemasan'
    + '\n(  )Produk dibungkus kemasan\n    yang disetujui, bersih dan\n    bebas dari benda asing'
    + '\n(  )Truk bersih dan bebas dari\n    segala resiko kontaminasi'
    + '\n(  )Hanya material\n    tersertifikasi/NFC yang di\n    dalam truk/kontainer'
    + '\n\n'
    // + 'Dicek oleh penerima:'
    // + '\nProduk sesuai standar Tripper( )'
    // + '\nLabel lengkap dan tertempel  ( )\npada kemasan'
    // + '\nProduk dibungkus kemasan yang( )\ndisetujui, bersih dan bebas\ndari benda asing'
    // + '\nTruk bersih dan bebas dari   ( )\nsegala resiko kontaminasi'
    // + '\nHanya material tersertifikasi( )\n/NFC yang di dalam truk/kontainer'
    // + '\n\n\n'
    ;    
    return printCharacteristic.writeValue(new TextEncoder("utf-8").encode(text))
}

function sendTextKriteria2() {
    // Get the bytes for the text
    let encoder = new TextEncoder("utf-8");
    // Add line feed + carriage return chars to text
    let text = ''
    // + '\x1B' + '\x61' + '\x31'                                              
    // + '\x1D' + '\x21' + '\x00' + 'SURAT JALAN PT. TRIPPER NATURE\n'
    // + 'PRODUK\n'+product.name+'\n'
    // + 'CERTIFIED ORGANIC BY CONTROL UNION\n\n'
    // + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    // + 'Nama Sopir\t: '+orderDriver
    // + '\nNomor Polisi: '+orderVehicle 
    // + '\nAlamat Asal\t: '
    // + '\nDikirim Ke\t: '+orderDestination
    // + '\nTgl Kirim\t: '+ orderDate
    // + '\n'
    // + '\nNomor CU\t: '
    // + '\nNomor PO\t: '+ poName
    // + '\nNomor LOT\t: '
    // + '\nKode Petani\t: '+ poPartner
    // + '\nJumlah Box\t: '+ product.amount
    // + '\nBerat Barang: '+ product.qty
    // + '\n--------------------------------\n'
    // + '\x1B' + '\x61' + '\x31'                                              
    // + '\x1D' + '\x21' + '\x00' + 'KRITERIA PENGIRIMAN\n'
    // + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    // + 'Dicek oleh pengirim :'
    // + '\nProduk sesuai standar Tripper( )'
    // + '\nLabel lengkap dan tertempel  ( )\npada kemasan'
    // + '\nProduk dibungkus kemasan yang( )\ndisetujui, bersih dan bebas\ndari benda asing'
    // + '\nTruk bersih dan bebas dari   ( )\nsegala resiko kontaminasi'
    // + '\nHanya material tersertifikasi( )\n/NFC yang di dalam truk/kontainer'
    // + '\n\n'
    + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    + 'Dicek oleh penerima:'
    + '\n(  )Produk sesuai standar\n    Tripper'
    + '\n(  )Label lengkap dan tertempel\n    pada kemasan'
    + '\n(  )Produk dibungkus kemasan\n    yang disetujui, bersih dan\n    bebas dari benda asing'
    + '\n(  )Truk bersih dan bebas dari\n    segala resiko kontaminasi'
    + '\n(  )Hanya material\n    tersertifikasi/NFC yang di\n    dalam truk/kontainer'
    + '\n\n'
    + '* beri tanda V jika sesuai'
    + '\n\n'
    + '--------------------------------'
    ;    
    return printCharacteristic.writeValue(new TextEncoder("utf-8").encode(text))
}

function sendTextTTD() {
    // Get the bytes for the text
    let encoder = new TextEncoder("utf-8");
    // Add line feed + carriage return chars to text
    let text = ''
    + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
    + 'Pengirim:'
    + '\n\n\n\n\n'
    + '(                              )'
    + '\n\n'
    + 'Tanggal Terima : \n'
    + 'Penerima:'
    + '\n\n\n\n\n'
    + '(                              )'
    + '\n\n'
    + '--------------------------------'
    ;    
    return printCharacteristic.writeValue(new TextEncoder("utf-8").encode(text))
}


async function sendPrinterData(product) {
    // Print an image followed by the text
    return sendImageData()
        .then(() => sendTextData(product))
        // .then(() => sendTextKriteria1())
        // .then(() => sendTextKriteria2())
        .catch(handleError);
}

function printDelivery (products) {
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
                processAllItems(products);
            })
            .catch(handleError);
    } else {
        processAllItems(products);
    }
};

function deliveryInfo(){
    let products = [] 

    const elements = document.querySelectorAll('.product-id');


    // Loop through each element and apply the desired functionality
    elements.forEach(element => {
        // For example, change the text content of each element
        let found = products.find(item => item.id === element.innerHTML);
        

        if (!found){
            let product_array = {};
            product_array.id = element.innerHTML;
            row = element.closest('tr');
            product_array.name = row.querySelector('.product-name').textContent.trim();
            product_array.amount = 1
            product_array.qty = parseFloat(row.querySelector('.order-qty').textContent);
            
            products.push(product_array);
        }else{
            let index = products.findIndex(item => item.id === element.innerHTML);
            let product_array = {};
            row = element.closest('tr');
            product_array.id = element.innerHTML;
            product_array.name = row.querySelector('.product-name').textContent.trim();
            product_array.amount = products[index].amount + 1
            product_array.qty = products[index].qty + parseFloat(row.querySelector('.order-qty').textContent);
            products[index] = product_array;
        }

    });

    products.forEach(product =>{
        console.log(product.name)
        console.log(orderDriver)
        console.log(orderVehicle)
        console.log(orderDestination)
        console.log(orderDate)
        console.log(poName)
        console.log(poPartner)
        console.log(product.amount)
        console.log(product.qty)
        
    })
    printDelivery(products)
    // processAllItems(products)
    
}

async function processItem(product) {
    return new Promise((resolve, reject) => {
        sendImageData()
        .then(() => sendTextData(product))

        .then(() => sendTextKriteria1())
        .then(() => sendTextKriteria2())
        .then(() => sendTextTTD())
        
        .then(()=>{resolve();})
        .catch(handleError);
    });
}

// Define an asynchronous function to process all items sequentially
async function processAllItems(products) {
    for (let product of products) {
        await processItem(product)
        console.log("finish--")
    }
    
    console.log('All items processed');
    window.location.href = '/delivery/confirm?do='+doId;

}

