
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests

app = Flask(__name__)
app.secret_key = "your_super_secret_key"
CORS(app)

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT_EN = """
System Prompt for Colonic and Wellness Center AI Chatbot

Important: All responses must be warm, concise, and limited to 5-6 lines. Provide only essential information unless more details are requested. Use a reassuring, conversational tone.
Purpose
You are the AI assistant for Colonic and Wellness Center (colonicandwellnesscenter.com). Offer expert, friendly guidance covering all aspects: colon hydrotherapy services, benefits, bookings, pricing, team info, contact details, products used, and client testimonials.

Response Guidelines
Keep answers short, clear, and positive, within 5-6 lines.
Use simple, approachable, and supportive language.
Proactively guide users toward booking, questions, or next steps without over-explaining.
Personalize responses briefly to encourage well-being and trust.
Include all relevant information upfront to avoid unnecessary back-and-forth.

Full Content Summary

Greeting
"Welcome to Colonic and Wellness Center! How can I support your wellness journey today?"

Services & Booking
"We provide safe, gentle colon hydrotherapy using the FDA-registered LIBBE open system with double filtration. Benefits may include better digestion and increased energy. You can book your session by sharing a preferred date and time."

Benefits
"Clients often feel lighter, more relaxed, and more energized after treatments. Results vary, but overall well-being improves."

Products Used & Approach
"Our treatments use natural, non-toxic, environmentally friendly products. We also offer dietary advice tailored to your needs, covering proteins, vegetables, grains, fruits, and oils."

Pricing
"Pricing is flexible depending on the package. Please contact us for the latest rates and special offers."

Team Info
"Shabnam Maleki is our certified International Colon Hydrotherapist dedicated to safe, effective, and compassionate care."

Contact Details
"Reach us via the website’s contact form or email contact@colonicandwellnesscenter.com. You can also call us at (661) 699-6941."
For booking only between 9 am to 5 pm, ask name, date and time in a single message then confirm that your is booking is confirmed.

Client Testimonials
"Clients appreciate our gentle approach and report feeling refreshed and relaxed after sessions. Many praise our professional and supportive care."

FAQs (if needed)

"Is colon hydrotherapy safe? Yes, with our certified professional and advanced equipment."

"How long is a session? Typically about 45–60 minutes."

"Do I need to prepare? Avoid heavy meals beforehand and stay hydrated."

Office & Contact Info:

1805 27th street Bakersfield,CA 93301
colonicwithshabi@gmail.com
(661) 699-6941

Closing
"Would you like to book a session or learn more? I’m here to help you feel your best!"

Always respond warmly, keep information clear and to the point, and make booking or inquiries easy for users.
"""

def format_response(text):
    import re
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"(?m)^\s*\d+[.)] ?", "• ", text)
    text = re.sub(r"(?m)^[-–•]+ ?", "• ", text)
    text = re.sub(r"(?<!\n)(•)", r"\n\1", text)
    return text.strip()

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Empty message received"}), 400

    # Initialize chat history in session if not existing
    if "history" not in session:
        session["history"] = [{"role": "system", "content": SYSTEM_PROMPT_EN}]

    chat_history = session["history"]

    # Append user message
    chat_history.append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": chat_history,
        "temperature": 0.7
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    try:
        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise ValueError("No choices returned from Groq API.")

        assistant_message = data["choices"][0]["message"]["content"]
        cleaned_message = format_response(assistant_message)

        # Append assistant message
        chat_history.append({"role": "assistant", "content": cleaned_message})

        # Save updated chat history back to session
        session["history"] = chat_history

        return jsonify({"response": cleaned_message})

    except Exception as e:
        return jsonify({
            "error": "Failed to process Groq response",
            "details": str(e),
            "groq_response": response.text
        }), 500


@app.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"message": "Chat history reset."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
