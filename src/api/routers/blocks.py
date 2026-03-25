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


@router.get("/last_block", response_model=BlockResponse)
async def get_last_block(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Block).order_by(Block.height.desc()).limit(1)
    )
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="No blocks found")
    return _block_to_response(block)


@router.get("/block_info/{block_height}", response_model=BlockResponse)
async def get_block_info(block_height: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Block).where(Block.height == block_height))
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return _block_to_response(block)


@router.get("/transactions/{block_height}")  # TODO: add response model
async def get_block_transactions(block_height: int, db: AsyncSession = Depends(get_db)):
    # TODO: implement — return coins created/spent at this block height
    return {"block_height": block_height, "transactions": []}


@router.get("/hash/{block_hash}", response_model=BlockResponse)
async def get_block_by_hash(block_hash: str, db: AsyncSession = Depends(get_db)):
    hash_bytes = bytes.fromhex(block_hash)
    result = await db.execute(select(Block).where(Block.header_hash == hash_bytes))
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return _block_to_response(block)
