<?php
/**
 * Created by PhpStorm.
 * User: rgeorgi
 * Date: 9/11/15
 * Time: 8:57 AM
 */

?>

<HTML>
    <HEAD>
        <meta charset="UTF-8">
        <TITLE>INTENT Web Interface</TITLE>

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
        <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>

        <!--   Add Jquery UI for Tabs     -->
        <script>
            $(function() {
                $( "#tabs" ).tabs();

//                Also restyle the buttons with JQueryUI
                $( "input[type=submit], a, button" );

//                Show/hide different elements
                $('#actualdownload').hide();
//                $('#output').hide();
                $('#loader').hide();
                $('#xmlout').hide();

                $("a#actualdownload").click(function(){
                    var now = new Date().toString();
                    this.download="export.xml";
                    this.href = "data:text/plain;charset=UTF-8," + encodeURIComponent($('#xmlout').html());
                });

            });
        </script>

    </HEAD>
    <BODY>

        <div style="text-align:center">
            <H1>
                INTENT Web Interface
            </H1>
        </div>

        <div id="tabs">
            <ul>
                <li><a href="#tabs-1">Enter Text</a></li>
                <li><a href="#tabs-2">Upload File</a></li>
            </ul>

            <div id="tabs-1" style="text-align:center">

                <div style="text-align:left; width:200px; float:left;"/>

                        <H2>Directions:</H2><BR/>
                        Type in your IGT instance(s), with <B>Lang</B>, <B>Gloss</B>, and <B>Translation</B> lines on separate
                        lines, and a blank line in between instances.

                </div>


                <div style="float:left;">
                    <textarea cols="80" rows="20" id="textbox" name="igt-text"></textarea> <BR/>
                </div>

                <!--    Add submit button -->
                <input type="submit" id="textsubmit" value="Convert to XIGT-XML"/>

                <BR/>
                <div id="output" style="clear:both; text-align:left"/>
                    <H2>Output:</H2>
                    <img id="loader" src="./images/ajax-loader.gif"/>
                    <PRE><div id="preout" style="width:100%;height:200px;overflow:auto;"></div></PRE>
                    <BR/>
                    <div id="xmlout"></div>

                    <a id="actualdownload"">Download</a>
                </div>

                <div class="ui-helper-clearfix"/>


            </div>
            <div id="tabs-2" style="...">
                TEST
                <form enctype="multipart/form-data" action="__URL__" method="POST">
                    <!-- MAX_FILE_SIZE must precede the file input field -->
                    <input type="hidden" name="MAX_FILE_SIZE" value="30000" />
                    <!-- Name of input element determines name in $_FILES array -->
                    Send this file: <input name="userfile" type="file" />
                    <input type="submit" value="Send File" />
                </form>

            </div>
            <div id="tabs-3">
                asdfasdfa
            </div>
        </div>

        <!-- This is for the POST -->
        <script type="text/javascript">
            $('input#textsubmit').click(function(){
                var tb = $('#textbox').val();
//                console.log(tb);
                $('#preout').hide();
                $('#actualdownload').hide();
                $('#loader').show();
                $.ajax({
                    type: "GET",
                    dataType : "text",
                    url: "intent-text.php",
                    success : posthandler,
                    data : {text : tb}
                });
            });


            function posthandler(r, stat) {
                $('#loader').hide();
//                console.log(r);
                $('#preout').show();
                $('#preout').text(r);
                $('#xmlout').html(r);
                $('#actualdownload').show();
//                $('#actualdownload').click(function(){
//                    // Download...
//                    doc = "data:application/xml;charset=UTF-8," + encodeURIComponent($('#xmlout').html());
//                    this.href = doc;
//                });
                $('#output').show();
            }


        </script>



    </BODY>
</HTML>

