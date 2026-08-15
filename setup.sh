#!/bin/bash
set -e

echo "🚀 Setting up AI-Powered Placement Intelligence & Career Preparation Platform"
echo ""

# Backend setup
echo "📦 Backend setup..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ Created backend/.env (edit if needed)"
fi
echo "✓ Backend dependencies installed"

# Run migrations
echo "🗄️  Running database migrations..."
if ! alembic upgrade head 2>/dev/null; then
  echo "⚠️  Migrations failed — ensure PostgreSQL is running:"
  echo "   docker compose up -d"
  exit 1
fi
echo "✓ Database ready"

deactivate
cd ..

# Frontend setup
echo "📦 Frontend setup..."
cd frontend
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ Created frontend/.env"
fi
npm install --prefer-offline --no-audit > /dev/null 2>&1 || npm install
echo "✓ Frontend dependencies installed"
cd ..

echo ""
echo "✅ Setup complete! Next steps:"
echo ""
echo "1. Ensure PostgreSQL is running:"
echo "   docker compose up -d"
echo ""
echo "2. Ensure Ollama is running locally with Qwen2.5:"
echo "   ollama pull qwen2.5"
echo "   ollama serve"
echo ""
echo "3. Start the backend (in a new terminal):"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "4. Start the frontend (in another terminal):"
echo "   cd frontend && npm start"
echo ""
echo "5. Open http://localhost:3000 in your browser and register."
echo ""
