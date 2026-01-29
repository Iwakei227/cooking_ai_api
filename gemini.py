import base64
import json
import os
import traceback

import google.generativeai as genai
import httpx
from flask import Flask, jsonify, request

app = Flask(__name__)

FOOD_LIST = (
    "たまねぎ, にんじん, じゃがいも, キャベツ, ネギ, 大根, トマト, ピーマン, きゅうり, しょうが, "
    "ニンニク, しそ, ナス, かぼちゃ, しいたけ, しめじ, えのき, ブロッコリー, もやし, 豆苗, 白菜, "
    "ほうれん草, ニラ, アボカド, パプリカ, ミニトマト, さつまいも, ごぼう, れんこん, オクラ, "
    "トウモロコシ, アスパラガス, エリンギ, マイタケ, マッシュルーム, 小松菜, チンゲンサイ, 水菜, かぶ, "
    "さといも, 長いも, セロリ, ズッキーニ, ゴーヤ, トマト缶, コーン, ミックスベジタブル, えんどう豆, "
    "いんげん豆, えだまめ, 切り干し大根, みょうが, 干しシイタケ, きくらげ, ししとう, なめこ, たくあん, "
    "高菜, らっきょう, かいわれ大根, みつば, ベビーリーフ, クレソン, ルッコラ, 芽キャベツ, ラディッシュ, "
    "ベビーコーン, そらまめ, にんにくの芽, グリーンピース, 菜の花, 春菊, 野沢菜, モロヘイヤ, 空心菜, "
    "ピクルス, クリームコーン, ビーツ, マツタケ, ぎんなん, うり, ふき, うど, せり, たけのこ, たらの芽, "
    "菊, ぜんまい, こごみ, ゆり根, じゅんさい, かんきつ類, 鶏もも肉, 鶏むね肉, 鶏ささみ, 鶏手羽肉, "
    "砂肝, 鶏レバー, 牛ひき肉, 豚ひき肉, 鶏ひき肉, 豚ロース肉, 豚もも肉, 豚バラ肉, 豚ヒレ肉, "
    "豚レバー, 豚もつ, 牛バラ肉, 牛ヒレ肉, 牛もも肉, 牛ロース肉, 牛タン, 牛レバー, 鶏皮, ラム肉, 鴨肉, "
    "ベーコン, ソーセージ, ハム, チャーシュー, スパム, コンビーフ, サラミ, サケ, さば, まぐろ, サーモン, "
    "ぶり, タラ, たい, カツオ, カジキ, さんま, イワシ, アジ, ししゃも, かれい, ひらめ, スズキ, ほっけ, "
    "きす, ムツ, タチウオ, キンキ, ニシン, メバル, はも, カワハギ, ワカサギ, あゆ, ウナギ, あなご, イカ, "
    "タコ, エビ, 甘エビ, 伊勢エビ, カニ, あさり, しじみ, ホタテ, 牡蠣, 貝柱, はまぐり, ムール貝, あわび, "
    "ばか貝, 赤貝, ばい貝, しらす, たらこ, さくらえび, いくら, とびっこ, ウニ, かずのこ, しらこ, ほたるいか, "
    "くらげ, シーフードミックス, ツナ缶, さば缶, さけ缶, ちくわ, かまぼこ, はんぺん, 魚肉ソーセージ, めかぶ, "
    "米, うどん, 麺, パスタ, ショートパスタ, そば, 食パン, パン, フランスパン, もち, そうめん, 春雨, 小麦粉, "
    "片栗粉, お好み焼き粉, ホットケーキミックス, ベーキングパウダー, もち米, 玄米, そば米, ドライイースト, "
    "ゼラチン, ココア, 米粉, コーンスターチ, てんぷら粉, 白玉粉, 上新粉, 雑穀米, くず粉, 押し麦, そば粉, "
    "玄米粉, 卵, 牛乳, 豆腐, ヨーグルト, クリーム, プロセスチーズ, スライスチーズ, 豆乳, 納豆, 油揚げ, "
    "厚揚げ, 粉チーズ, クリームチーズ, モッツアレラチーズ, カマンベールチーズ, チーズ, 豆, 大豆, きなこ, "
    "おから, あずき, 高野豆腐, 湯葉, スキムミルク, ココナッツミルク, サワークリーム, うずらの卵, ピータン, "
    "リンゴ, バナナ, オレンジ, いちご, キウイ, ブルーベリー, ジャム, ピーナッツバター, チョコレート, レーズン, "
    "ナッツ, 香料, リキュール, ブランデー, メープルシロップ, 黒みつ, あんこ, もも, ぶどう, パイナップル, "
    "グレープフルーツ, マンゴー, みかん, スイカ, メロン, さくらんぼ, 柿, 梨, あんず, クランベリー, プルーン, "
    "洋なし, きんかん, プラム, パパイヤ, くり, オレンジジュース, リンゴジュース, ぶどうジュース, アイスクリーム, "
    "マシュマロ, クラッカー, コーンフレーク, 水あめ, ワカメ, ひじき, のり, かつお節, 昆布, こんにゃく, しらたき, "
    "ごま, 塩昆布, 天かす, とろろこんぶ, 青のり, キムチ, ザーサイ, メンマ, アンチョビ, オリーブ, ホワイトソース, "
    "がんも, さつま揚げ, ぎょうざの皮, ライスペーパー, もずく, ところてん, 松の実, ゆかり, かんぴょう, 麩, 酒かす, "
    "コーヒー, 紅茶, 茶, 甘栗, 甘酒, 梅, 梅干し, 梅酒, トマトジュース, 野菜ジュース, 抹茶, ポテトチップス, "
    "塩, 胡椒, 砂糖, 醤油, 料理酒, みりん, 酢, 味噌, バター, サラダ油, オリーブオイル, ごま油, マヨネーズ, "
    "ケチャップ, ドレッシング, レモン汁, めんつゆ, ソース, はちみつ, 豆板醤, 豆鼓, 甜面醤, おろしにんにく, "
    "おろししょうが, オイスターソース, スープの素, わさび, からし, ワイン, ポン酢, マスタード, ラー油, コチュジャン, "
    "柚子胡椒, ナンプラー, バルサミコ酢, タバスコ, デミグラスソース, チリソース, 塩こうじ, たれ, カレー粉, パセリ, "
    "バジル, シナモン, ローリエ, ナツメグ, パクチー, とうがらし, ローズマリー, 山椒, クミン, ターメリック, サフラン, "
    "オールスパイス, ガーリックパウダー, オレガノ, タイム, ミント, 八角, チリパウダー, パプリカパウダー, クローブ, "
    "カルダモン, ディル, セージ, レモングラス, チャービル"
)


