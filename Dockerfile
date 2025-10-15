FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy dbt project files
COPY . .

# Create dbt profiles directory
RUN mkdir -p ~/.dbt

# Set environment variables
ENV DBT_PROFILES_DIR=~/.dbt
ENV PYTHONPATH=/app

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database to be ready\n\
until pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do\n\
  echo "Waiting for database..."\n\
  sleep 2\n\
done\n\
\n\
# Run dbt commands\n\
echo "Running dbt debug..."\n\
dbt debug\n\
\n\
echo "Running dbt compile..."\n\
dbt compile\n\
\n\
echo "Running dbt test..."\n\
dbt test\n\
\n\
echo "Running dbt run..."\n\
dbt run\n\
\n\
echo "Running Soda data quality checks..."\n\
cd soda_project\n\
soda scan -d postgres -c configuration.yml checks/checks.yml || true\n\
\n\
echo "Saving validation results..."\n\
cd ..\n\
python save_validation_results.py\n\
\n\
echo "Pipeline completed successfully!"\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
