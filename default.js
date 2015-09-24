/**
 * Created by rgeorgi on 9/22/15.
 */

/* GLOBAL STUFF */

function hideLoader() {
    loader = $('#loader-panel');
    loader.hide();
}
function showLoader() {
    loader = $('#loader-panel');
    loader.show();
}

function hideDownload() {
    $('#actualdownload').hide();
}

function showDownload() {
    $('#actualdownload').show();
    $('#actualdownload').css('display', '');
}

/* -------------- */

$(function() {
    $( "#tabs" ).tabs();

    /* Hide Loader */
    hideLoader();
    hideDownload();

    /* Hide Output Button */
    var ho = $('#hide-output-button');
    ho.button();
    ho.click(function() {toggleOutput()});

    /* Hide Stdout Button */
    var hs = $('#hide-stdout-button');
    hs.button();
    hs.click(function() {toggleStdout()});

    /* Actual Download Button */
    var dn = $('#actualdownload');
    dn.button();

    /* Bind the click function to the download link */
    dn.click(function() {
        this.download='export.xml';
        this.href='data:text/plain;charset=UTF-8,' + encodeURIComponent($('#xmlout').html());
    });

    setupTextSection();
    setupFileOptions();

});

function toggleOutput() {
    $('#output-panel').toggle();
}

function toggleStdout() {
    $('#stdout-section').toggle();
}

