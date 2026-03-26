from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.models import Block, Coin
from src.api.schemas.blocks import BlockResponse, BlockInfoResponse, LastBlockResponse
from src.utils.bech32m import encode_puzzle_hash


router = APIRouter(prefix="/blocks", tags=["blocks"])


def _block_to_response(block: Block) -> BlockResponse:
    return BlockResponse(
        height=block.height,
        header_hash=block.header_hash.hex(),
        prev_hash=block.prev_hash.hex(),
        timestamp=block.timestamp,
        is_transaction_block=block.is_transaction_block,
    )


def _coin_to_dict(coin: Coin) -> dict:
    return {
        "coin_id": coin.coin_id.hex(),
        "puzzle_hash": coin.puzzle_hash.hex(),
        "parent_coin_id": coin.parent_coin_id.hex(),
        "amount": coin.amount,
        "created_height": coin.created_height,
        "spent_height": coin.spent_height,
        "coinbase": coin.coinbase,
    }


@router.get("/last_block", response_model=LastBlockResponse)
async def get_last_block(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Block).order_by(Block.height.desc()).limit(1)
    )
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="No blocks found")

    # coinbase rewards
    rewards_result = await db.execute(
        select(Coin).where(Coin.coinbase == True, Coin.created_height == block.height)
    )
    rewards = rewards_result.scalars().all()

    # transferred amount (non-coinbase)
    transferred_result = await db.execute(
        select(func.coalesce(func.sum(Coin.amount), 0))
        .where(Coin.created_height == block.height, Coin.coinbase == False)
    )
    transferred_amount = transferred_result.scalar_one()

    farmer_address = None
    pool_address = None
    farmer_amount = 0
    pool_amount = 0
    total_reward = 0

    if rewards:
        rewards_sorted = sorted(rewards, key=lambda c: c.amount)
        farmer_coin = rewards_sorted[0]
        farmer_address = encode_puzzle_hash(farmer_coin.puzzle_hash)
        farmer_amount = farmer_coin.amount

        if len(rewards_sorted) > 1:
            pool_coin = rewards_sorted[-1]
            pool_address = encode_puzzle_hash(pool_coin.puzzle_hash)
            pool_amount = pool_coin.amount

        total_reward = sum(c.amount for c in rewards)

    MOJO_PER_XCH = 1_000_000_000_000

    return LastBlockResponse(
        number=block.height,
        hash=block.header_hash.hex(),
        type="Transaction block" if block.is_transaction_block else "Non Transaction block",
        timestamp=block.timestamp if block.timestamp > 0 else None,
        farmer_address=farmer_address,
        pool_address=pool_address,
        block_reward=total_reward / MOJO_PER_XCH,
        pool_amount=pool_amount / MOJO_PER_XCH,
        farmer_amount=farmer_amount / MOJO_PER_XCH,
        transferred_amount=transferred_amount / MOJO_PER_XCH,
    )


@router.get("/block_info/{block_height}", response_model=BlockInfoResponse)
async def get_block_info(block_height: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Block).where(Block.height == block_height))
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    # coinbase rewards
    rewards_result = await db.execute(
        select(Coin).where(Coin.coinbase == True, Coin.created_height == block_height)
    )
    rewards = rewards_result.scalars().all()

    # counts
    addition_result = await db.execute(
        select(func.count()).select_from(Coin).where(Coin.created_height == block_height, Coin.coinbase == False)
    )
    addition_count = addition_result.scalar_one()

    removal_result = await db.execute(
        select(func.count()).select_from(Coin).where(Coin.spent_height == block_height)
    )
    removal_count = removal_result.scalar_one()

    # transferred amount (non-coinbase created coins)
    transferred_result = await db.execute(
        select(func.coalesce(func.sum(Coin.amount), 0))
        .where(Coin.created_height == block_height, Coin.coinbase == False)
    )
    transferred_amount = transferred_result.scalar_one()

    # parse rewards: larger = pool (7/8), smaller = farmer (1/8)
    farmer_address = None
    pool_address = None
    farmer_amount = 0
    pool_amount = 0
    total_reward = 0

    if rewards:
        rewards_sorted = sorted(rewards, key=lambda c: c.amount)
        farmer_coin = rewards_sorted[0]
        farmer_address = encode_puzzle_hash(farmer_coin.puzzle_hash)
        farmer_amount = farmer_coin.amount

        if len(rewards_sorted) > 1:
            pool_coin = rewards_sorted[-1]
            pool_address = encode_puzzle_hash(pool_coin.puzzle_hash)
            pool_amount = pool_coin.amount

        total_reward = sum(c.amount for c in rewards)

    MOJO_PER_XCH = 1_000_000_000_000

    return BlockInfoResponse(
        number=block.height,
        hash=block.header_hash.hex(),
        type="Transaction block" if block.is_transaction_block else "Non Transaction block",
        timestamp=block.timestamp if block.timestamp > 0 else None,
        farmer_address=farmer_address,
        pool_address=pool_address,
        block_reward=total_reward / MOJO_PER_XCH,
        pool_amount=pool_amount / MOJO_PER_XCH,
        farmer_amount=farmer_amount / MOJO_PER_XCH,
        transferred_amount=transferred_amount / MOJO_PER_XCH,
        addition_count=addition_count,
        removal_count=removal_count,
        reward_count=len(rewards),
    )


@router.get("/transactions/{block_height}")
async def get_block_transactions(block_height: int, db: AsyncSession = Depends(get_db)):
    # TODO: add response model
    # TODO: classify coins by type (standard, dust, token/CAT, nft, did, dl)
    #       requires puzzle_hash analysis to detect coin type
    # TODO: add query params: include_dust, include_token, include_nft, include_did, include_dl
    create = await db.execute(
        select(Coin).where(Coin.created_height == block_height)
    )
    spent = await db.execute(
        select(Coin).where(Coin.spent_height == block_height)
    )
    return {
        "block_height": block_height,
        "created_coins": [_coin_to_dict(coin) for coin in create.scalars().all()],
        "spent_coins": [_coin_to_dict(coin) for coin in spent.scalars().all()],
    }


@router.get("/hash/{block_hash}", response_model=BlockResponse)
async def get_block_by_hash(block_hash: str, db: AsyncSession = Depends(get_db)):
    hash_bytes = bytes.fromhex(block_hash)
    result = await db.execute(select(Block).where(Block.header_hash == hash_bytes))
    block = result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return _block_to_response(block)
