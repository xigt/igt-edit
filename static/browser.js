/* Constant Strings */
var AJAX_LOADER_BIG = '<IMG src="/static/images/ajax-loader.gif"/>';
var AJAX_LOADER_SMALL = '<IMG src="/static/images/ajax-loader-small.gif"/>';

/* QUALITY CONSTANTS */
const HIDDEN = 4;
const BAD_QUALITY = 3;
const OK_QUALITY = 2;
const GOOD_QUALITY = 1;

/* CONSTANTS FOR BUTTON TITLES */
const CLEAN_GEN   = "Generate Cleaned Tier";
const CLEAN_REGEN = "Regenerate Cleaned Tier";

const NORM_GEN    = "Generate Normalized Tier";
const NORM_REGEN  = "Regenerate Normalized Tier";

/* CLASS CONSTANTS */
const RATING_DISABLED = "rating-disabled";
const RATING_ENABLED  = "rating-enabled";

const FEEDBACK_WARN   = "feedback-warn";
const FEEDBACK_OK     = "feedback-ok";

const ICON_CLICKED    = "iconclicked";

const CURRENT_ROW     = "current-row";
// -------------------------------------------

/* Login the User */
function login() {
    var userid = $('#userid').val();
    console.log(userid);
    window.location.href = '/user/'+userid;
}

/* Populate the IGT pane */
function populateIGTs(corpId, async) {

    if (typeof async === 'undefined') {async = false;}

    data = {userID : userID()};
    console.log(data);

    $('#fine-list').html('<div style="text-align:center;top:40px;position:relative;">'+AJAX_LOADER_SMALL+'</div>');
    $.ajax({
        url:'/populate/'+corpId,
        type: 'POST',
        data: JSON.stringify(data),
        error: populateError,
        success: populateSuccess,
        async: async
    })
}

function populateSuccess(r, stat, jqXHR) {
    $('#fine-list').html(r);
    nexts = {};
    $('.igtrow').each(function(i, elt) {
        igtid = $(elt).attr('igtid');
        nexts[igtid] = $(elt).attr('next');
    });
    localStorage.setItem('nexts', JSON.stringify(nexts));
}

function populateError() {
    $('#fine-list').text("An error occurred.");
}

/* display a single IGT instance */
function displayIGT(corp_id, igt_id) {
    $('#editor-panel').html(AJAX_LOADER_BIG);
    url = '/display/'+corp_id+'/'+igt_id+'?user='+userID();
    $.ajax({
        url: url,
        success: displaySuccess,
        error: displayError,
        contentType : "json"
    });
}

function displaySuccess(r, stat, jqXHR) {
    // Get the data out of the response.
    data = JSON.parse(r);
    content = data['content'];
    $('#editor-panel').html(content);

    // createCombos
    createCombos();

    // Assign the tooltips to the interface elements.
    assign_tooltips();

    // Stash the current versions of the clean lines for undo-ing.
    stashCleanLines();
    $('.igtrow').removeClass(CURRENT_ROW);
    $('#igtrow-'+igtId()).addClass(CURRENT_ROW);
}

/* COMBO FUNCTIONS */
function createCombos() {
    $('.taglabel-combo').each(function(i, comboElt) {
        if (!$(comboElt).hasClass('combo-f')) {
            var labels = $(comboElt).next('.taglabels');
            $(comboElt).combo({
                multiple: true,
                editable: false,
                checkbox: true,
                panelHeight: 'auto'
            });
            var panel = $(comboElt).combo('panel');
            labels.appendTo(panel);

            labels.find('input').each(function (i, elt) {
                $(elt).click(function () {
                    updateCombo(comboElt, labels);
                });
            });

            // Begin an array of the marked items
            updateCombo(comboElt, labels);
        }
    });

    labelTooltips();
}

function updateCombo(comboElt, labels) {
    var labelArr = [];
    $(labels).find('input').each(function(i, labelElt) {
        var v = $(labelElt).val();
        if ($(labelElt).is(':checked')) {
            labelArr.push(v);
        }
    });
    $(comboElt).combo('setText', labelArr.join('+'));
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
        linedata['lineno'] = $(el).find('.lineno').text();
        lines.push(linedata);
    });
    return lines;
}

