/* Populate the IGT pane */
function populateIGTs(index, data) {
    var fl = $('#fine-list')
    fl.text('Loading...')
    $.ajax({
        url:'/populate/'+data['value'],
        error: populateError,
        success: populateSuccess
    })
}

function populateSuccess(r, stat, jqXHR) {
    $('#fine-list').html(r);
    $('#igtlist').datalist({
        lines:true
    });
}

function populateError() {
    $('#fine-lists').text("An error occurred.");
}

/* display a single IGT instance */

function browseSuccess(r, stat, jqXHR) {
    $('#editor-panel').html(r);
}

function browseError(r, stat, jqXHR) {
    $('#editor-panel').text("An error occurred.");
}

function displayIGT(corp_id, igt_id) {
    $('#editor-panel').text("Loading...");
    url = 'display/'+corp_id+'/'+igt_id
    console.log(url);
    $.ajax({
        url: url,
        success: browseSuccess,
        error: browseError,
        dataType: "text"
    })
}

function browseTo(rowIndex, rowData) {
    browseToPage(rowData['value'], 1);
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