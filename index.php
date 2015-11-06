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

        <script src="jquery-2.1.4.min.js"></script>
        <link rel="stylesheet" href="jquery-ui/jquery-ui.css"/>
        <link rel="stylesheet" href="default.css"/>
        <script src="jquery-ui/jquery-ui.min.js"></script>

        <!-- For the main page setup and other stuff -->
        <script src="default.js"></script>

        <!-- For the behaviors on the file tab -->
        <script src="file_behaviors.js"></script>

        <!-- For the behaviors on the text tab -->
        <script src="text_behaviors.js"></script>


    </HEAD>
    <BODY>

        <div id="title">
            INTENT Web Interface
        </div>

        <div id="tabs">
            <ul>
                <li><a href="#tabs-2">Upload File</a></li>
                <li><a href="#tabs-1">Enter Text</a></li>

            </ul>

            <div id="tabs-1" style="text-align:center">

                <div class="directions">

                        <H2>Directions:</H2><BR/>
                        Type in your IGT instance(s), with <B>Lang</B>, <B>Gloss</B>, and <B>Translation</B> lines on separate
                        lines, and a blank line in between instances.

                </div>

                <!-- TEXT AREA / INPUT SECTION -->
                <div class="input-section">
                        <textarea cols="50" rows="20" id="textbox"
                                  style="font-family: Courier" name="igt-text"></textarea> <BR/>

                    <!-- SUBMIT BUTTON -->
                    <div class="submit-section">
                        <input type="submit" id="textsubmit" value="Convert to XIGT-XML"/>
                    </div>

                </div>




                <BR/>



                <div class="ui-helper-clearfix"></div>

                <div id="text-msg"></div>

            </div>
            <!-- END OF TEXT TAB            -->






            <!--    FILE UPLOAD SECTION    -->
            <div id="tabs-2">
                <!--     BEGIN DIRECTIONS      -->
                <div class="directions"/>
                    <H2>Directions:</H2>
                    Choose your XIGT-XML file to enrich, and the options to use in order to enrich it.
                </div>
                <div class="input-section">

                    <!-- FILE UPLOAD FORM -->
                    <form enctype="multipart/form-data" action="intent-file.php" method="POST">

                        <!-- For spacing... -->
                        <div id="hidden" class="optcolumn" style="background-color:transparent !important;"></div>

                        <div id="file-select" class="optcolumn">
                            <!-- MAX_FILE_SIZE must precede the file input field -->
                            <input type="hidden" name="MAX_FILE_SIZE" value="3000000" />
                            <!-- Name of input element determines name in $_FILES array -->
                            <H3>Select File:</H3><input id="inputfile" name="userfile" type="file" />
                        </div>
                        <div class="ui-helper-clearfix"></div>


                        <!-- OPTION CHECKBOXES -->

                        <!--POS OPTIONS-->
                        <div id="pos-options" class="optcolumn">
                            <H3>POS Tags</H3>
                            <div id="pos-checkboxes" style="text-align: left">
                                <input id="pos-class" type="checkbox" value="test2"/> Use Classifier <BR/>
                                <input id="pos-proj"  type="checkbox" value="test3"/> Use Projection
                            </div>
                        </div>

                        <!-- PARSE OPTIONS -->
                        <div id="ps-options" class="optcolumn">
                            <H3>Phrase/Dep Trees</H3>

                            <div id="ps-checkboxes">
                                <input name="ps" id="ps-none"  type="radio" value="none" checked="checked"/> None<BR/>
                                <input name="ps" id="ps-trans" type="radio" value="trans"/> Trans Only <BR/>
                                <input name="ps" id="ps-proj"  type="radio" value="proj"/> Trans + Project
                            </div>
                        </div>

                        <!-- ALIGNMENT OPTIONS -->
                        <div id="aln-options" class="optcolumn">
                            <H3>Alignment</H3>

                            <div id="aln-checkboxes">
                                <input id="aln-giza" type="checkbox"/> Giza <BR/>
                                <input id="aln-heur" type="checkbox"/> Heuristic
                            </div>
                        </div>

                        <!-- SUBMIT BUTTON -->
                        <div class="ui-helper-clearfix"></div>

                        <div id="enrich-submit">
                            <input name="verbose" type="checkbox" id="verbose"/> Verbose Mode
                            <input type="button" value="Enrich" onclick="clickEnrich()"/>
                        </div>

                        <!-- MESSAGE WINDOW -->
                        <div id="enrich-msg"></div>

                    </form>

                </div>


            <div class="ui-helper-clearfix"></div>
            </div>


            <div id="tabs-3">

            </div>
        </div>

        <div id="loader-panel">
            <img id="loader" src="./images/ajax-loader.gif"/>
        </div>


        <!-- STDOUT Panel -->
        <div id="stdout-panel-container" class="ui-widget-header ui-widget ui-corner-all">
            <span>Messages</span> <a id="hide-stdout-button">Hide/Show</a><BR/>
            <!-- For containing the STDOUT data from the program -->
            <div id="stdout-section" class="ui-widget-content">
                <PRE>
                    <div id="stdout"></div>
                </PRE>
            </div>
            <div class="ui-helper-clearfix"></div>
        </div>

        <!-- Output Panel -->
        <div id="output-panel-container" class="ui-widget-header ui-widget ui-corner-all">
            <span>Output</span> <a id="hide-output-button">Hide/Show</a> <a id="actualdownload">Download</a><BR/>
            <div id="output-panel" class="ui-widget-content">


                <PRE><div id="preout"></div></PRE>
                <BR/>
<!--                <div id="xmlout"></div>-->


                <div class="ui-helper-clearfix"></div>
            </div>


        </div>
        <!-- END OUTPUT PANEL -->




    </BODY>
</HTML>

