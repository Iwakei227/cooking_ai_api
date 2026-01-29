<?php
// Simple form to POST dish name to Gemini image API.

$api_url = "http://localhost:5000/dish-image";
$result = null;
$result_pretty = null;
$error = null;
$image_url = null;

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $dish = trim($_POST["dish"] ?? "");

    if ($dish === "") {
        $error = "料理名を入力してください。";
    } else {
        $payload = json_encode(["dish" => $dish], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

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
            $decoded = json_decode($response, true);
            if (json_last_error() === JSON_ERROR_NONE) {
                $result_pretty = json_encode(
                    $decoded,
                    JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT
                );
                if (isset($decoded["image_url"])) {
                    $image_url = $decoded["image_url"];
                }
            }
        }
    }
}
?>
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Dish Image API POST Test</title>
  <style>
    body { font-family: sans-serif; max-width: 820px; margin: 24px auto; padding: 0 16px; }
    label { display: block; margin-bottom: 6px; }
    input[type="text"] { width: 100%; padding: 10px; }
    button { margin-top: 12px; padding: 10px 16px; }
    pre { background: #f5f5f5; padding: 12px; overflow: auto; }
    .error { color: #b00020; margin-top: 12px; }
    img { max-width: 100%; margin-top: 12px; display: block; }
  </style>
</head>
<body>
  <h1>料理名→画像 生成テスト</h1>
  <form method="post">
    <label for="dish">料理名</label>
    <input type="text" id="dish" name="dish" placeholder="カレーライス" value="<?php echo htmlspecialchars($_POST['dish'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">
    <button type="submit">送信</button>
  </form>

<?php if ($error): ?>
  <div class="error"><?php echo htmlspecialchars($error, ENT_QUOTES, 'UTF-8'); ?></div>
<?php endif; ?>

<?php if ($image_url): ?>
  <h2>生成画像</h2>
  <img src="<?php echo htmlspecialchars($image_url, ENT_QUOTES, 'UTF-8'); ?>" alt="generated">
<?php endif; ?>

<?php if ($result): ?>
  <h2>レスポンス</h2>
  <pre><?php echo htmlspecialchars($result_pretty ?? $result, ENT_QUOTES, 'UTF-8'); ?></pre>
<?php endif; ?>
</body>
</html>
