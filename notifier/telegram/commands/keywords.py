from aiogram.filters import Command
from aiogram import types

from db.crud.user import get_user_by_user_id
from db.crud.user_keyword import upsert_user_keyword, get_user_all_keywords
from db.db import AsyncSessionLocal
from logs.logger import logger
from notifier.telegram.bot_config import (
    dp,
)


@dp.message(Command("add_keyword"))
async def add_keyword(message: types.Message):
    """Add or update a user keyword with a specified weight."""
    logger.info("-" * 60)
    user_id = message.from_user.id
    logger.info(
        f"User {user_id} invoked /add_keyword with text: {message.text!r}"
    )

    # Split text into exactly 3 parts: command, keyword, weight
    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.answer(
            "Usage: /add_keyword <keyword> <weight>\nBoth are required ❌"
        )
        return

    keyword = parts[1].lower()
    try:
        weight = int(parts[2])
    except ValueError:
        await message.answer("Weight must be an integer ❌")
        return

    async with AsyncSessionLocal() as session:
        # Check if user exists
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to add a keyword."
            )
            await message.answer("You are not registered yet ❌")
            return

        # Check if keyword already exists
        from db.crud.user_keyword import get_user_keyword

        existing_kw = await get_user_keyword(session, user.id, keyword)
        if existing_kw:
            # Update existing keyword
            existing_kw.weight = weight
            await session.flush()
            action = "updated"
        else:
            # Create new keyword
            await upsert_user_keyword(session, user.id, keyword, weight)
            action = "created"

        await session.commit()

    logger.info(
        f"User {user_id} {action} keyword '{keyword}' with weight {weight}"
    )
    await message.answer(
        f"Keyword '{keyword}' {action} with weight {weight} ✅"
    )


@dp.message(Command("list_keywords"))
async def list_keywords(message: types.Message):
    """List all keywords for the current user."""
    user_id = message.from_user.id
    logger.info("-" * 60)
    logger.info(f"User {user_id} invoked /list_keywords")

    async with AsyncSessionLocal() as session:
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to list keywords."
            )
            await message.answer("You are not registered yet ❌")
            return

        keywords = await get_user_all_keywords(session, user.id)

        if not keywords:
            await message.answer("You haven't added any keywords yet ❌")
            return

        reply = "Your keywords:\n"
        for kw in keywords:
            reply += f"- {kw.keyword} (weight: {kw.weight})\n"

        await message.answer(reply)


@dp.message(Command("remove_keyword"))
async def remove_keyword(message: types.Message):
    """Remove a keyword for the current user."""
    user_id = message.from_user.id
    logger.info("-" * 60)
    logger.info(
        f"User {user_id} invoked /remove_keyword with text: {message.text!r}"
    )

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /remove_keyword <keyword> ❌")
        return

    keyword = parts[1].lower()

    async with AsyncSessionLocal() as session:
        # Check if user exists
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to remove a keyword."
            )
            await message.answer("You are not registered yet ❌")
            return

        # Try to delete keyword
        from db.crud.user_keyword import delete_user_keyword

        deleted = await delete_user_keyword(session, user.id, keyword)

        if deleted:
            await session.commit()
            await message.answer(f"Keyword '{keyword}' removed ✅")
            logger.info(f"User {user_id} removed keyword '{keyword}'")
        else:
            await message.answer(f"Keyword '{keyword}' not found ❌")
            logger.info(
                f"User {user_id} tried to remove non-existent keyword '{keyword}'"
            )
