from app import app
import os
import logging

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
