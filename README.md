LifeCompass - 音声相談アプリ

📌 概要
LifeCompass は「声を丁寧に聴く」ことをテーマにした AI搭載のオンライン相談アプリです。
ユーザーが音声で話した内容を AI が文字起こしし、応答を生成。さらに音声合成で返すことで、まるで本当に会話しているように相談を進めることができます。
「ちょっとした悩みでも安心して話せる場」を目指しています。

✨ 機能
	•	ユーザーが音声で相談内容を入力
	•	Whisper による音声認識 (Speech-to-Text)
	•	ChatGPT による応答生成 (Text-based counseling)
	•	Google Text-to-Speech (gTTS) など TTS での音声出力
	•	Web UI 上で会話履歴を確認・再生

🛠 技術スタック
	•	言語/フレームワーク: Python (Flask / FastAPI)
	•	音声処理: Whisper (STT), Google Text-to-Speech (gTTS)
	•	AI: OpenAI API (ChatGPT系)
	•	データベース: SQLite（会話ログ保存）
