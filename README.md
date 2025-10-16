<<<<<<< HEAD
<<<<<<< HEAD
# Dbt_project_with_cicd
=======
# dbt Project 2 - Data Pipeline with Soda Data Quality
=======
# 🚀 DBT + Soda Data Pipeline with CI/CD
>>>>>>> 27aed56 (Initial commit with dbt and CI/CD setup)

Complete data pipeline with dbt transformations, Soda data quality validation, and automated CI/CD.

## 🎯 Quick Start

### Single Command Test Everything:
```bash
./run_tests.sh
```

### Python Test Suite:
```bash
python test_all.py
```

## 📊 Project Structure

```
dbt_project_2/
├── models/
│   ├── steging/           # Staging models
│   │   ├── stg_customers.sql
│   │   └── stg_transactions.sql
│   ├── marts/             # Mart models
│   │   ├── dim_customers.sql
│   │   ├── fact_transactions.sql
│   │   └── schema.yml
│   └── sources.yml        # Source definitions
├── soda_project/          # Data quality checks
│   ├── configuration.yml  # Database connection
│   └── checks/checks.yml  # Quality validation rules
├── .github/workflows/     # CI/CD pipeline
├── test_all.py           # Complete test suite
├── save_validation_results.py # Results storage
├── run_tests.sh          # Simple run script
└── requirements.txt      # Dependencies
```

## 🧪 Testing

### 1. Simple Test (Recommended):
```bash
./run_tests.sh
```

### 2. Python Test Suite:
```bash
python test_all.py
```

### 3. Individual Components:
```bash
# dbt tests
dbt debug && dbt compile && dbt test && dbt run

# Soda data quality
cd soda_project && soda scan -d postgres -c configuration.yml checks/checks.yml

# Save results
python save_validation_results.py
```

## 📧 Email Configuration

### Setup Email Notifications:
```bash
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password
export RECIPIENT_EMAIL=recipient@gmail.com
```

### For Gmail:
1. Enable 2-factor authentication
2. Generate App Password
3. Use App Password (not regular password)

## 🔄 CI/CD Pipeline

### GitHub Actions:
- **Trigger**: Push to main/develop branches
- **Tests**: dbt + Soda validation
- **Deploy**: Production deployment on main
- **Notifications**: Email alerts on completion

### Setup GitHub Secrets:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com
```

## 📊 Data Models

### Staging Layer:
- `stg_customers`: Cleaned customer data
- `stg_transactions`: Processed transaction data

### Mart Layer:
- `dim_customers`: Customer dimension (deduped)
- `fact_transactions`: Transaction fact (incremental)

## 🔍 Data Quality Checks

### Soda Validations:
- ✅ Row count validation
- ✅ Missing value detection
- ✅ Duplicate identification
- ✅ Invalid value detection
- ✅ Data freshness monitoring

## 🗄️ Database Schema

### Validation Tables:
- `dbt_run_results`: dbt execution results
- `soda_scan_results`: Data quality check results
- `soda_metrics`: Metric values
- `validation_summary`: Aggregated validation metrics

## 🚀 Deployment

### Docker:
```bash
docker-compose up -d
```

### Local:
```bash
source myenv/bin/activate
./run_tests.sh
```

## 📈 Monitoring

### Check Results:
```sql
-- Latest validation summary
SELECT * FROM validation_summary 
ORDER BY validation_timestamp DESC;

-- Failed checks
SELECT * FROM soda_scan_results 
WHERE check_status = 'FAILED' 
ORDER BY scan_timestamp DESC;
```

## 🛠️ Troubleshooting

### Common Issues:
1. **Database Connection**: Check PostgreSQL is running
2. **Email Not Sent**: Verify email credentials
3. **dbt Errors**: Run `dbt debug` to check configuration
4. **Soda Issues**: Check `configuration.yml` settings

### Logs:
- dbt logs: `logs/`
- Test results: Console output
- Database: PostgreSQL tables

## 📝 Environment Variables

```bash
# Database
DB_HOST=172.17.0.3
DB_USER=admin
DB_PASSWORD=admin
DB_NAME=test_db
DB_SCHEMA=public
DB_PORT=5432

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com
```

## 🎯 Features

- ✅ **Complete dbt Pipeline**: Staging → Marts
- ✅ **Data Quality**: Soda validation
- ✅ **CI/CD**: GitHub Actions automation
- ✅ **Email Notifications**: Test result alerts
- ✅ **Database Storage**: Validation results tracking
- ✅ **Docker Support**: Containerized deployment
- ✅ **Simple Commands**: One-command testing

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review database validation tables
3. Check email configuration
4. Verify database connectivity

---

<<<<<<< HEAD
## License

This project is licensed under the MIT License.
>>>>>>> 5952d8e (Initial commit: Complete dbt project with CI/CD setup)
=======
**🎉 Ready to use! Run `./run_tests.sh` to test everything!**
>>>>>>> 27aed56 (Initial commit with dbt and CI/CD setup)
