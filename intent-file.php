<?php
/**
 * Created by PhpStorm.
 * User: rgeorgi
 * Date: 9/16/15
 * Time: 2:59 PM
 */

// -- 1) Get the environment settings from the env.ini file.
$config = parse_ini_file('env.ini');

// -- 2) Get the python exe from the settings
$py = $config['python_bin'];
$int = $config['intent_path'];

// -- 3) Get the file passed in by the user.
$infile = $_FILES['userfile']['tmp_name'];

// -- 4) Get a temporary output file...
$t = tempnam('', 'out');


// -- 5) Deal with the arguments...

/* ALN ARGUMENTS */

$aln_arr = array();
if (@$_POST['aln-giza'] == 'true')
    $aln_arr[0] = "giza";
if (@$_POST['aln-heur'] == 'true')
    $aln_arr[1] = "heur";

$aln_str = implode(',', $aln_arr);
if ($aln_str)
    $aln_arg = '--align '.$aln_str;
else
    $aln_arg = null;

/* POS ARGUMENTS */

$pos_arr = array();
if (@$_POST['pos-class'] == 'true')
    $pos_arr[0] = "class";
if (@$_POST['pos-proj'] == 'true')
    $pos_arr[1] = "proj";

$pos_str = implode(',',$pos_arr);
if ($pos_str)
    $pos_arg = '--pos '.$pos_str;
else
    $pos_arg = null;

/* PS/DS ARGUMENTS */

$parse_arr = array();
if (@$_POST['ps'] == 'trans')
    $parse_arr[0] = "trans";
if (@$_POST['ps'] == 'proj') {
    $parse_arr[0] = "trans";
    $parse_arr[1] = 'proj';
}

$parse_str = implode(',', $parse_arr);
if ($parse_str)
    $parse_arg = '--parse '.$parse_str;
else
    $parse_arg = null;

// Now put the commands together
// (And redirect stderr to stdout)
$command = "$py $int enrich $infile $t $aln_arg $pos_arg $parse_arg -vv 2>&1";


$descriptorspec = array(
    0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
    1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
    2 => array("pipe", "w") // stderr is a file to write to
);


// Open the script as a stream and output.
$pid = proc_open( $command, $descriptorspec, $pipes);

$status = proc_get_status($pid);
while ($status['running']) {
    sleep(0.25);
    $status = proc_get_status($pid);
}

$code = $status['exitcode'];

header('Content-Type: application/xml');
header("Exit-Code: $code");
header("Stdout: ".urlencode(stream_get_contents($pipes[1])));
//header("Stderr: ".urlencode(stream_get_contents($pipes[2])));
//header("tempfile: ".$infile);

if ($code == 0) {
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    readfile($t);
}
unlink($t);

?>
