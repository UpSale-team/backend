from ..providers import cacher, memory_cacher

def clear_cache_control():
    '''
    Clear cache.
    '''
    cacher.clear()