import os
from dotenv import load_dotenv
from src.app.app import create_app
from src.config.database import init_db

load_dotenv()

PORT = int(os.getenv('PORT', 3002))

if __name__ == '__main__':
    try:
        # Inicializar PostgreSQL
        init_db()
        print('✅ Database connected (Appointments)')
        
        # Crear y ejecutar app
        app = create_app()
        print(f'🚀 Appointment Service running on port {PORT}')
        app.run(host='0.0.0.0', port=PORT, debug=True)
    except Exception as e:
        print(f'Error starting server: {e}')
        exit(1)