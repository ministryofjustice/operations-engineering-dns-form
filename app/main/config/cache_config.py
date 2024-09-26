from flask_caching import Cache

cache = Cache()

def configure_cache(type: str, timeout: int, app):
    app.config['CACHE_TYPE'] = type
    app.config['CACHE_DEFAULT_TIMEOUT'] = timeout

    return cache.init_app(app)