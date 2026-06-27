import os
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from main import run_simulation

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Path to the generated graphics and PDF
GRAPHICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'relatorio_graficos')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        # Run the simulation synchronously (in a real world scenario this could be async/celery)
        results = run_simulation()
        return jsonify({
            "status": "success",
            "data": results
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route('/api/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(GRAPHICS_DIR, filename)

if __name__ == '__main__':
    # Run the server on port 5001
    app.run(debug=True, port=5001)
