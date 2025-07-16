# Deployment Guide

This guide provides step-by-step instructions for deploying the AI Knowledge Assistant in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd ai_knowledge_assistant
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize database**
   ```bash
   # The application will create the auth database automatically
   # Default admin user: admin/admin123
   ```

5. **Start backend**
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint**
   ```bash
   # Create .env.local
   echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
   ```

3. **Start frontend**
   ```bash
   npm run dev
   ```

### Verification

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Health check: http://localhost:8000/health

## Docker Deployment

### Single Container (Backend Only)

1. **Build image**
   ```bash
   docker build -t ai-knowledge-assistant .
   ```

2. **Run container**
   ```bash
   docker run -d \
     --name ai-knowledge-assistant \
     -p 8000:8000 \
     -v $(pwd)/chroma_db:/app/chroma_db \
     -v $(pwd)/data:/app/data \
     -e JWT_SECRET_KEY=your-secret-key \
     ai-knowledge-assistant
   ```

### Multi-Service with Docker Compose

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Start services**
   ```bash
   # Development
   docker-compose up -d
   
   # Production (with nginx)
   docker-compose --profile production up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Docker Compose Services

- **backend**: FastAPI application (port 8000)
- **frontend**: React application (port 3000)
- **ollama**: Local LLM service (port 11434)
- **nginx**: Reverse proxy (ports 80/443) - production only

## Cloud Deployment

### AWS Deployment

#### Option 1: ECS with Fargate

1. **Create ECR repository**
   ```bash
   aws ecr create-repository --repository-name ai-knowledge-assistant
   ```

2. **Build and push image**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag
   docker build -t ai-knowledge-assistant .
   docker tag ai-knowledge-assistant:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-knowledge-assistant:latest
   
   # Push
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-knowledge-assistant:latest
   ```

3. **Create ECS task definition**
   ```json
   {
     "family": "ai-knowledge-assistant",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "ai-knowledge-assistant",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-knowledge-assistant:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "ENVIRONMENT",
             "value": "production"
           },
           {
             "name": "JWT_SECRET_KEY",
             "value": "your-production-secret"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/ai-knowledge-assistant",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

4. **Create ECS service**
   ```bash
   aws ecs create-service \
     --cluster default \
     --service-name ai-knowledge-assistant \
     --task-definition ai-knowledge-assistant \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

#### Option 2: EC2 with Docker

1. **Launch EC2 instance**
   - AMI: Amazon Linux 2
   - Instance type: t3.medium or larger
   - Security group: Allow ports 22, 80, 443, 8000

2. **Install Docker**
   ```bash
   sudo yum update -y
   sudo yum install -y docker
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -a -G docker ec2-user
   ```

3. **Install Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. **Deploy application**
   ```bash
   git clone <repository-url>
   cd ai_knowledge_assistant
   cp .env.example .env
   # Edit .env with production values
   docker-compose --profile production up -d
   ```

### Google Cloud Platform

#### Cloud Run Deployment

1. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

2. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/ai-knowledge-assistant
   
   gcloud run deploy ai-knowledge-assistant \
     --image gcr.io/PROJECT-ID/ai-knowledge-assistant \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production,JWT_SECRET_KEY=your-secret
   ```

### Azure Container Instances

1. **Create resource group**
   ```bash
   az group create --name ai-knowledge-assistant --location eastus
   ```

2. **Deploy container**
   ```bash
   az container create \
     --resource-group ai-knowledge-assistant \
     --name ai-knowledge-assistant \
     --image ai-knowledge-assistant:latest \
     --dns-name-label ai-knowledge-assistant \
     --ports 8000 \
     --environment-variables ENVIRONMENT=production JWT_SECRET_KEY=your-secret
   ```

## Production Checklist

### Security

- [ ] Change default admin password
- [ ] Generate strong JWT secret key (32+ characters)
- [ ] Configure HTTPS/SSL certificates
- [ ] Restrict CORS origins to your domains
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure secure headers
- [ ] Set up monitoring and alerting

### Performance

- [ ] Configure resource limits (CPU/Memory)
- [ ] Set up load balancing
- [ ] Configure caching (Redis)
- [ ] Optimize database queries
- [ ] Set up CDN for static assets
- [ ] Configure log rotation
- [ ] Monitor performance metrics

### Reliability

- [ ] Set up health checks
- [ ] Configure auto-scaling
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerting
- [ ] Test disaster recovery
- [ ] Set up CI/CD pipeline
- [ ] Configure log aggregation

### Environment Configuration

```env
# Production .env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=<32-character-random-string>
JWT_EXPIRATION_HOURS=8

# Database
CHROMA_DB_PATH=/app/chroma_db

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_BURST=5
```

## Monitoring & Maintenance

### Health Monitoring

1. **Application health**
   ```bash
   curl -f http://your-domain/health
   ```

2. **Docker health**
   ```bash
   docker-compose ps
   docker-compose logs backend
   ```

3. **Resource usage**
   ```bash
   docker stats
   ```

### Log Management

1. **View logs**
   ```bash
   # Docker logs
   docker-compose logs -f backend
   
   # Application logs
   tail -f logs/app.log
   ```

2. **Log rotation**
   ```bash
   # Add to crontab
   0 0 * * * /usr/sbin/logrotate /etc/logrotate.d/ai-knowledge-assistant
   ```

### Backup Strategy

1. **Database backup**
   ```bash
   # Backup ChromaDB
   tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_db/
   
   # Backup auth database
   cp auth.db auth_backup_$(date +%Y%m%d).db
   ```

2. **Automated backups**
   ```bash
   #!/bin/bash
   # backup.sh
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/backups"
   
   # Create backup directory
   mkdir -p $BACKUP_DIR
   
   # Backup databases
   tar -czf $BACKUP_DIR/chroma_$DATE.tar.gz chroma_db/
   cp auth.db $BACKUP_DIR/auth_$DATE.db
   
   # Upload to cloud storage (optional)
   aws s3 cp $BACKUP_DIR/ s3://your-backup-bucket/ --recursive
   
   # Clean old backups (keep 30 days)
   find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
   find $BACKUP_DIR -name "*.db" -mtime +30 -delete
   ```

### Updates and Maintenance

1. **Update application**
   ```bash
   # Pull latest code
   git pull origin main
   
   # Rebuild and restart
   docker-compose build
   docker-compose up -d
   ```

2. **Update dependencies**
   ```bash
   # Update Python packages
   pip install -r requirements.txt --upgrade
   
   # Update Node packages
   cd frontend && npm update
   ```

3. **Database maintenance**
   ```bash
   # Optimize ChromaDB (if needed)
   # This is typically handled automatically
   ```

### Troubleshooting

#### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Check configuration
   docker-compose config
   
   # Restart services
   docker-compose restart
   ```

2. **Database connection errors**
   ```bash
   # Check permissions
   ls -la chroma_db/
   
   # Fix permissions
   sudo chown -R $USER:$USER chroma_db/
   ```

3. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   ```

4. **Authentication issues**
   ```bash
   # Reset admin password
   # Connect to container and run Python script to reset password
   ```

#### Performance Tuning

1. **Database optimization**
   - Monitor query performance
   - Adjust chunk sizes for documents
   - Consider database sharding for large datasets

2. **Memory optimization**
   - Adjust embedding model size
   - Configure garbage collection
   - Monitor memory leaks

3. **Network optimization**
   - Use CDN for static assets
   - Enable gzip compression
   - Optimize API response sizes

## Support

For deployment issues:
1. Check the logs first
2. Review the troubleshooting section
3. Create an issue with deployment details
4. Include environment information and error messages

---

**Happy Deploying! 🚀**

