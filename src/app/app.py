from flask import Flask, jsonify
from flask_cors import CORS
from src.routes.appointment_routes import appointment_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'OK', 'service': 'appointment-service'}), 200
    
    @app.errorhandler(Exception)
    def handle_error(error):
        print(f'Error: {error}')
        status = getattr(error, 'status', 500)
        code = getattr(error, 'code', 'INTERNAL_ERROR')
        message = str(error) or 'Error interno del servidor'
        
        return jsonify({
            'error': True,
            'message': message,
            'code': code
        }), status
    
    return app