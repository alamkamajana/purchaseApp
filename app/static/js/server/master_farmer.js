$(document).ready(function() {

    var selectedStation = $('#station_id').val();
    var index=0;
    var first_option=0;
    // $('#farmer_group_form').val(null).trigger('change');
    $('#parent_id option').each(function() {
        var itemStation = $(this).data('category');
        if (selectedStation == 'all' || selectedStation == itemStation) {
            if(index==0){
                first_option=$(this).val()
            }
            $(this).show();
            index++
        } else {
            $(this).hide();
        }
    });
    // $('#parent_id').val(first_option).trigger('change');
    
    $('#station_id').on('change', function() {
        var selectedStation = $(this).val();
        $('#parent_id').val(null).trigger('change');
        var index=0;
        var first_option=0;
        $('#parent_id option').each(function() {
            var itemStation = $(this).data('category');
            if (selectedStation == 'all' || selectedStation == itemStation) {
                if(index==0){
                    first_option=$(this).val()
                }
                $(this).show();
                index++
            } else {
                $(this).hide();
            }
            
        });
        $('#parent_id').val(first_option).trigger('change');
        // $('#farmer-station').select2();
    });
    // $('#farmer-group').select2({
    // });

    // $('#farmer-station').select2({
    // });
});