function browseSuccess(r, stat, jqXHR) {
    $('#editor-panel').text(r);
}

function browseError(r, stat, jqXHR) {
    $('#editor-panel').text("An error occurred.");
}

function browseTo(rowIndex, rowData) {
    $.ajax({
        url: '/browse/'+rowData['value'],
        success: browseSuccess,
        error: browseError,
        dataType: "text"
    });
}