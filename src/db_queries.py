# src/db_queries.py - Useful MongoDB queries
from src.db import jobs_col, candidates_col, results_col
from datetime import datetime, timedelta

class DatabaseQueries:
    """Helper methods for common MongoDB queries."""
    
    @staticmethod
    def get_latest_screening_results(limit=5):
        """Get most recent screening runs."""
        return list(results_col.find({}).sort("_id", -1).limit(limit))
    
    @staticmethod
    def get_screening_results_by_job(job_id: str):
        """Get all screening results for a specific job."""
        return list(results_col.find({"job.jobId": job_id}).sort("timestamp", -1))
    
    @staticmethod
    def get_candidate_by_name(first_name: str, last_name: str):
        """Find candidate by name."""
        return candidates_col.find_one({
            "firstName": first_name,
            "lastName": last_name
        })
    
    @staticmethod
    def get_top_candidates_from_run(run_id: str, limit=10):
        """Get top N candidates from a screening run."""
        result = results_col.find_one({"screeningRunId": run_id})
        if result:
            return result.get("shortlist", [])[:limit]
        return []
    
    @staticmethod
    def clear_test_data():
        """Clear all collections (for testing only!)"""
        jobs_col.delete_many({})
        candidates_col.delete_many({})
        results_col.delete_many({})
        print("🗑️  All collections cleared!")