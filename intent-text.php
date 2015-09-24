<?php header('Content-type: application/xml');
// Get the environment settings from the env.ini file.
$config = parse_ini_file('env.ini');

// Get the python exe from the settings
$py = $config['python_bin'];
$int = $config['intent_path'];

//Get a temporary output file...
$t = tempnam('', 'out');

// Now put the commands together
// (And redirect stderr to stdout)
$command = "$py $int text - $t 2>&1";

$descriptorspec = array(
    0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
    1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
    2 => array("file", "/dev/null", "a") // stderr is a file to write to
);

// Open the script as a stream and output.
$pid = proc_open( $command, $descriptorspec, $pipes, $cwd, $env);


if (is_resource($pid)) {
    // $pipes now looks like this:
    // 0 => writeable handle connected to child stdin
    // 1 => readable handle connected to child stdout
    // Any error output will be appended to /tmp/error-output.txt
    fwrite($pipes[0], $_GET['text']);
    fclose($pipes[0]);

}

$status = proc_get_status($pid);
while ($status['running']) {
    sleep(0.25);
    $status = proc_get_status($pid);
}
$code = $status['exitcode'];

?><?php
echo "<RESPONSE>\n<STATUS>$code</STATUS>\n<STDOUT>\n";
echo stream_get_contents($pipes[1]);
echo "</STDOUT>\n<CONTENT>\n";
readfile($t);
echo "</CONTENT></RESPONSE>";

proc_close($pid);

?>

