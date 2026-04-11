"""
General utility functions used across the AI module.
"""
import asyncio
from typing import List, Callable, Any


async def process_in_batches(
    items: List[Any], 
    processor: Callable, 
    batch_size: int,
    **kwargs
) -> List[Any]:
    """Process a list of items in batches to avoid API rate limits."""
    results = [None] * len(items)
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        tasks = [processor(item, **kwargs) for item in batch]
        batch_results = await asyncio.gather(*tasks)
        
        for j, result in enumerate(batch_results):
            results[i + j] = result
            
        if i + batch_size < len(items):
            await asyncio.sleep(0.5)
    
    return results