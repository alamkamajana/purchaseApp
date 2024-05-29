
    var html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", { fps: 10, qrbox: 250 });
    
    
    function startScan(){
        $('#scannerModal').modal('show');
        html5QrcodeScanner.render(
            function (decodedText) {
                document.getElementById('farmer_code').value = decodedText;
                
                // Stop scanning after successfully decoding a QR code
                html5QrcodeScanner.clear().then(_ => {
                    
                    // the UI should be cleared here   
                    $('.modal').modal('hide');
                  }).catch(error => {
                    // Could not stop scanning for reasons specified in `error`.
                    // This conditions should ideally not happen.
                  });
            }, 
            function (errorMessage) {
                
            }
        );
    }

    function stopScan(){
        html5QrcodeScanner.clear().then(_ => {
                    
            // the UI should be cleared here   
            $('.modal').modal('hide');
          }).catch(error => {
            // Could not stop scanning for reasons specified in `error`.
            // This conditions should ideally not happen.
          });

    }


    
    

