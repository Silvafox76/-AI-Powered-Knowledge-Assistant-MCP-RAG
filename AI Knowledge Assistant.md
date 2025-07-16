# AI Knowledge Assistant

A production-ready AI-powered knowledge assistant built on 1400+ professional certifications, notes, lessons learned, and frameworks in program, project, and product management.

## Features

### 🧠 Dual AI Modes
- **RAG (Retrieval-Augmented Generation)**: Query your knowledge base with semantic search
- **MCP (Multi-agent Conversational Programming)**: Specialized agents for different domains

### 🔒 Security & Authentication
- JWT-based authentication system
- Role-based access control
- Secure file upload and processing
- Environment-based configuration

### 📚 Document Processing
- Support for multiple file formats: PDF, DOCX, PPTX, TXT, CSV, MD
- Intelligent text chunking and metadata extraction
- Vector embeddings with ChromaDB
- Web content ingestion

### 🤖 Specialized Agents
- **PRINCE2 Agent**: PRINCE2 methodology specialist
- **Agile Agent**: Scrum and Agile practices expert
- **ITIL Agent**: Service management specialist
- **AI Strategy Agent**: Digital transformation expert
- **PMBOK Agent**: Traditional project management
- **General PM Agent**: Cross-methodology guidance

### 🎨 Modern Frontend
- React-based responsive interface
- Real-time query processing
- File upload with drag-and-drop
- Agent selection and management
- Dashboard with analytics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   ChromaDB      │
│                 │    │                 │    │   Vector Store  │
│ • Query Interface│◄──►│ • RAG Engine    │◄──►│                 │
│ • File Upload   │    │ • MCP Agents    │    │ • Embeddings    │
│ • Dashboard     │    │ • Authentication│    │ • Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite Auth   │
                       │   Database      │
                       └─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_knowledge_assistant
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Installation

1. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start backend
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend Setup**
   ```bash
   # In a new terminal
   cd frontend
   npm install
   npm run dev
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
CHROMA_DB_PATH=./chroma_db
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*

# Production Settings
ENVIRONMENT=development
DEBUG=true
```

### Default Credentials

The system creates a default admin user:
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default password in production!

## Usage

### 1. Authentication

First, log in to get an access token:

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```

### 2. Upload Documents

```bash
curl -X POST "http://localhost:8000/ingest/file" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@document.pdf"
```

### 3. Query Knowledge Base

**RAG Query:**
```bash
curl -X POST "http://localhost:8000/query/rag" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are PRINCE2 principles?", "mode": "rag"}'
```

**MCP Agent Query:**
```bash
curl -X POST "http://localhost:8000/query/mcp" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "Compare Agile and Waterfall", "mode": "mcp", "agent_type": "agile"}'
```

### 4. Get Statistics

```bash
curl -X GET "http://localhost:8000/stats" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## File Structure

```
ai_knowledge_assistant/
├── backend/                 # FastAPI backend
│   ├── auth.py             # Authentication system
│   ├── main.py             # Main FastAPI application
│   ├── ingestion/          # Document processing
│   │   ├── ingestion_manager.py
│   │   ├── pdf_ingestion.py
│   │   ├── pptx_ingestion.py
│   │   ├── text_ingestion.py
│   │   ├── csv_ingestion.py
│   │   └── web_ingestion.py
│   └── mcp/                # Multi-agent system
│       ├── agents.py       # Specialized agents
│       └── crew_manager.py # Agent orchestration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main application
│   │   └── components/    # UI components
│   └── package.json
├── chroma_db/             # Vector database
├── data/                  # Document storage
├── logs/                  # Application logs
├── .env                   # Environment configuration
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-service deployment
└── README.md             # This file
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Format code
black backend/
flake8 backend/

# Type checking
mypy backend/
```

### Adding New Agents

1. Create agent class in `backend/mcp/agents.py`
2. Add agent to `CrewManager` in `backend/mcp/crew_manager.py`
3. Update routing keywords for automatic agent selection

### Adding New Document Types

1. Create ingestion module in `backend/ingestion/`
2. Add to `IngestionManager` in `backend/ingestion/ingestion_manager.py`
3. Update file type routing in main application

## Deployment

### Production Deployment

1. **Update environment variables**
   ```bash
   # Set production values
   ENVIRONMENT=production
   DEBUG=false
   JWT_SECRET_KEY=<strong-random-key>
   ```

2. **Use production Docker Compose**
   ```bash
   docker-compose --profile production up -d
   ```

3. **Set up SSL/TLS**
   - Configure nginx with SSL certificates
   - Update CORS origins for your domain

### Scaling Considerations

- **Database**: Consider PostgreSQL for larger deployments
- **Vector Store**: ChromaDB supports clustering for scale
- **Load Balancing**: Use nginx or cloud load balancers
- **Caching**: Implement Redis for query caching
- **Monitoring**: Add Prometheus/Grafana for observability

## Security

### Best Practices

1. **Change default credentials** immediately
2. **Use strong JWT secrets** (32+ characters)
3. **Enable HTTPS** in production
4. **Restrict CORS origins** to your domains
5. **Regular security updates** for dependencies
6. **Monitor access logs** for suspicious activity

### Rate Limiting

The application includes built-in rate limiting:
- 60 requests per minute per user
- Burst capacity of 10 requests

## Troubleshooting

### Common Issues

1. **ChromaDB Permission Errors**
   ```bash
   sudo chown -R $USER:$USER chroma_db/
   ```

2. **Port Already in Use**
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

3. **Memory Issues with Large Documents**
   - Increase Docker memory limits
   - Adjust chunk sizes in ingestion settings

### Logs

Check application logs:
```bash
# Docker logs
docker-compose logs -f backend

# Local logs
tail -f logs/app.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/docs` or `/redoc`

## Roadmap

### Upcoming Features

- [ ] Integration with external knowledge sources
- [ ] Advanced analytics and reporting
- [ ] Mobile application
- [ ] Voice interface
- [ ] Multi-language support
- [ ] Advanced role-based permissions
- [ ] Integration with Slack/Teams
- [ ] Automated document synchronization
- [ ] Custom agent training
- [ ] Enterprise SSO integration

---

**Built with ❤️ for project management professionals**

