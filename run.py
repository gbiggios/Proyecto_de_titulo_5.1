from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Configura el puerto dinámico para Render o usa el 5000 como predeterminado para desarrollo local
    port = int(os.environ.get("PORT", 5000))
    
    # Elimina debug=True para producción; úsalo solo en desarrollo
    app.run(host="0.0.0.0", port=port, debug=False)
