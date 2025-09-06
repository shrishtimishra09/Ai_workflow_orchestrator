import openai
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"


def register_ai_routes(app, db, CodeReview):

    @app.route("/", methods=["GET"])
    def home():
        return "✅ AI Agent is live using OpenRouter!"

    @app.route("/review", methods=["POST"])
    def review_code():
        try:
            data = request.get_json()
            code = data.get("code")
            user_id = data.get("userId")

            if not code or not user_id:
                return jsonify({"error": "Missing code or user ID"}), 400

            prompt = f"""
You are a senior software engineer and code reviewer.

Please analyze the following code and provide a structured review:
1. Summarize what the code is doing (1-2 lines)
2. Point out any bugs, logic issues, or bad practices
3. Suggest improvements (clarity, performance, best practices)
4. Rate the overall quality from 1 to 5
5. Provide the review as markdown-formatted bullet points

Code:
{code}
"""

            client = openai.OpenAI(
                api_key=openai.api_key,
                base_url=openai.base_url,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "AI-Workflow-Orchestrator"
                }
            )

            response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{ "role": "user", "content": prompt }],
                max_tokens=500
            )

            review = response.choices[0].message.content

            review_entry = CodeReview(code=code, review=review, user_id=user_id)
            db.session.add(review_entry)
            db.session.commit()

            return jsonify({ "review": review })

        except Exception as e:
            print("❌ Review Error:", e)
            return jsonify({ "error": str(e) }), 500


    @app.route("/generate-tests", methods=["POST"])
    def generate_tests():
        try:
            data = request.get_json()
            code = data.get("code")

            if not code:
                return jsonify({"error": "Missing code input"}), 400

            prompt = f"""
You are a senior developer. Please generate unit test cases (using pytest or unittest) for the following Python code:

{code}

Format the tests cleanly in markdown.
"""

            client = openai.OpenAI(
                api_key=openai.api_key,
                base_url=openai.base_url,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "AI-Workflow-Orchestrator"
                }
            )

            response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{ "role": "user", "content": prompt }],
                max_tokens=500
            )

            return jsonify({ "tests": response.choices[0].message.content })

        except Exception as e:
            print("❌ Test Generation Error:", e)
            return jsonify({ "error": str(e) }), 500


    @app.route("/history", methods=["GET"])
    def get_history():
        try:
            user_id = request.args.get("userId")
            if not user_id:
                return jsonify({ "error": "Missing userId" }), 400

            reviews = CodeReview.query.filter_by(user_id=user_id)\
                .order_by(CodeReview.timestamp.desc())\
                .limit(10).all()

            return jsonify([
                {
                    "id": r.id,
                    "code": r.code,
                    "review": r.review,
                    "timestamp": r.timestamp.isoformat()
                } for r in reviews
            ])

        except Exception as e:
            print("❌ History Fetch Error:", e)
            return jsonify({ "error": str(e) }), 500


    @app.route("/merge-suggest", methods=["POST"])
    def suggest_merge():
        try:
            data = request.get_json()
            diff = data.get("diff")

            if not diff:
                return jsonify({"error": "Missing code diff"}), 400

            prompt = (
                "You're a senior software engineer reviewing a code diff.\n\n"
                "Analyze this code change for safety, impact, and style.\n"
                "Suggest whether it should be merged or not. Provide a detailed explanation with a final Yes/No verdict.\n\n"
                "```diff\n"
                f"{diff}\n"
                "```"
            )

            client = openai.OpenAI(
                api_key=openai.api_key,
                base_url=openai.base_url,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "AI-Workflow-Orchestrator"
                }
            )

            response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{ "role": "user", "content": prompt }],
                max_tokens=300
            )

            return jsonify({ "suggestion": response.choices[0].message.content })

        except Exception as e:
            print("❌ Merge Suggestion Error:", e)
            return jsonify({ "error": str(e) }), 500


