# test_mongodb.py - Quick MongoDB verification
from src.db import jobs_col, candidates_col, results_col, db

print("🔍 Testing MongoDB connection...\n")

# Check connection
try:
    collections = db.list_collection_names()
    print(f"✅ Connected to MongoDB!")
    print(f"   Collections in 'hirelens' database: {collections}\n")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

# Test collection access
print("📊 Collection Status:")
try:
    jobs_count = jobs_col.count_documents({})
    candidates_count = candidates_col.count_documents({})
    results_count = results_col.count_documents({})
    
    print(f"   - jobs: {jobs_count} documents")
    print(f"   - candidates: {candidates_count} documents")
    print(f"   - screening_results: {results_count} documents\n")
    
    # Show sample
    if results_count > 0:
        latest_result = results_col.find_one(sort=[("_id", -1)])
        print(f"✨ Latest screening result:")
        print(f"   - Job: {latest_result.get('job', {}).get('title')}")
        print(f"   - Timestamp: {latest_result.get('timestamp')}")
        print(f"   - Shortlist size: {len(latest_result.get('shortlist', []))}")
    
    print(f"\n✅ All systems ready!")
except Exception as e:
    print(f"❌ Collection error: {e}")