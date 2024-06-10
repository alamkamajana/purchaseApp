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
            let is_organic = row.querySelector('.is-organic').textContent.trim();
            
            product_array.name = row.querySelector('.product-name').textContent.trim();
            product_array.amount = 1
            product_array.qty = parseFloat(row.querySelector('.order-qty').textContent);
            product_array.cu_number = row.querySelector('.cu-number').textContent.trim();
            if(is_organic=="True"){
                product_array.organic_message = "CERTIFIED ORGANIC BY CONTROL UNION"
            }else{
                product_array.organic_message = ""
            }
            console.log(product_array.organic_message)
            
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

    printDelivery(products)
    // processAllItems(products)
    
}

function printDelivery(products) {
    var SERVICE = '000018f0-0000-1000-8000-00805f9b34fb';
    var WRITE = '00002af1-0000-1000-8000-00805f9b34fb';
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

    function getTextData(product) {
        // Get the bytes for the text
        let encoder = new TextEncoder("utf-8");
        // Add line feed + carriage return chars to text
        let text = ''
            // + '\x1B' + '\x61' + '\x31'
            // + '\x1D' + '\x21' + '\x00' + 'TRIPPER\n'
            + '\x1B' + '\x61' + '\x31'
            + '\x1D' + '\x21' + '\x00' + 'SURAT JALAN PT. TRIPPER NATURE\n'
            + orderName + '\n'
            + 'PRODUK\n' + product.name + '\n'
            + product.organic_message + '\n\n'
            + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
            + 'Nama Sopir\t: ' + orderDriver
            + '\nJenis Kendaraan & No. Polisi: \n' + orderVehicle
            + '\nAlamat Asal\t: ' + orderOrigin
            + '\nDikirim Ke\t: ' + orderDestination
            + '\nTgl Kirim\t: ' + orderDate
            + '\nTgl Sampai\t: ' + receivedDate
            + '\n'
            + '\nNomor CU\t: ' + product.cu_number
            + '\nNomor PO\t: ' + poName
            + '\nKode Petani\t: ' + poPartner
            + '\nJumlah Box\t: ' + product.amount
            + '\nBerat Barang: ' + product.qty
            + '\n--------------------------------\n'
            ;
        return text
    }

    function getTextKriteria1() {
        // Get the bytes for the text
        let encoder = new TextEncoder("utf-8");
        // Add line feed + carriage return chars to text
        let text = ''
            + '\x1B' + '\x61' + '\x31'
            + '\x1D' + '\x21' + '\x00' + 'KRITERIA PENGIRIMAN\n'
            + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
            + 'Dicek oleh pengirim :'
            + '\n(  )Produk sesuai standar\n    Tripper'
            + '\n(  )Label lengkap dan tertempel\n    pada kemasan'
            + '\n(  )Produk dibungkus kemasan\n    yang disetujui, bersih dan\n    bebas dari benda asing'
            + '\n(  )Truk bersih dan bebas dari\n    segala resiko kontaminasi'
            + '\n(  )Hanya material\n    tersertifikasi/NFC yang di\n    dalam truk/kontainer'
            + '\n\n'
            ;
        return text
    }

    function getTextKriteria2() {
        // Get the bytes for the text
        let encoder = new TextEncoder("utf-8");
        // Add line feed + carriage return chars to text
        let text = ''
            + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
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
        return text
    }

    function getTextTTD() {
        // Get the bytes for the text
        let encoder = new TextEncoder("utf-8");
        // Add line feed + carriage return chars to text
        let text = ''
            + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
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
        return text
    }

    function splitDataIntoChunks(data, chunkSize) {
        let chunks = [];
        for (let i = 0; i < data.length; i += chunkSize) {
            chunks.push(data.slice(i, i + chunkSize));
        }
        return chunks;
    }

    let printCharacteristic;
            let index = 0;
            let data;
            let test;

            let image = document.querySelector('#tripper-logo-black');
            // Use the canvas to get image data
            let canvas = document.createElement('canvas');
            // Canvas dimensions need to be a multiple of 40 for this printer
            canvas.width = 360;
            canvas.height = 60;
            imageWidth = canvas.width / 2;
            imageHeight = imageWidth / 966 * 277;
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
                if (index + 128 < test.length) {
                    console.log(data.length)
                    console.log(test.length)
                    printCharacteristic.writeValue(test.slice(index, index + 128)).then(() => {
                        index += 128;
                        sendNextImageDataBatch(resolve, reject);
                    })
                        .catch(error => reject(error));
                } else {
                    // Send the last bytes
                    console.log(test.length)
                    if (index < test.length) {
                        printCharacteristic.writeValue(test.slice(index, test.length)).then(() => {
                            resolve();
                        })
                            .catch(error => reject(error));
                    } else {
                        resolve();
                    }
                }
            }

            function sendImageData() {
                data = getImagePrintData();
                test = data;
                index = 0;
                return new Promise(function (resolve, reject) {
                    sendNextImageDataBatch(resolve, reject);
                });
            }

            function processItem() {
                return new Promise((resolve, reject) => {
                    sendImageData()
                        .then(() => {
                            resolve();
                        })
                        .catch(handleError);
                });
            }

            function printDelivery() {
                if (printCharacteristic == null) {
                    // Cache the characteristic
                    printCharacteristic = characteristic;
                    processItem()

                } else {
                    processItem()
                }
            };

    allData = ''
    
    // products.forEach(product => {
    //     allData += getTextData(product)
    //     allData += getTextKriteria1()
    //     allData += getTextKriteria2()
    //     allData += getTextTTD()
    // });
    navigator.bluetooth.requestDevice({ filters: [{ services: [SERVICE] }] }).then(device => {
        return device.gatt.connect();
    }).then(server => {
        return server.getPrimaryService(SERVICE);
    }).then(service => {
        return service.getCharacteristic(WRITE);
    }).then(characteristic => {
        let chunks
        function sendNextProducts(){
            return new Promise((resolve, reject) => {
                function processProduct() {
                    if (products.length > 0) {
                        let product = products.shift();
                        allData = ''
                        allData += getTextData(product)
                        allData += getTextKriteria1()
                        allData += getTextKriteria2()
                        allData += getTextTTD()
                        chunks = splitDataIntoChunks(allData, 128);
                        console.log(chunks)
                        console.log(allData)
                        // processProduct()
                        printDelivery()
                        .then(() => {
                        sendNextChunk().then(() => {
                            processProduct(); // Send the next chunk
                        })
                        })
                        
                        .catch(error => {
                            reject(error);
                        });
                    } else {
                        resolve();
                    }
                }

                processProduct(); // Start processing chunks
            });
        }
        
        function printDelivery() {
            return new Promise((resolve, reject) => {
                console.log("data")
                // if (printCharacteristic == null) {
                    // Cache the characteristic
                    printCharacteristic = characteristic;
                    processItem().then(()=> resolve())

                // } else {
                    // processItem().then(()=> resolve())
                // }
        });
        };
        // Split the data into chunks
        // let chunks = splitDataIntoChunks(allData, 128);

        // Function to send a chunk and then send the next chunk
        function sendNextChunk() {
            return new Promise((resolve, reject) => {
                function processChunk() {
                    if (chunks.length > 0) {
                        let chunk = chunks.shift();
                        characteristic.writeValue(new TextEncoder("utf-8").encode(chunk)).then(() => {
                            processChunk(); // Send the next chunk
                        }).catch(error => {
                            reject(error);
                        });
                    } else {
                        resolve();
                    }
                }

                processChunk(); // Start processing chunks
            });
        }

        // Start sending chunks and then write the additional data
        // return printDelivery().then(() => {sendNextChunk();});
        return sendNextProducts()
    }).catch(error => {
        console.error('Error connecting to device:', error);
    });

}


