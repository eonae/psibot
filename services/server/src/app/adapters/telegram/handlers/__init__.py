from .router import router


def register_handlers(bot):
    """Регистрирует все обработчики для бота"""
    bot.include_router(router)


__all__ = ["router", "register_handlers"]
