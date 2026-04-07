from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify
from chatbot import chat

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"response": "Please type a message!"})
        response = chat(user_input)
        return jsonify({"response": response})
    except Exception:
        return jsonify({"response": "I'm not sure about that one! Try asking me about resumes, interviews, internships, job searching, or salary negotiation."})


if __name__ == "__main__":
    app.run(debug=True)
