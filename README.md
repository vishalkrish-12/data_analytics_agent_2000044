# Data Analytics Agent (T5)

Unlock the power of data with an intelligent agent that answers your analytics questions, generates insights, and creates visualizations—all from natural language prompts!

## 🚀 Features

- **Ask Anything:** Get instant answers to your data questions.
- **Automated Analysis:** Perform calculations, summaries, and more.
- **Visual Results:** Receive charts and plots as base64 images.
- **Powered by gpt-4.1-mini & LangChain:** Advanced NLP for accurate, context-aware responses.

## 🛠️ Tech Stack

- Python
- OpenAI Chat GPT
- LangChain

## 💡 Usage

1. Clone the repo  
2. Install requirements  
3. Run the agent and start asking questions!
4. curl "http://127.0.0.1:8000/api/" \
     -F "questions.txt=@question1.txt" \
     -F "data.csv=@irs.csv"
5. This API accept multiple files main file is question so there we can give idea to agent how to use additional attached files during the analytics task
---

Give it a try and supercharge your data analytics!
