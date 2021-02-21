from core.config import settings

DB_CONFIG = {
    "connections": {
        "default": settings.DATABASE_URI
    },
    "apps": {
        "models": {
            "models": settings.MODELS
        }
    }
}
