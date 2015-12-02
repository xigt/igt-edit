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
function displayIGT(corp_id, igt_id) {
    $('#editor-panel').text("Loading...");
    url = 'display/'+corp_id+'/'+igt_id
    $.ajax({
        url: url,
        success: displaySuccess,
        error: displayError,
        dataType: "text"
    });
}

function displaySuccess(r, stat, jqXHR) {
    $('#editor-panel').html(r);
}

function displayError(r, stat, jqXHR) {
    $('#editor-panel').text("An error occurred.");
}

function get_raw_lines() {
    lines = [];
    $('.raw-tier .textrow').each(function(i, el){
        linedata = {};
        linedata['tag'] = $(el).find('.tags').text();
        linedata['text'] = $(el).find('.text').text();
        lines.push(linedata);
    });
    return lines;
}

/* Retrieve Clean Tiers */
function get_tier_lines(rowSelector) {

    var lines = [];

    /* Iterate over all the clean items, and add them to the data */
    $(rowSelector).each(function(i, el) {

        linedata = {};

        linedata['tag'] = $(el).find('.tag-input').val();

        li = $(el).find('.line-input');
        linedata['text'] = li.val();
        linedata['id'] = li.attr('id');
        linedata['num'] = i+1;

        /* Skip the line if it's disabled */
        if (!li.attr('disabled')) {
            lines.push(linedata);
        }

    });

    return lines;
}

function get_clean_lines() {
    return get_tier_lines('.cleanrow');
}

function get_normal_lines() {
    return get_tier_lines('normalrow');
}

/* Normalization */
function normalizeIGT(corp_id, igt_id) {
    console.log('Normalizing '+igt_id);
    $('#normalized-contents').text('Loading...');

    cleanData = get_clean_lines();

    $.ajax({
        url: '/normalize/'+corp_id+'/'+igt_id,
        type: 'POST',
        dataType: 'text',
        contentType: 'text/plain',
        data: JSON.stringify(cleanData),
        success: normalizeSuccess,
        error: normalizeError
    });
}

function normalizeSuccess(r, stat, jqXHR) {
    $('#normalized-tier').show();
    $('#normalized-contents').html(r);
}

function normalizeError() {
    $('#normalized-contents').text("An error occured while normalizing.");
}

/* INTENT-ification */
function generateFromNormalized(corp_id, igt_id) {
    normalData = get_normal_lines();
    cleanData  = get_clean_lines();
    rawData    = get_raw_lines();

    data = {raw: rawData,
            clean: cleanData,
            normal: normalData}

    $.ajax({
        url: '/intentify/'+corp_id+'/'+igt_id,
        contentType: 'text/plain',
        type: 'POST',
        data: JSON.stringify(data),
        success: intentifySuccess,
        error: intentifyError
    });
}

function intentifySuccess(r, stat, jqXHR) {
    console.log(r);
}

function intentifyError() {
    $('#remaining-content').text("An error occurred producing the remaining tiers.")
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

function addItem(jqAfter) {
    numitems = $('.cleantable tr').length;

    id = 'c-'+(numitems+1).toString();

    jqAfter.after('<TR class="textrow cleanrow" id="'+id+'">\
        <TD class="short-col">\
            <img class="hovericon undo" src="static/images/undo.png" onclick="restoreItem(\'#'+id+'\')"/>\
            <img class="hovericon delete" src="static/images/delete.png" onclick="deleteItem(\'#'+id+'\')"/>\
            <img class="hovericon add" src="static/images/add.png" onclick="addItem($(this).closest(\'tr\'))" />\
        </TD>\
        <TD class="short-col">\
            <input class="tag-input" type="text" value=""/>\
        </TD>\
        <TD class="textinput">\
            <input class="line-input" type="text" value=""/>\
        </TD>\
        </TR>');
}