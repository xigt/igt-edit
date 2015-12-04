/* Constant Strings */
var AJAX_LOADER_BIG = '<IMG src="static/images/ajax-loader.gif"/>'
var AJAX_LOADER_SMALL = '<IMG src="static/images/ajax-loader-small.gif"/>'

/* Populate the IGT pane */
function populateIGTs(index, data) {
    $('#fine-list').html('<div style="text-align:center;top:40px;position:relative;">'+AJAX_LOADER_SMALL+'</div>');
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
    $('#editor-panel').html(AJAX_LOADER_BIG);
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
    // Assign the tooltips to the interface elements.
    assign_tooltips();

    // Stash the current versions of the clean lines for undo-ing.
    stashCleanLines();
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
    return get_tier_lines('.normalrow');
}

/* Normalization */
function normalizeIGT(corp_id, igt_id) {
    console.log('Normalizing '+igt_id);
    $('#normalized-contents').html('Loading...');

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
    assign_tooltips();
    stashNormLines();
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
            normal: normalData};

    analyzeUnmark('glm');
    analyzeUnmark('glw');
    analyzeUnmark('tag');
    analyzeUnmark('col');

    $.ajax({
        url: '/intentify/'+corp_id+'/'+igt_id,
        contentType: 'text/plain',
        dataType: 'json',
        type: 'POST',
        data: JSON.stringify(data),
        success: intentifySuccess,
        error: intentifyError
    });
}

function analyzeUnmark(id) {
    $('#'+id).removeClass('feedback-warn');
    $('#'+id).removeClass('feedback-ok');
}

function analyzeWarn(id) {
    $('#'+id).addClass('feedback-warn');
}

function analyzeOK(id) {
    $('#'+id).addClass('feedback-ok');
}

function analysisNotifier(r, id) {
    if (r[id] == 0) {
        analyzeWarn(id);
    } else {
        analyzeOK(id);
    }
}

function intentifySuccess(r, stat, jqXHR) {
    analysisNotifier(r, 'glw');
    analysisNotifier(r, 'glm');
    analysisNotifier(r, 'tag');
    analysisNotifier(r, 'col');
}

function intentifyError() {
    $('#remaining-content').text("An error occurred producing the remaining tiers.")
}

/* Edit/Delete Scripts */
function deleteItem(elt, itemId) {

    var identifier = '#'+itemId;

    /* If this button has been clicked already,
     * restore (as a toggle) */
    if ($(elt).hasClass('iconclicked')) {
        $(elt).removeClass('iconclicked');

        // Unmark the item for deletion.
        $(identifier).find('input').prop('disabled',false);
        $(identifier).removeClass('for-deletion');

    } else {

    /* Otherwise, set it clicked, and delete it. */
        $(elt).addClass('iconclicked');

        // If neither of the boxes are filled out, delete the
        // element.
        if ($(identifier).find('.tag-input').val().trim() == '' &&
            $(identifier).find('.line-input').val().trim() == '') {
            $(identifier).remove();

        // Otherwise, simply mark it for deletion.
        } else {
            $(identifier).find('input').prop('disabled', true);
            $(identifier).addClass('for-deletion');
        }
    }
}

function restoreItem(itemId) {
    var identifier = '#'+itemId;

    /* Set the item to its initial value. */
    $(identifier).find('.line-input').val(localStorage.getItem(itemId));
}

function addItem(prefix, jqAfter, rowtype) {
    numitems = $('.cleantable tr').length;

    id = prefix+(numitems+1).toString();

    jqAfter.after('<TR class="textrow '+rowtype+'" id="'+id+'">\
        <TD class="short-col">\
            <img class="hovericon undo" src="static/images/undo.png" onclick="restoreItem(\''+id+'\')"/>\
            <img class="hovericon delete" src="static/images/delete.png" onclick="deleteItem(this, \''+id+'\')"/>\
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

/* Save the edited tier! */
function saveTier() {
    $('#save-msg').text('Unimplemented.');
}