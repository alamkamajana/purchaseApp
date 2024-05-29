$(document).ready(function() {
    tab_info = document.getElementById('tab-info').innerHTML;

    // Hide all tab contents except the first one
    $('.tab-content').not(':first').hide();

    // Handle tab click event
    $('.tab-links a').click(function() {
        var tab_id = $(this).attr('href');

        // Remove the 'active' class from all tabs
        $('.tab-links a').removeClass('active');

        // Add the 'active' class to the clicked tab
        $(this).addClass('active');

        // Hide all tab contents
        $('.tab-content').hide();

        // Show the clicked tab content
        $(tab_id).show();
    });

    if(tab_info==2){
        tab = $('#manual-tab-btn');
        var tab_id = $('#manual');

        $('.tab-links a').removeClass('active');

        // Add the 'active' class to the clicked tab
        tab.addClass('active');

        // Hide all tab contents
        $('.tab-content').hide();

        // Show the clicked tab content
        $(tab_id).show();
        tab_info = document.getElementById('tab-info').innerHTML = 0;

    }

    var selectedStation = $('#farmer_station_form').val();
    $('#farmer_group_form').val(null).trigger('change');
    $('#farmer_group_form option').each(function() {
        var itemStation = $(this).data('category');
        if (selectedStation == 'all' || selectedStation == itemStation || $(this).val()==0) {
            $(this).show();
        } else {
            $(this).hide();
        }
        });
    $('#farmer_group_form').val('').trigger('change');

    
    $('#farmer_station_form').on('change', function() {
        var selectedStation = $(this).val();
        $('#farmer_group_form').val(null).trigger('change');
        $('#farmer_group_form option').each(function() {
        var itemStation = $(this).data('category');
        if (selectedStation == 'all' || selectedStation == itemStation || $(this).val()==0) {
            $(this).show();
        } else {
            $(this).hide();
        }
        });
        $('#farmer_group_form').val('').trigger('change');
            
    });
        
    
    
});
