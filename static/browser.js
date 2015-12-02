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
    $.ajax({
        url: url,
        success: browseSuccess,
        error: browseError,
        dataType: "text"
    })
}

/* Normalization */
function normalizeIGT(corp_id, igt_id) {
    console.log('Normalizing '+igt_id);
    var lines = [];
    var data = {lines:lines,
                igt_id:igt_id,
                corp_id:corp_id};

    /* Iterate over all the clean items, and add them to the data */
    $('.cleanrow').each(function(i, el) {

        linedata = {}

        linedata['tag'] = $(el).find('.tag-input').val();

        li = $(el).find('.line-input');
        linedata['text'] = li.val();
        linedata['id'] = li.attr('id');

        /* Skip the line if it's disabled */
        if (!li.attr('disabled')) {
            lines.push(linedata);
        }

    });

    $.ajax({
        url: '/normalize/'+corp_id+'/'+igt_id,
        type: 'POST',
        dataType: 'text',
        contentType: 'text/plain',
        data: JSON.stringify(data),
        success: normalizeSuccess,
        error: normalizeError
    })
}

function normalizeSuccess(r, stat, jqXHR) {
    $('#normalized-tier').show();
    $('#normalized-contents').html(r);
}

function normalizeError() {
    $('#normalized-contents').text("An error occured while normalizing.");
}

/* Edit/Delete Scripts */
function deleteItem(itemId) {
    $(itemId).find('input').prop('disabled',true);
    $(itemId).css('background-color','pink');
}

function restoreItem(itemId) {
    $(itemId).find('input').prop('disabled',false);
    $(itemId).css('background-color', 'inherit');
}