<?php
// Simple form to POST image URL to Render Gemini API.

$api_url = "https://cooking-ai-api-pieo.onrender.com/gemini";
$result = null;
$error = null;

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $image_url = trim($_POST["image_url"] ?? "");

    if ($image_url === "") {
        $error = "画像URLを入力してください。";
    } else {
        $payload = json_encode(["url" => $image_url], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

        $ch = curl_init($api_url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_HTTPHEADER => ["Content-Type: application/json"],
            CURLOPT_POSTFIELDS => $payload,
            CURLOPT_TIMEOUT => 60,
        ]);
        $response = curl_exec($ch);
        $curl_error = curl_error($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($response === false) {
            $error = "cURLエラー: " . $curl_error;
        } elseif ($http_code >= 400) {
            $error = "HTTPエラー: " . $http_code . " / " . $response;
        } else {
            $result = $response;
        }
    }
}
?>
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Gemini API POST Test</title>
  <style>
    body { font-family: sans-serif; max-width: 820px; margin: 24px auto; padding: 0 16px; }
    label { display: block; margin-bottom: 6px; }
    input[type="text"] { width: 100%; padding: 10px; }
    button { margin-top: 12px; padding: 10px 16px; }
    pre { background: #f5f5f5; padding: 12px; overflow: auto; }
    .error { color: #b00020; margin-top: 12px; }
  </style>
</head>
<body>
  <h1>Gemini API POST テスト</h1>
  <form method="post">
    <label for="image_url">画像URL</label>
    <input type="text" id="image_url" name="image_url" placeholder="https://example.com/image.jpg" value="<?php echo htmlspecialchars($_POST['image_url'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">
    <button type="submit">送信</button>
  </form>

<?php if ($error): ?>
  <div class="error"><?php echo htmlspecialchars($error, ENT_QUOTES, 'UTF-8'); ?></div>
<?php endif; ?>

<?php if ($result): ?>
  <h2>レスポンス</h2>
  <pre><?php echo htmlspecialchars($result, ENT_QUOTES, 'UTF-8'); ?></pre>
<?php endif; ?>
</body>
</html>
