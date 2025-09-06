from flask import Flask, request, jsonify
from flask_cors import CORS
from aiagent import FREDAgent

app = Flask(__name__)
CORS(app)  # 启用 CORS
agent = FREDAgent()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '')
    response = agent.answer(question)
    return jsonify(response)

if __name__ == '__main__':
    # 仅启动 Flask 服务，禁止其他逻辑干扰
    app.run(host='0.0.0.0', port=5000, debug=True)