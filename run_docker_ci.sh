#!/bin/bash

echo "🐳 Running CI/CD with Docker..."
echo "==============================="

# Stop any running containers
docker-compose down

# Build and run the pipeline
echo "📋 Building Docker image..."
docker-compose build

echo "📋 Starting services..."
docker-compose up -d postgres

# Wait for database to be ready
echo "📋 Waiting for database to be ready..."
sleep 10

# Run the dbt pipeline
echo "📋 Running dbt pipeline..."
docker-compose run --rm dbt-pipeline

echo "✅ Docker CI/CD Pipeline completed!"
echo "📊 Check logs with: docker-compose logs"
