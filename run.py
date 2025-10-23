#!/usr/bin/env python3
"""
Pesti-Link Flask Application Runner
Connecting Farmers with Pesticide Shops
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("📝 Please copy env_example.txt to .env and configure your MongoDB URI")
        print("🔗 Get your MongoDB Atlas connection string from: https://www.mongodb.com/atlas")
        print()
    
    # Check if MongoDB URI is configured
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri or mongo_uri == 'mongodb://localhost:27017/pesti_link':
        print("⚠️  Warning: MongoDB URI not configured!")
        print("📝 Please set MONGO_URI in your .env file")
        print("🔗 Example: MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pesti_link")
        print()
    
    print("🌱 Starting Pesti-Link Application...")
    print("🌐 Application will be available at: http://localhost:5000")
    print("📚 Documentation: See README.md for setup instructions")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure MongoDB is accessible and credentials are correct")
        sys.exit(1)
