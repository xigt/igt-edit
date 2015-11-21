function browseSuccess(r, stat, jqXHR) {
    $('#editor-panel').html(r);
    $('.igt-panel').each(function(index, elem) {
        $(elem).panel({
            title: 'Instance '+$(elem).attr('id')
        });
    });
    $('.button').button();
}

function browseError(r, stat, jqXHR) {
    $('#editor-panel').text("An error occurred.");
}

function browseToPage(val, page) {
    $.ajax({
        url: 'browse/'+val+'?page='+page,
        success: browseSuccess,
        error: browseError,
        dataType: "text"
    })
}

function browseTo(rowIndex, rowData) {
    browseToPage(rowData['value'], 0);
}