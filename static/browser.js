/* Constant Strings */
function ajax_loader_big() {
    return '<IMG src="'+staticURL+'images/ajax-loader.gif"/>';
}

function ajax_loader_small() {
    return '<IMG src="'+staticURL+'images/ajax-loader-small.gif"/>';
}

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
    window.location.href = appRoot()+'/user/'+userid;
}

function appRoot() {
    return approot;
}

/* Populate the IGT pane */
function populateIGTs(corpId, async) {

    if (typeof async === 'undefined') {async = false;}

    data = {userID : userID()};

    $('#fine-list').html('<div style="text-align:center;top:40px;position:relative;">'+ajax_loader_small()+'</div>');
    $.ajax({
        url:appRoot()+'/populate/'+corpId,
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

/* Download the corpus in XML if requested */
function downloadCorpus(corpId){
    location.href=appRoot()+'/download/'+corpId;
}

/* display a single IGT instance */
function displayIGT(corp_id, igt_id) {
    $('#editor-panel').html(ajax_loader_big());
    url = appRoot()+'/display/'+corp_id+'/'+igt_id+'?user='+userID();
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

    // resize the generated lines as neccessary
    checkTextWidths();

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
            url: appRoot()+'/clean/' + corp_id + '/' + igt_id,
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

    checkTextWidths();

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
            url: appRoot()+'/normalize/' + corp_id + '/' + igt_id,
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

    checkTextWidths();

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
        url: appRoot()+'/intentify/'+corp_id+'/'+igt_id,
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
    // $('#group-2-content').html('');
    // igtLayout('#group-2-content', r['igt']);
    $('#analysis').css('display','block');
    $('#group-2-content').html(r['group2']);
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
            reason: reason_str,
            raw: get_raw_lines(),
            userID: userID(),
            comment: $("#freeform-comment").val()
        };


        $.ajax({
            url: appRoot()+'/save/' + corpId() + '/' + igtId(),
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
            url: appRoot()+'/split/' + corpId + '/' + igtId(),
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
                url: appRoot()+'/delete/' + corpId() + '/' + igtId(),
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

function wIdNum(obj) {
    var myId = cssId(obj);
    return idNum(myId);
}

function itemType(obj) {
    var idRegex = /([^0-9]+)/;
    return idRegex.exec(cssId(obj))[1];
}

function cssId(obj) {
    return $(obj).attr('id');
}

function idNum(s) {
    var idRegex = /([0-9]+)/;
    return parseInt(idRegex.exec(s)[1])
}

function isItemType(obj, t) { return itemType(obj) == t;}
function isGw(obj) {return isItemType(obj, 'gw');}
function isTw(obj) {return isItemType(obj, 'tw');}
function isLw(obj) {return isItemType(obj, 'w');}
function isGm(obj) {return isItemType(obj, 'g');}
function isLm(obj) {return isItemType(obj, 'm');}


/* HIGHLIGHTING FOR HOVER */

function highlight(obj) {
    highlight_helper(obj, true);
}

function unhighlight(obj) {
    highlight_helper(obj, false);
}

function getAln(arr, myId, myIdx) {
    // console.log('Pairing "'+myId+'" with idx='+myIdx+' in arr '+arr.toString());
    var retArr = [];
    var otherIdx = myIdx == 0 ? 1 : 0;
    for (i=0; i<arr.length; i++) {
        var eltId = arr[i][myIdx];
        var oId = arr[i][otherIdx];
        if (eltId == myId)
            retArr.push(oId);
    }
    return retArr;
}

function getAlnW(myId, myIdx) {
    return getAln(w_aln, myId, myIdx);
}

function getAlnM(myId, myIdx) {
    return getAln(m_aln, myId, myIdx);
}

// -------------------------------------------
// COLORS FOR ALIGNMENTS
// -------------------------------------------

SELF_COLOR = 'tomato';

ALN_COLOR = 'DeepSkyBlue'; // For elements an elt is aligned with directly
REL_COLOR = 'PowderBlue'; // For elements aligned with a related element

SUB_COLOR = 'lightsalmon'; // For elements subsumed by this element
SUP_COLOR = 'lightgreen'; // For parents of this element

function highlightList(arr, color, entering) {
    color = entering ? color : 'white';
    idArr = arr.map(function(s){return '#'+s;});
    // console.log('Highlighting "' + arr.join(',') +'" with ' + color);
    $(idArr.join(',')).css('background-color', color);
}

function highlight_helper(obj, entering) {
    var myNum = wIdNum(obj);
    var myId = cssId(obj);

    // If we are in alignment mode, add a
    // border, then halt
    if (alignClicked) {
        if (obj == alignClicked) {return} // don't alter the item already clicked
        if (entering) var border = 'solid pink';
        else var border = 'solid white';
        $(obj).css('border', border);
        return
    }


    var rels = [];
    var subs = [];
    var sups = [];
    var alns = [];

    if (isGw(obj)) {
        // SUB: gm, REL: m, ALN: w, tw
        var myLw = 'w'+myNum.toString(); alns = alns.concat([myLw]);
        var myTws = getAlnW(myLw, 1); alns = alns.concat(myTws);
        var myGms = gw_to_gm[myId]; subs = subs.concat(myGms);
        var myMs = lw_to_lm[myLw]; rels = rels.concat(myMs);
    } else if (isTw(obj)) {
        // ALN: Gw, Lw REL: Gm
        var myLws = getAlnW(myId, 0); alns = alns.concat(myLws);
        var myGws = myLws.map(function(x){return 'gw'+idNum(x)}); alns = alns.concat(myGws);
        var myGms = getAlnM(myId, 0); alns=alns.concat(myGms);
    } else if (isLw(obj)) {
        var myMs = lw_to_lm[myId]; subs = subs.concat(myMs);
        var myTws = getAlnW(myId, 1); alns = alns.concat(myTws);
        var myGw = 'gw'+myNum.toString(); alns = alns.concat([myGw]);
        var myGms = gw_to_gm[myGw]; rels = rels.concat(myGms);
    } else if (isLm(obj)) {
        var myLw = $(obj).attr('parentWord'); sups = sups.concat([myLw]);
        var myGw = 'gw'+idNum(myLw).toString(); rels = rels.concat([myGw]);
    } else if (isGm(obj)) {
        var myGw = $(obj).attr('parentWord'); sups = sups.concat([myGw]);
        var myLw = 'w'+idNum(myGw).toString(); rels = rels.concat([myLw]);
        var myTws = getAlnM(myId, 1); alns = alns.concat(myTws);
    }

    highlightList(rels, REL_COLOR, entering);
    highlightList(subs, SUB_COLOR, entering);
    highlightList(sups, SUP_COLOR, entering);
    highlightList(alns, ALN_COLOR, entering);
    highlightList([myId], SELF_COLOR, entering);
}


// Tell whether or not the word types are the
function similarType(me, other) {
    var myWT = itemType(me);
    var oWT = itemType(other);
    function isLWT(o) {return (itemType(o) == 'w' || itemType(o) == 'gw')}

    return ((myWT == 'tw' && oWT == 'tw') ||
    (isLWT(me) && isLWT(other)))
}

// -------------------------------------
// Add/undo alignments when clicked...
// -------------------------------------
function startAlign(obj) {
    // If we have already clicked an alignment,
    // we need to either add or remove this item


    if (alignClicked) {
        // we would like to cancel the operation without
        // doing anything if another word of the same
        // type is clicked.

        var myWT = itemType(obj);
        var oWT = itemType(alignClicked);
        if (similarType(obj, alignClicked)) {stopAlign(obj);}

        // Otherwise, we should handle the request
        // for adding or removing alignment.
        else {
            // Blink three times to indicate this is
            // the one being selected
            count = 0;
            blinkOn = false;
            intervalId = setInterval(function () {
                if (blinkOn) {
                    blinkOn = false;
                    $(obj).css('border', 'solid white');
                } else {
                    blinkOn = true;
                    $(obj).css('border', 'solid red');
                }
                count++;
                if (count == 7) {
                    blinkOn = false;
                    $(obj).css('border', 'solid white');
                    clearInterval(intervalId);
                    addAlign(obj);
                    stopAlign(obj);
                }
            }, 100);
        }

        // And no matter what's clicked, we should
        // exit the alignment mode.

    } else {
        $(obj).css('border', 'solid red');

        alignClicked = obj;
    }
}

// Stop being in adding alignment mode
function stopAlign(obj) {
    $(alignClicked).css('border', 'solid white');
    $(obj).css('border', 'solid white');
    alignClicked = false;

    $('.alignable-word').each(function(i, elt){
       unhighlight(elt);
    });
    highlight(obj);
}

function toggleArr(srcId, tgtId) {
    for (i=0;i<w_aln.length;i++) {
        if (w_aln[i][0] == srcId && w_aln[i][1] == tgtId) {
            w_aln.splice(i, 1);
            return
        }
    }
    w_aln.push([srcId, tgtId]);
}

function addAlign(obj) {
    var clickedId = cssId(obj);
    var prevId = cssId(alignClicked);

    function toLw(idStr) {return 'w' + idNum(idStr).toString();}
    function toTw(idStr) {return 'tw'+ idNum(idStr).toString();}

    if (isTw(obj)) {
        tgtId = toLw(prevId);
        srcId = toTw(clickedId); // Make sure to regularize
    } else {
        tgtId = toLw(clickedId);
        srcId = toTw(prevId);
    }

    toggleArr(srcId, tgtId);
}

/* All the stuff that needs fixing when the window is resized */

function doResizeStuff() {
    checkTextWidths();
    $('#mainwindow').height($(document).height() -35);
}

// -------------------------------------------
/* Make sure that the text input fields are the right width */

(function($) {
    $.fn.textWidth = function () {
        $body = $('body');
        $this =  $(this);
        $text = $this.text();
        if($text=='') $text = $this.val();
        var calc = '<div style="clear:both;display:block;visibility:hidden;white-space:pre"><span style="width;inherit;margin:0;font-family:'  + $this.css('font-family') + ';font-size:'  + $this.css('font-size') + ';font-weight:' + $this.css('font-weight') + '">' + $text + '</span></div>';
        $body.append(calc);
        var width = $('body').find('span:last').width();
        $body.find('span:last').parent().remove();
        return width;
    };
})(jQuery);


function checkTextWidths() {
    maxwidth=0;
    $('.line-input').each(function(i, elt) {
        maxwidth=Math.max(maxwidth, $(elt).textWidth()+10);
    });
    $('.textrow,.line-input').each(function(i, elt) {
       $(elt).css('min-width', maxwidth);
    });
}



// -------------------------------------------
// Functions that trigger on resize and catch keystrokes
// -------------------------------------------
$(document).keyup(function(e) {
   checkTextWidths();
});


$(window).resize(function() {
    doResizeStuff();
});

/*  */