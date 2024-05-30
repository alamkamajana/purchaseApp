$(document).ready(function() {
    
    $('#station_id').on('change', function() {
        var selectedStation = $(this).val();
        $('#parent_id').val(null).trigger('change');
        $('#parent_id option').each(function() {
        var itemStation = $(this).data('category');
        if (selectedStation == 'all' || selectedStation == itemStation) {
            $(this).show();
        } else {
            $(this).hide();
        }
        });
        $('#parent_id').val('').trigger('change');
        // $('#farmer-station').select2();
    });
    // $('#farmer-group').select2({
    // });

    // $('#farmer-station').select2({
    // });
});