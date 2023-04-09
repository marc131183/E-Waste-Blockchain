from flask import Flask, request

app = Flask(__name__)

@app.route('/message', methods=['POST'])
def receive_message():
    message = request.json.get('message')
    print(f'Received message: {message}')
    return 'Message received'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
