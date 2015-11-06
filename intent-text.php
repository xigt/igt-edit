<?php

// Get the environment settings from the env.ini file.
$config = parse_ini_file('env.ini');

// Get the python exe from the settings
$py = $config['python_bin'];
$int = $config['intent_path'];

//Get a temporary output file...
$temp = tempnam('', 'out');

$temp_input = tempnam('', 'user');
$temp_input_f = fopen($temp_input, 'wb');
fwrite($temp_input_f, $_POST['text']);
fclose($temp_input_f);


// Now put the commands together
// (And redirect stderr to stdout)
$command = "$py $int text $temp_input $temp 2>&1";

$descriptorspec = array(
    0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
    1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
    2 => array("file", "/dev/null", "a") // stderr is a file to write to
);

$env = $_ENV;
$env['USER'] = 'www';

// Open the script as a stream and output.
$pid = proc_open( $command, $descriptorspec, $pipes, null, $env);


$status = proc_get_status($pid);
while ($status['running']) {
    sleep(0.25);
    $status = proc_get_status($pid);
}
$code = $status['exitcode'];

header('Content-Type: application/xml');
header("Exit-Code: $code");
header("Stdout: ".urlencode(stream_get_contents($pipes[1])));

if ($code == 0) {
    echo '<?xml version="1.0" encoding="UTF-8"?>'."\n";
    readfile($temp);
}

proc_close($pid);
unlink($temp);
unlink($temp_input);

?>

