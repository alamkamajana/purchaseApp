$(document).ready(function() {

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
    
    
});
