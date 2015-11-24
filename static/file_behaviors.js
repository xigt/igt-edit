/**
 * Created by rgeorgi on 9/17/15.
 */


function ischecked(o) {
    return o.is(':checked');
}



function enricherr(em, str) {
    em.css('background-color', 'pink');
    em.html(str);
    em.show();
}

function enrichwarn(em, str) {
    em.css('background-color', '#E9E081');
    em.html(str);
    em.show();
}


function clickStats() {
    var out = $('#output');
    var pre = $('#preout');
    var std = $('#stdout');

    std.text('');
    out.text('');
    pre.text('');

    hideDownload();

    em = $('#enrich-msg');
    em.hide();

    var errors = false;

    var infile = $('#statsfile').get(0).files[0];
    //if (!infile) {
    //    enricherr(em, "<B>ERROR:</B> Must specify a file to get stats on.");
    //    errors = true;
    //    em.show();
    //}


    if (!errors) {
        showLoader();
        /* Finally, send the file for enrichment... */
        var data = new FormData();
        data.append("userfile", infile);

        $.ajax({
            url: "intent-stats.php",
            type: "POST",
            dataType: "text",
            data: data,
            contentType: false,
            processData: false,
            success: statssuccess
        });
    }
}

function statssuccess(r, stat, jqXHR) {
    var std = $('#stdout').text(r);
    hideLoader();
}

function clickEnrich() {

    /* The message space */
    em = $('#enrich-msg');
    em.hide();

    hideDownload();

    /* The output space */
    var out = $('#output');
    var std = $('#stdout');
    var pre = $('#preout');

    std.text("");
    pre.text("");

    /* POS Options */
    var posProj  = $('#pos-proj');
    var posClass = $('#pos-class');

    /* If no POS options are checked... */
    var noPOS = !(ischecked(posProj) || ischecked(posClass));


    /* PS Options */
    var psProj =  $("#ps-proj");
    var psNone = $('#ps-none');
    var psTrans= $('#ps-trans');

    var noPS = ischecked(psNone);


    var alnGiza = $('#aln-giza');
    var alnHeur = $('#aln-heur');

    var noAln = !(ischecked(alnGiza) || ischecked(alnHeur));


    var errors = false;
    /* Projection requested without alignment */
    if ((ischecked(psProj) || ischecked(posProj)) && noAln) {
        enricherr(em, '<B>ERROR:</B> cannot use a projection method without selecting at least one alignment method.')
        errors = true;
    }

    /* No enrichment requested */
    if (noAln && noPOS && noPS) {
        enrichwarn(em, "<B>WARNING:</B> No enrichment was requested. The file will be returned with morphemes and Gloss-Lang alignment, but no further enrichment.");
    }
    
    var infile = $('#inputfile').get(0).files[0];
    if (!infile) {
	    enricherr(em, "<B>ERROR:</B> Must specify a file to enrich.");
	    errors = true;
    }

    if (!errors) {
        /* Finally, send the file for enrichment... */

        var data = new FormData();
        data.append("infile", infile);

        /* Now, add the various settings. */
        if (ischecked(posClass)) data.append('pos_class', 1);
        if (ischecked(posProj)) data.append('pos_proj', 1);

        data.append("ps", $('input[name=ps]:checked').val());

        if (ischecked(alnGiza)) data.append('align_giza', 1);
        if (ischecked(alnHeur)) data.append('align_heur', 1);

        if (ischecked($('#verbose'))) data.append('verbose', 1);

        out.show();
        showLoader();

        $.ajax({
            url: "enrich",
            type: "POST",
            data: data,
            dataType: "text",
            contentType: false,
            processData: false,
            success: filesuccess
        });
    }
}



function filesuccess(r, stat, jqXHR) {

    hideLoader();

    /* Get the status */
    status = parseInt(jqXHR.getResponseHeader('Exit-Code'));

    /* Set the STDOUT field to contain the program output */
    std = getStdout(jqXHR);
    $('#stdout').text(std);
    $('#stdout').show();

    /* If the program exits correctly... */
    if (status == 0) {
        /* Get the XIGT doc and put it in "storage" */
        xc = $(r).find("xigt-corpus");
        localStorage.setItem('xml', r);
        $('#preout').text(r);
        showDownload();
    } else {
        $('#preout').text("There was an error in processing your file. Please see the messages above.");
    }
}


function setupFileOptions() {
    $('#enrich-msg').hide();
};

