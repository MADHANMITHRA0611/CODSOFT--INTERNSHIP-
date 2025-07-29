from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
contacts = []

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    contact = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'notes': request.form.get('notes')
    }
    contacts.append(contact)
    return jsonify({'status': 'success'})

@app.route('/get_contacts')
def get_contacts():
    return jsonify(contacts)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
