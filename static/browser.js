function browseSuccess(r, stat, jqXHR) {
    $('#editor-panel').html(r);
    $('#all-elements').accordion();
    $('.igt-panel').each(function(index, elem) {
        $(elem).panel({
            title: 'Instance '+$(elem).attr('id'),
        });
    });

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

/* Edit/Delete Scripts */
function deleteItem(itemId) {
    $(itemId).find('input').prop('disabled',true);
    $(itemId).css('background-color','pink');
    //$(itemId+' textinput').css('opacity', '0.3');
}

function restoreItem(itemId) {
    $(itemId).find('input').prop('disabled',false);
    $(itemId).css('background-color', 'inherit');

}