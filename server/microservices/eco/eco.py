from flask import Flask, request

app = Flask(__name__)

@app.route('/eco', methods=['POST'])
def eco_service():
    data = request.json
    return data

if __name__ == '__main__':
    app.run(debug=True)