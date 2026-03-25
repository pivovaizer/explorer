from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.models import Block
from src.api.schemas.blocks import BlockResponse


router = APIRouter(prefix="/blocks", tags=["blocks"])


def _block_to_response(block: Block) -> BlockResponse:
    return BlockResponse(
        height=block.height,
        header_hash=block.header_hash.hex(),
        prev_hash=block.prev_hash.hex(),
        timestamp=block.timestamp,
        is_transaction_block=block.is_transaction_block,
    )


@router.get("/", response_model=list[BlockResponse])
async def get_blocks(
    start_ts: int | None = None,
    end_ts: int | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Block)
    if start_ts is not None:
        query = query.where(Block.timestamp >= start_ts)
    if end_ts is not None:
        query = query.where(Block.timestamp <= end_ts)
    query = query.order_by(Block.height.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    blocks = result.scalars().all()
    return [_block_to_response(b) for b in blocks]


@router.get("/by_hash/{block_hash}", response_model=BlockResponse)
async def get_block_by_hash(block_hash: str, db: AsyncSession = Depends(get_db)):
    hash_bytes = bytes.fromhex(block_hash)
    result = await db.execute(select(Block).where(Block.header_hash == hash_bytes))
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return _block_to_response(block)


@router.get("/{height}", response_model=BlockResponse)
async def get_block(height: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Block).where(Block.height == height))
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return _block_to_response(block)
