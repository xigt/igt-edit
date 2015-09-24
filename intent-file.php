<?php
/**
 * Created by PhpStorm.
 * User: rgeorgi
 * Date: 9/16/15
 * Time: 2:59 PM
 */



$infile = $_FILES['userfile']['tmp_name'];


// Get the environment settings from the env.ini file.
$config = parse_ini_file('env.ini');

// Get the python exe from the settings
$py = $config['python_bin'];
$int = $config['intent_path'];


//Get a temporary output file...
$t = tempnam('', 'out');


/* Get the alignment argument */
$aln_arr = array();
if ($_POST['aln-giza'] == 'true') {
    $aln_arr[0] = "giza";
}
if ($_POST['aln-heur'] == 'true') {
    $aln_arr[1] = "heur";
}
$aln_str = implode(',', $aln_arr);
if ($aln_str) {
    $aln_arg = '--align '.$aln_str;
}

$pos_arr = array();
if ($_POST['pos-class'] == 'true') {
    $pos_arr[0] = "class";
}
if ($_POST['pos-proj'] == 'true') {
    $pos_arr[1] = "proj";
}
$pos_str = implode(',',$pos_arr);
if ($pos_str) {
    $pos_arg = '--pos '.$pos_str;
}

// Now put the commands together
// (And redirect stderr to stdout)
$command = "$py $int enrich $infile $t $aln_arg $pos_arg 2>&1";

$descriptorspec = array(
    0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
    1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
    2 => array("file", "/dev/null", "a") // stderr is a file to write to
);




// Open the script as a stream and output.
$pid = proc_open( $command, $descriptorspec, $pipes, $cwd, $env);

$status = proc_get_status($pid);
while ($status['running']) {
    sleep(0.25);
    $status = proc_get_status($pid);
}

$code = $status['exitcode'];

//if (is_resource($pid)) {
    // $pipes now looks like this:
    // 0 => writeable handle connected to child stdin
    // 1 => readable handle connected to child stdout
    // Any error output will be appended to /tmp/error-output.txt
//    fwrite($pipes[0], $_GET['text']);
//    fclose($pipes[0]);

//}

header('Content-Type: application/xml');
//readfile($t);
echo "<RESPONSE>\n";

/* Put the exit status in here, too, so we can see if errors happened. */
echo "<STATUS>$code</STATUS>\n";
echo "<STDOUT>\n";
echo stream_get_contents($pipes[1]);
//print_r($_POST);

echo "</STDOUT>\n";


echo "<CONTENT>\n";
readfile($t);
echo "</CONTENT>\n</RESPONSE>";
?>
