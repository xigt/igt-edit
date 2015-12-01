function browseSuccess(r, stat, jqXHR) {
    $('#editor-panel').html(r);
    $('#all-elements').accordion();
    $('.igt-panel').each(function(index, elem) {
        $(elem).panel({
            title: 'Instance '+$(elem).attr('id'),
        });
        $(elem).hover(function(){$(this).find('.panel-header').css('background-color:blue')})
    });
    $('.button').button();
}

function browseError(r, stat, jqXHR) {
    $('#editor-panel').text("An error occurred.");
}

function browseToPage(val, page) {
    $('#editor-panel').text("Loading...");
    $.ajax({
        url: 'display/'+val+'?page='+page,
        success: browseSuccess,
        error: browseError,
        dataType: "text"
    })
}

function browseTo(rowIndex, rowData) {
    browseToPage(rowData['value'], 0);
}