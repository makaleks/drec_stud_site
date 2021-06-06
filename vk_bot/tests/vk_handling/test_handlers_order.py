import pytest


@pytest.mark.asyncio
@pytest.mark.unit
async def test_default_fallback_is_last_in_handlers_list():
    # GIVEN: prepared environment
    # WHEN: bot is build
    from src.bot import bot
    # THEN: default handler goes to the last of handlers' list
    all_handlers = bot.labeler.message_view.handlers
    position = None
    for i, handler in enumerate(all_handlers):
        if 'hello_admin' in str(handler):
            position = i
    assert position == len(all_handlers) - 1
