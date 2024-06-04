
function btPrintTest() {
    var SERVICE = '000018f0-0000-1000-8000-00805f9b34fb';
    var WRITE = '00002af1-0000-1000-8000-00805f9b34fb';

    
    var DATA = ''
        + '\x1B' + '\x61' + '\x31'
        + '\x1D' + '\x21' + '\x00' + 'Success\nSuccess\n\nSuccess'
        + '\n\n\n\n';

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