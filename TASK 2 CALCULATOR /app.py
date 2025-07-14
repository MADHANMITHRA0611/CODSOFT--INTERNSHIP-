from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        expr = request.json['expression']

        # Safe evaluation context
        allowed_names = {}
        allowed_names.update(math.__dict__)
        allowed_names.update({
            'abs': abs,
            'pow': pow,
            'round': round
        })

        result = eval(expr, {"__builtins__": {}}, allowed_names)
        return jsonify({'result': result})
    except Exception:
        return jsonify({'error': 'Invalid Expression'})

if __name__ == '__main__':
    app.run(debug=True)
