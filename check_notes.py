from backend.database import get_db
from backend.models import ProcessRecord

# Get database session
db = next(get_db())

# Query recent process records
records = db.query(ProcessRecord).order_by(ProcessRecord.id.desc()).limit(5).all()

# Print records with notes
print("Recent process records with notes:")
print("-" * 50)
for record in records:
    print(f"ID: {record.id}")
    print(f"Notes: {record.notes}")
    print(f"Machine ID: {record.machine_id}")
    print(f"Product ID: {record.product_id}")
    print(f"Record time: {record.record_time}")
    print("-" * 50)