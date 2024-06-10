
function btPrintTest() {
    var SERVICE = '000018f0-0000-1000-8000-00805f9b34fb';
    var WRITE = '00002af1-0000-1000-8000-00805f9b34fb';

    
    var barcodeData = generateBarcodeData('123456789'); // Replace '123456789' with your barcode data

    // Construct the data to send to the printer
    var DATA = ''
        + '\x1D' + '\x68' + '\x50'  // Set barcode height (in dots)
        + '\x1D' + '\x77' + '\x02'  // Set barcode width (in dots)
        + '\x1D' + '\x6B' + '\x02' + '\x0B' + barcodeData;  // Print barcode

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
        console.log(new TextEncoder("utf-8").encode(DATA))
        return channel.writeValue(new TextEncoder("utf-8").encode(DATA));
    }).catch(error => {
        console.error(error)
    }).finally(() => {
        deviceHandle.gatt.disconnect();
    });
}

function generateBarcodeData(data) {
    // Format barcode data as per printer command format (e.g., Code 128)
    // This is a simplified example, you might need to adjust it based on your printer's requirements
    var barcodeCommand = '\x7B' + '\x42' + '\x04' + '\x07' + '\x07' + data;  // Example: Code 128 encoding
    return barcodeCommand;
}