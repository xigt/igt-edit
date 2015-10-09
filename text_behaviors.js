/**
 * Created by rgeorgi on 9/18/15.
 */

function setupTextSection() {
    $('#xmlout').hide();
    $('#text-msg').hide();



    /* Bind the click function to the convert button*/
    $('#textsubmit').click(function(){clickConvert()});
}

function clickConvert() {
    hideDownload();

    po = $('#preout');
    tm = $('#text-msg');

    po.text('');
    $('#stdout').text('');

    text_content = $('#textbox').val();

    tm.hide();

    if ($.trim(text_content) === "") {
        tm.html("<B>ERROR</B>: No Text was entered. Please refer to the directions to the left.");
        tm.show();
    } else if (text_content.split("\n").length < 3) {
        tm.html("<B>ERROR</B>: Too few lines entered. Please enter at least three lines.");
        tm.show();
    }
     else {
        showLoader();

        /* Now, send the ajax to the server... */
        $.ajax({
            type: "GET",
            dataType: "text",
            url: "intent-text.php",
            success: converthandler,
            data: {text: text_content}
        })
    }
}

function converthandler(r, stat, jqXHR) {
    hideLoader();

    /* Start by getting the status of the response */
    status = parseInt(jqXHR.getResponseHeader('Exit-Code'));

    console.log(status);

    /* And getting the STDOUT, if any. */
    stdout = getStdout(jqXHR);

    $('#stdout').text(stdout);
    $('#stdout').show();

    /* Finally, display the output if no error occured. */
    if (status == 0) {
        $('#preout').text(r);
        $('#xmlout').html(r);
    } else {
        $('#preout').text("There was an error processing the document. Please check the messages above for more information");
    }
}

/* Do Validation on the Text box before sending it... */

function validateIGTText() {
    console.log($('#textbox').val())
}