def _generate_from_image_url(image_url: str) -> str:
    if not image_url:
        raise ValueError("image_url is required")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    response_img = httpx.get(image_url, timeout=30.0)
    response_img.raise_for_status()
    image_data = base64.b64encode(response_img.content).decode("utf-8")

    prompt = (
        "画像の食材の個数を教えてください。\n"
        "食材名は" + FOOD_LIST + "ここから参照してください。\n\n"
        "重要:\n"
        "- 必ず以下の形式でJSON配列として出力すること\n"
        "- 余計な説明やマークダウン記法は一切付けないこと\n"
        "- 形式: [[\"食材名\", 数量], [\"食材名\", 数量]]\n"
        "- 例: [[\"アボカド\", 1], [\"いちご\", 3]]\n\n"
        "JSON配列のみを出力:\n"
    )

    response = model.generate_content(
        [
            {"mime_type": "image/png", "data": image_data},
            prompt,
        ]
    )
    return response.text


@app.post("/gemini")
def gemini_api():
    try:
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            image_url = payload.get("url") or payload.get("image_url")
        else:
            image_url = request.form.get("url") or request.form.get("image_url")

        result_text = _generate_from_image_url(image_url)

        try:
            parsed = json.loads(result_text)
            return jsonify({"ok": True, "result": parsed})
        except json.JSONDecodeError:
            return jsonify({"ok": True, "result": result_text})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 400


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
