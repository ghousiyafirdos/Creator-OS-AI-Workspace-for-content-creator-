"""
CreatorOS - Main Entry Point
Run this script to launch the Flask development server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("CreatorOS - AI Workspace for Content Creators")
    print("Environment Setup Complete (Phase 1)")
    print("Server running on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=False)
