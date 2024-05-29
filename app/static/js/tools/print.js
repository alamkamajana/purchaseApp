function btPrint(){
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
    console.log(code_petani)
    var nama_petani = document.getElementById("farmer_name").value;
    console.log(nama_petani)




    var DATA = ''
        + '\x1B' + '\x61' + '\x31'                                              
        + '\x1D' + '\x21' + '\x00' + 'TRIPPER\nWE ADD VALUE AT ORIGIN\n\n'                    
        + '\x1D' + '\x21' + '\x00' + '\x1B' +'\x61' + '\x00' 
        + 'Tanggal\t: '+ formattedDate 
        + '\nID Petani\t: ' + code_petani
        + '\nNama\t: ' + nama_petani  
        + '\n\n';                                                     

    var deviceHandle;
    navigator.bluetooth.requestDevice({ filters: [{ services: [SERVICE]}] }).then(device => {
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