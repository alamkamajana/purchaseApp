function deliveryInfo() {
    let products = []

    const elements = document.querySelectorAll('.product-id');
    // const barcodes = document.querySelectorAll('.product_barcode');
    // console.log(barcodes)
    // const barcodeValues = Array.from(barcodes).map(barcode => barcode.value);
    // console.log(barcodeValues);
    // const uniqueBarcodes = new Set(barcodeValues);
    //
    // const uniqueBarcodeArray = Array.from(uniqueBarcodes);
    // console.log(uniqueBarcodeArray)
    //
    // const length_producct = uniqueBarcodeArray.length
    // console.log(length_producct)

    // Loop through each element and apply the desired functionality
    elements.forEach(element => {
        // For example, change the text content of each element
        let found = products.find(item => item.id === element.innerHTML);


        if (!found) {

            let product_array = {};

            product_array.id = element.innerHTML;
            row = element.closest('tr');
            let is_organic = row.querySelector('.is-organic').textContent.trim();

            product_array.name = row.querySelector('.product-name').textContent.trim();
            product_array.amount = 1
            product_array.qty = parseFloat(row.querySelector('.order-qty').textContent);
            product_array.cu_number = row.querySelector('.cu-number').textContent.trim();
            if (is_organic == "True") {
                product_array.organic_message = "CERTIFIED ORGANIC BY CONTROL UNION"
            } else {
                product_array.organic_message = ""
            }
            console.log(product_array.organic_message)

            products.push(product_array);
        } else {
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
    let note = document.getElementsByClassName('note')[0].innerHTML.trim()
    let tempDiv = document.createElement('div');
    tempDiv.innerHTML = note;

    // Extract text content (this will remove the <p> tags)
    let textContent = tempDiv.textContent || tempDiv.innerText || '';

    // Set the text content back to the first element
    note = textContent.trim();
    note = note.slice(0, 50)+'...'; 
    console.log(note)

    const barcodes = document.querySelectorAll('.product_barcode');
    console.log(barcodes)
    const barcodeValues = Array.from(barcodes).map(barcode => barcode.value);
    console.log(barcodeValues);
    const uniqueBarcodes = new Set(barcodeValues);

    const uniqueBarcodeArray = Array.from(uniqueBarcodes);
    console.log(uniqueBarcodeArray)

    const length_producct = uniqueBarcodeArray.length
    console.log(length_producct)

    function getTextHeader() {
        // Get the bytes for the text
        let encoder = new TextEncoder("utf-8");
        // Add line feed + carriage return chars to text
        let text = ''
            // + '\x1B' + '\x61' + '\x31'
            // + '            TRIPPER\n'
            + '\x1B' + '\x61' + '\x31'
            + '\x1D' + '\x21' + '\x00'
            +'SURAT JALAN PT. TRIPPER NATURE\n'
            + orderName + '\n'
            + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
            + '\nTgl Kirim\t: ' + orderDate
            + '\nTgl Sampai\t: ' + receivedDate
            + '\nAlamat Asal\t: ' + orderOrigin
            + '\nDikirim Ke\t: ' + orderDestination
            + '\nNama Sopir\t: ' + orderDriver
            + '\nJenis Kendaraan & \nNo. Polisi\t: ' + orderVehicle
            + '\nNomor PO\t: ' + poName
            + '\nKode Petani\t: ' + poPartner
            + '\nNote\t: ' + '\n'+ note
            + '\n--------------------------------\n'
        ;
        return text
    }

    function getTextData(product) {
        // Get the bytes for the text
        let encoder = new TextEncoder("utf-8");
        // Add line feed + carriage return chars to text
        let text = ''
            + '\x1D' + '\x21' + '\x00' + '\x1B' + '\x61' + '\x00'
            + 'Produk  : ' + product.name
            // + product.organic_message + '\n\n'
            // + '\nNomor CU\t: ' + product.cu_number
            + '\nJumlah Karung : ' + product.amount
            + '\nBerat Barang  : ' + product.qty.toFixed(2) + ' Kg'
            + '\nBerat Diterima:          Kg'
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
            // + '\n\n'
            + '\n--------------------------------'
            // + '\n'
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
    let printCharacteristic2;
    let index = 0;
    let data;
    let test;
    let data2;
    let test2;
    let image = document.querySelector('#tripper-logo-black');
    // Use the canvas to get image data
    let canvas = document.createElement('canvas');
    // Canvas dimensions need to be a multiple of 40 for this printer
    canvas.width = 360;
    canvas.height = 90;
    let imageWidth = canvas.width / 2;
    
    let imageHeight = imageWidth / 966 * 277;
    let context = canvas.getContext("2d");
    let offsetX = (canvas.width - imageWidth) / 2 + 1;
    context.drawImage(image, offsetX, 0, imageWidth, imageHeight);
    let imageData = context.getImageData(0, 0, canvas.width, canvas.height).data;

    let image2 = document.querySelector('#sig-qr');
    // Use the canvas to get image data
    let canvas2 = document.createElement('canvas');
    // Canvas dimensions need to be a multiple of 40 for this printer
    canvas2.width = 360;
    canvas2.height = 200;
    let imageWidth2 = canvas2.width / 2;
    let imageHeight2 = imageWidth2 / 966 * 950;
    let context2 = canvas2.getContext("2d");
    let offsetX2 = (canvas2.width - imageWidth2) / 2 + 1;
    context2.drawImage(image2, offsetX2, 0, imageWidth2, imageHeight2);
    let imageData2 = context2.getImageData(0, 0, canvas2.width, canvas2.height).data;

    function getDarkPixel(x, y) {
        // Return the pixels that will be printed black
        let red = imageData[((canvas.width * y) + x) * 4];
        let green = imageData[((canvas.width * y) + x) * 4 + 1];
        let blue = imageData[((canvas.width * y) + x) * 4 + 2];
        return (red + green + blue) > 0 ? 1 : 0;
    }

    function getDarkPixel2(x, y) {
        // Return the pixels that will be printed black
        let red = imageData2[((canvas2.width * y) + x) * 4];
        let green = imageData2[((canvas2.width * y) + x) * 4 + 1];
        let blue = imageData2[((canvas2.width * y) + x) * 4 + 2];
        return (red + green + blue) > 0 ? 0 : 1;
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

    function getImagePrintData2() {
        if (imageData2 == null) {
            console.log('No image to print!');
            return new Uint8Array([]);
        }
        // Each 8 pixels in a row is represented by a byte
        let printData2 = new Uint8Array(canvas2.width / 8 * canvas2.height + 8);
        let offset = 0;
        // Set the header bytes for printing the image
        printData2[0] = 29;  // Print raster bitmap
        printData2[1] = 118; // Print raster bitmap
        printData2[2] = 48; // Print raster bitmap
        printData2[3] = 0;  // Normal 203.2 DPI
        printData2[4] = canvas2.width / 8; // Number of horizontal data bits (LSB)
        printData2[5] = 0; // Number of horizontal data bits (MSB)
        printData2[6] = canvas2.height % 256; // Number of vertical data bits (LSB)
        printData2[7] = canvas2.height / 256;  // Number of vertical data bits (MSB)
        offset = 7;
        // Loop through image rows in bytes
        for (let i = 0; i < canvas2.height; ++i) {
            for (let k = 0; k < canvas2.width / 8; ++k) {
                let k8 = k * 8;
                //  Pixel to bit position mapping
                printData2[++offset] = getDarkPixel2(k8 + 0, i) * 128 + getDarkPixel2(k8 + 1, i) * 64 +
                    getDarkPixel2(k8 + 2, i) * 32 + getDarkPixel2(k8 + 3, i) * 16 +
                    getDarkPixel2(k8 + 4, i) * 8 + getDarkPixel2(k8 + 5, i) * 4 +
                    getDarkPixel2(k8 + 6, i) * 2 + getDarkPixel2(k8 + 7, i);
            }
        }
        return printData2;
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

    function sendNextImageDataBatch2(resolve, reject) {

        // Can only write 512 bytes at a time to the characteristic
        // Need to send the image data in 512 byte batches
        if (index + 128 < test2.length) {
            printCharacteristic2.writeValue(test2.slice(index, index + 128)).then(() => {
                index += 128;
                sendNextImageDataBatch2(resolve, reject);
            })
                .catch(error => reject(error));
        } else {
            // Send the last bytes
            console.log(test2.length)
            if (index < test2.length) {
                printCharacteristic2.writeValue(test2.slice(index, test2.length)).then(() => {
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

    function sendImageData2() {
        data2 = getImagePrintData2();
        test2 = data2;
        index = 0;
        return new Promise(function (resolve, reject) {
            sendNextImageDataBatch2(resolve, reject);
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

    function processItem2() {
        return new Promise((resolve, reject) => {
            sendImageData2()
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
    navigator.bluetooth.requestDevice({filters: [{services: [SERVICE]}]}).then(device => {
        return device.gatt.connect();
    }).then(server => {
        return server.getPrimaryService(SERVICE);
    }).then(service => {
        return service.getCharacteristic(WRITE);
    }).then(characteristic => {
        let chunks
        allData = ''
        allData += getTextHeader()
        products.forEach(product => {
            allData += getTextData(product)
        });
        // let product = products.shift();
        // allData += getTextData(product)
        allData += getTextKriteria1()
        allData += getTextKriteria2()
        allData += getTextTTD()
        chunks = splitDataIntoChunks(allData, 128);

        function sendNextProducts() {
            return new Promise((resolve, reject) => {
                function processProduct() {
                    if (products.length > 0) {
                        let product = products.shift();
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
                                sendNextChunk()
                                    .then(() => {
                                        processProduct(); // Send the next chunk
                                    })
                            }).then(() => {
                            processItem(); // Call processItem() after processProduct() completes
                        })

                            .catch(error => {
                                reject(error);
                            });
                    } else {
                        resolve();
                        window.location.href = '/delivery/confirm?do=' + doId;
                    }
                }

                processProduct().then(() => {
                    processItem(); // Call processItem() after processProduct() completes
                })
            });
        }

        function printDelivery() {
            return new Promise((resolve, reject) => {
                console.log("data");
                // if (printCharacteristic == null) {
                // Cache the characteristic
                printCharacteristic = characteristic;
                processItem()
                    .then(() => {
                        // window.location.href = '/delivery/confirm?do=' + doId;
                        resolve();  // Resolve the promise when both processItem() and processItem2() are complete
                    })
                    .catch((error) => {
                        reject(error);  // Reject the promise if any error occurs
                    });

                // } else {
                // processItem().then(()=> resolve())
                // }
            });
        };

        function printDelivery2() {
            return new Promise((resolve, reject) => {
                console.log("data");
                // if (printCharacteristic == null) {
                // Cache the characteristic
                printCharacteristic2 = characteristic;
                processItem2()
                    .then(() => {
                        window.location.href = '/delivery/confirm?do=' + doId;
                        resolve();  // Resolve the promise when both processItem() and processItem2() are complete
                    })
                    .catch((error) => {
                        reject(error);  // Reject the promise if any error occurs
                    });

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
        
        return printDelivery().then(()=>{sendNextChunk().then(() => {printDelivery2();})});
        // return printDelivery2()
        // return sendNextProducts()
    }).catch(error => {
        console.error('Error connecting to device:', error);
    });

}


