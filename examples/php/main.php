<?php
$url = 'https://devtest.newpage.app/graphql/v1/graphql';
$tokenFile = '../../token.json';
try {
    $tokenData = file_get_contents($tokenFile);
    if ($tokenData === false) {
        throw new Exception("Could not read token file");
    }
    $tokenJson = json_decode($tokenData, true);
    if ($tokenJson === null || !isset($tokenJson['id_token'])) {
        throw new Exception("Could not find id_token in token file");
    }
    $token = $tokenJson['id_token'];
} catch (Exception $e) {
    echo "Exception wile reading token file: " . $e->getMessage() . "\n";
    echo "Run npm start at the root of the project in order to generate the token file";
    exit;
}

$headers = [
    'Authorization: Bearer ' . $token,
    'Content-Type: application/json'
];

$query = '
query MyQuery {
    carrier {
      id
      label
      createdAt
      updatedAt
    }
  }
';

$options = [
    'http' => [
        'header' => implode("\r\n", $headers),
        'method' => 'POST',
        'content' => json_encode(['query' => $query])
    ]
];

$context = stream_context_create($options);
$result = file_get_contents($url, false, $context);
if ($result === FALSE) {
    // Handle error
}

echo "Response:\n";
echo json_encode(json_decode($result), JSON_PRETTY_PRINT);

echo "\n";
