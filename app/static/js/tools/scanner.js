
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

    function startScanQR(element_id){
      $('#scannerModal').modal('show');
      html5QrcodeScanner.render(
          function (decodedText) {
              document.getElementById(element_id).value = decodedText;
              
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

  function startScanDelivery(){
    let do_id = document.getElementById('qr-do').value
    console.log(do_id)
    $('#scannerModal').modal('show');
    html5QrcodeScanner.render(
        function (decodedText) {
            document.getElementById('barcode').value = decodedText;
            
            // Stop scanning after successfully decoding a QR code
            html5QrcodeScanner.clear().then(_ => {
                
                // the UI should be cleared here 
                $('.modal').modal('hide');
                let add_url = '/delivery/detail/add?do='+do_id+'&barcode='+decodedText
                window.location.href = add_url  
                
              })
              // .then(() => {
              //   let add_url = '/delivery/detail/add?do='+do_id+'&barcode='+decodedText
              //   window.location.href = add_url
              // })
              .catch(error => {
                // Could not stop scanning for reasons specified in `error`.
                // This conditions should ideally not happen.
              });
        }, 
        function (errorMessage) {
            
        }
    );
}

  function stopScanQR(){
      html5QrcodeScanner.clear().then(_ => {
                  
          // the UI should be cleared here   
          $('.modal').modal('hide');
        }).catch(error => {
          // Could not stop scanning for reasons specified in `error`.
          // This conditions should ideally not happen.
        });

  }

  function startScanTest(element_id){
    $('#scannerModal').modal('show');
    html5QrcodeScanner.render(
        function (decodedText) {
            document.getElementById(element_id).value = decodedText;

            // Stop scanning after successfully decoding a QR code
        },
        function (errorMessage) {

        }
    );
  }


    
    

