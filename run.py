import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    # Create and run the application
    app = create_app('development')
    
    print("\n" + "=" * 60)
    print("🩺 DIABETES PREDICTION APP")
    print("=" * 60)
    print("\n✅ Server is running!")
    print("🌐 Open your browser and visit: http://127.0.0.1:5000")
    print("\n📝 To stop the server, press CTRL+C")
    print("=" * 60 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
