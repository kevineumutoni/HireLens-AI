"""
Basic test for the CandidateMatcher service.
Run with: python -m pytest tests/test_matcher.py -v
"""
import pytest
import asyncio
from src.services.matcher import CandidateMatcher
from tests.dummy_data import get_sample_job, get_strong_match_candidate, get_weak_match_candidate


@pytest.mark.asyncio
async def test_matcher_strong_candidate():
    """Test that a strong candidate gets a high score."""
    matcher = CandidateMatcher()
    job = get_sample_job()
    candidate = get_strong_match_candidate()
    
    result = await matcher.match_candidate(job, candidate)
    
    # Assertions
    assert "matchScore" in result
    assert 0 <= result["matchScore"] <= 100
    assert isinstance(result["strengths"], list)
    assert isinstance(result["gaps"], list)
    assert "recommendation" in result
    assert result["matchScore"] >= 75  # Strong candidate should score high
    print(f"✓ Strong match test passed: Score={result['matchScore']}")


@pytest.mark.asyncio  
async def test_matcher_weak_candidate():
    """Test that a weak candidate gets a lower score."""
    matcher = CandidateMatcher()
    job = get_sample_job()
    candidate = get_weak_match_candidate()
    
    result = await matcher.match_candidate(job, candidate)
    
    # Assertions
    assert 0 <= result["matchScore"] <= 100
    assert result["matchScore"] <= 60  # Weak candidate should score lower
    print(f"✓ Weak match test passed: Score={result['matchScore']}")


if __name__ == "__main__":
    # Run tests directly (for quick local testing)
    asyncio.run(test_matcher_strong_candidate())
    asyncio.run(test_matcher_weak_candidate())
    print("✅ All matcher tests passed!")