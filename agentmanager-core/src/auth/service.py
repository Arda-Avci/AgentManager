from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.keys import generate_api_key, hash_key, verify_key
from src.database.models import ApiKeyModel


class AuthService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_api_key(
        self, name: str, allowed_agent_ids: list[str] | None = None
    ) -> tuple[str, ApiKeyModel]:
        raw_key = generate_api_key()
        key_hash = hash_key(raw_key)
        model = ApiKeyModel(
            key_hash=key_hash,
            name=name,
            allowed_agent_ids=allowed_agent_ids or [],
            is_active=True,
        )
        self._session.add(model)
        await self._session.flush()
        return raw_key, model

    async def validate_api_key(self, key: str) -> ApiKeyModel | None:
        key_hash = hash_key(key)
        result = await self._session.execute(
            select(ApiKeyModel).where(
                ApiKeyModel.key_hash == key_hash,
                ApiKeyModel.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def create_device_pairing(self, name: str) -> tuple[str, ApiKeyModel]:
        raw_key = generate_api_key()
        key_hash = hash_key(raw_key)
        model = ApiKeyModel(
            key_hash=key_hash,
            name=name,
            device_name=name,
            is_active=False,
        )
        self._session.add(model)
        await self._session.flush()
        return raw_key, model

    async def confirm_device_pairing(self, token: str) -> ApiKeyModel | None:
        key_hash = hash_key(token)
        result = await self._session.execute(
            select(ApiKeyModel).where(
                ApiKeyModel.key_hash == key_hash,
                ApiKeyModel.is_active == False,
                ApiKeyModel.device_name.isnot(None),
            )
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_active = True
            await self._session.flush()
        return model

    async def list_keys(self) -> list[ApiKeyModel]:
        result = await self._session.execute(
            select(ApiKeyModel).order_by(ApiKeyModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_key(self, key_id: str) -> ApiKeyModel | None:
        return await self._session.get(ApiKeyModel, key_id)

    async def delete_key(self, key_id: str) -> bool:
        model = await self._session.get(ApiKeyModel, key_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