/* Retrieve Clean Tiers */
function get_tier_lines(rowSelector) {

    var lines = [];

    /* Iterate over all the clean items, and add them to the data */
    $(rowSelector).each(function(i, el) {

        // Set up the data that will be returned for the lines.
        linedata = {};

        // Set the tag value.
        linedata['tag'] = $(el).find('.tags option:selected').val();
        linedata['labels'] = $(el).find('.taglabel-combo').combo('getText');
        linedata['judgment'] = $(el).find('input.judgment').val();
        linedata['lineno'] = $(el).find('.lineno').text();

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

/* Cleaning */
function cleanIGT(corp_id, igt_id, alreadyGenerated) {

    cleanExists = $('#clean-contents').html().trim();

    var regenerate = true;
    if (cleanExists) {
        regenerate = confirm("This will replace the data on the clean tier. Is this ok?");
    }

    if (regenerate) {
        $('#clean-contents').html('Loading...');
        $('#generate-normalized').val(NORM_GEN);
        $('#normalized-tier').hide();
        $('#normalized-contents').html('');
        disableYellowGreen();
        $('#group-2-content').html(''); // Blank out the group 2 content.


        $.ajax({
            url: '/clean/' + corp_id + '/' + igt_id,
            type: 'GET',
            dataType: 'html',
            success: cleanSuccess,
            error: cleanError
        });
    }
}

function cleanSuccess(r, stat, jqXHR) {

    $('#clean-contents').html(r);
    $('#clean-tier').show();

    $('#generate-clean').val(CLEAN_REGEN);

    createCombos();
    assign_tooltips();
    stashCleanLines();
}

function cleanError(r) {
    $('#clean-tier').show();
    $('#clean-contents').text("An error occurred.");
    console.error(r);
}

/* Normalization */
function normalizeIGT(corp_id, igt_id, alreadyGenerated) {

    normExists = $('#normalized-contents').html().trim();

    var regenerate = true;

    if (normExists) {
        regenerate = confirm("This will replace the existing normalized tier. Are you sure? ");
    }

    if (regenerate) {

        $('#normalized-contents').html('Loading...');

        cleanData = {lines: get_clean_lines()};

        $.ajax({
            url: '/normalize/' + corp_id + '/' + igt_id,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(cleanData),
            contentType: 'application/json',
            success: normalizeSuccess,
            error: normalizeError
        });
    }
}

function disableYellowGreen() {
    rg = $('#rating-green');
    ry = $('#rating-yellow');

    rg.removeClass(RATING_ENABLED);
    ry.removeClass(RATING_ENABLED);
    rg.addClass(RATING_DISABLED);
    ry.addClass(RATING_DISABLED);

    rg.attr('onclick', '');
    ry.attr('onclick', '');
}

function enableYellowGreen() {
    $('.rating-button').removeClass(RATING_DISABLED);
    $('.rating-button').addClass(RATING_ENABLED);
    $('#rating-green').click(function() {setRating(GOOD_QUALITY)});
    $('#rating-yellow').click(function() {setRating(OK_QUALITY)});
}

function normalizeSuccess(r, stat, jqXHR) {

    $('#normalized-tier').show();
    $('#generate-normalized').val(NORM_REGEN);
    $('#normalized-contents').html(r['content']);

    assign_tooltips();
    stashNormLines();
    createCombos();

    // Once the normalized lines are shown, it's okay for
    // the user to use the green/yellow buttons.
    enableYellowGreen();
}

function normalizeError(r) {
    $('#normalized-contents').text("An error occured while normalizing.");
    console.error(r);
}

/* INTENT-ification */
function generateFromNormalized(corp_id, igt_id) {
    normalData = get_normal_lines();
    cleanData  = get_clean_lines();
    rawData    = get_raw_lines();

    data = {raw: rawData,
            clean: cleanData,
            normal: normalData};

    $('#group-2-content').html("Analyzing...");

    analyzeUnmark('glm');
    analyzeUnmark('glw');
    analyzeUnmark('tag');
    analyzeUnmark('col');

    $.ajax({
        url: '/intentify/'+corp_id+'/'+igt_id,
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: intentifySuccess,
        error: intentifyError
    });
}

function analyzeUnmark(id) {
    $('#'+id).removeClass(FEEDBACK_WARN);
    $('#'+id).removeClass(FEEDBACK_OK);
}

function analyzeWarn(id) {
    $('#'+id).addClass(FEEDBACK_WARN);
}

function analyzeOK(id) {
    $('#'+id).addClass(FEEDBACK_OK);
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
    $('#group-2-content').html('');
    igtLayout('#group-2-content', r['igt']);
}

function intentifyError() {
    $('#group-2-content').html('')
    $('#group-2-content').text("An error occurred producing the remaining tiers.")
}

/* Edit/Delete Scripts */
function deleteItem(elt, itemId) {

    var identifier = '#'+itemId;

    /* Start by hiding the tooltip, if there is one shown. */
    $(elt).tooltip('hide');

    /* If this button has been clicked already,
     * restore (as a toggle) */
    if ($(elt).hasClass(ICON_CLICKED)) {
        $(elt).removeClass(ICON_CLICKED);

        // Unmark the item for deletion.
        $(identifier).find('input').prop('disabled',false);
        $(identifier).removeClass('for-deletion');

    } else {

    /* Otherwise, set it clicked, and delete it. */
        $(elt).addClass(ICON_CLICKED);

        // If neither of the boxes are filled out, delete the
        // element.
        if ($(identifier).find('.line-input').val().trim() == '') {
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
    numitems = $('.'+rowtype).length;

    id = prefix+(numitems+1).toString();

    if (rowtype == 'normalrow')
        var lineHTML = $($('#norm_row_template').html());
    else
        var lineHTML = $($('#row_template').html());
    lineHTML.attr('id', id);    // set the id to the new id
    lineHTML.addClass(rowtype); // Add the row class

    /* Change the functions */
    lineHTML.find('.undo').attr("onclick", "restoreItem('"+id+'")');
    lineHTML.find('.delete').attr("onclick", "deleteItem(this, '"+id+"')");
    lineHTML.find('.add').attr("onclick", "addItem('"+prefix+"',$(this).closest('tr'),'"+rowtype+"')");

    jqAfter.after(lineHTML.get(0));
    createCombos();
}

/* Retrieve the IGT id and Corp ID */
function igtId() {
    id = $('#igt-instance').attr('igtid');
    console.log(id);
    return id;
}

function corpId() {
    return $('#igt-instance').attr('corpid');
}

/* Save the edited tier! */
function setRating(rating) {
    $('.rating-button').removeClass(ICON_CLICKED);
    $('.rating-reasons').hide();
    $('#submit-instance').show();
    $('#comment-container').show();

    localStorage.setItem("instance-rating", rating);

    if (rating == BAD_QUALITY) {
        $('#bad-reasons').show();
        $('#rating-red').addClass(ICON_CLICKED);
    } else if (rating == OK_QUALITY) {
        $('#ok-reasons').show();
        $('#rating-yellow').addClass(ICON_CLICKED);
    } else if (rating == GOOD_QUALITY) {
        $('#rating-green').addClass(ICON_CLICKED);
    }
}

function userID() {
    return $("#userID").text();
}

// Save IGT
function saveIGT() {

    // ----------------------------------
    // Get the reason for editing
    // ----------------------------------
    rating = parseInt(localStorage.getItem('instance-rating'));
    reason_select = null;
    if (rating == BAD_QUALITY) {
        reason_select = $('#bad-reasons');
    } else if (rating == OK_QUALITY) {
        reason_select = $('#ok-reasons');
    }

    reason_str = null;
    if (!(reason_select === null)) {
        reason_str = reason_select.find('option:selected').val();
    }

    // ----------------------------------
    // Ensure that a reason was given
    // ----------------------------------
    if (!(reason_select === null) && !(reason_str)) {
        alert('Please choose a reason for the rating.');
        } else {

        var data = {
            rating: rating,
            norm: get_normal_lines(),
            clean: get_clean_lines(),
            raw: get_raw_lines(),
            userID: userID(),
            comment: $("#freeform-comment").val()
        };


        console.log(igtId() + ' ' + corpId());
        $.ajax({
            url: '/save/' + corpId() + '/' + igtId(),
            type: 'PUT',
            data: JSON.stringify(data),
            success: saveSuccess,
            contentType: 'application/json',
            error: saveError
        });
    }
}

/* Split an Instance */
function splitIGT(corpId, IgtId) {

    var confirmSplit = confirm("This will make two copies of the current instance at the current state. Do you wish to proceed?");
    if (confirmSplit) {
        //-------------------------------------------
        // Let's start by doing the same thing as
        // we would in saving (e.g., getting all the
        // clean and normalized lines)
        //-------------------------------------------
        var data = {
            norm: get_normal_lines(),
            clean: get_clean_lines(),
            raw:   get_raw_lines,
            userID: userID()
        };

        $.ajax({
            url: '/split/' + corpId + '/' + igtId(),
            type: 'POST',
            success: splitSuccess,
            data: JSON.stringify(data),
            contentType: 'application/json',
            error: splitError
        });
    }
}

function splitSuccess(r, stat, jqXHR) {
    populateIGTs(corpId(), false);
    data = JSON.parse(r);
    displayIGT(corpId(), data['next']);
    scrollToIGT(data['next']);
}

function splitError(r, stat, jq) {
    alert(r);
}

//-------------------------------------------

/* Deal with the additional comment field */
function toggleCommentBox() {
    var comments = $('#comments');
    var toggle = $('#comment-toggle');
    if (comments.is(':visible')) {
        comments.hide();
        toggle.val('Add Additional Comment');
    } else {
        comments.show();
        toggle.val('Hide Comment Field');
    }
}

function scrollToIGT(igtId) {
    var scrollPos = $('#igtrow-'+igtId).position().top + $('#fine-list').scrollTop()-52;
    $('#fine-list').animate({scrollTop : scrollPos}, 0);
}

function saveSuccess(r, stat, jqXHR) {
    populateIGTs(corpId(), false);
    nexts = JSON.parse(localStorage.getItem('nexts'));
    nextId = nexts[igtId()];

    // scroll the igt list to the appropriate position
    scrollToIGT(nextId);

    // Now display the current IGT.
    displayIGT(corpId(), nextId);
}

function saveError(r, stat, jqXHR) {
    console.error("An error occurred saving the instance.");
    console.error(jqXHR.toString());
}

function deleteIGT() {

    doDelete = confirm("Are you sure you want to DELETE this instance?");


    if (doDelete) {
        next = JSON.parse(localStorage.getItem('nexts'))[igtId()];
        localStorage.setItem('deleteNext', next);

        data = {userID: userID()};

        $.ajax(
            {
                url: '/delete/' + corpId() + '/' + igtId(),
                type: "POST",
                data: JSON.stringify(data),
                contentType: 'application/json',
                success: deleteSuccess,
                error: deleteError
            }
        )
    }
}

function deleteSuccess(r) {
    populateIGTs(corpId(), false);
    nextId = localStorage.getItem('deleteNext');
    console.log("NEXT INSTANCE: " + nextId);
    scrollToIGT(nextId);
    displayIGT(corpId(), nextId);
    localStorage.removeItem('deleteNext');

}

function deleteError(r) {
    alert(r.toString());
}

/* Highlighting for Word Display */
function modIdlist(idlist, classes, highlight) {
    cs = classes.split(',');
    for (j=0; j<cs.length; j++) {
        c = cs[j];

        ids = idlist.split(',');
        for (i=0; i < ids.length; i++) {
            s = '.'+c+'-' + ids[i];
            if (highlight == true) {
                $(s).css('background-color', 'red');
            } else {
                $(s).css('background-color', 'white');
            }
        }
    }
}

function highlightSrcs(obj, idlist, classes) {
    $(obj).css('background-color','cyan');
    modIdlist(idlist, 'gw,lw', true);
}

function unhighlightSrcs(obj, idlist) {
    $(obj).css('background-color', 'white');
    modIdlist(idlist, 'gw,lw', false);
}