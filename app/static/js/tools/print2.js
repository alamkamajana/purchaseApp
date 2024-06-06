let printCharacteristic;
let index = 0;
let data;
let image = document.querySelector('#sig-image');
let canvas = document.createElement('canvas');
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

function sendNextImageDataBatch(resolve, reject) {
    if (index + 512 < data.length) {
        printCharacteristic.writeValue(data.slice(index, index + 512)).then(() => {
            index += 512;
            sendNextImageDataBatch(resolve, reject);
        })
            .catch(error => reject(error));
    } else {
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