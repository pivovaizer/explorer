from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.models import Coin
from src.utils.bech32m import decode_puzzle_hash
from src.api.schemas.addresses import AddressResponse, CoinResponse, HistoryResponse


router = APIRouter(prefix="/addresses", tags=["addresses"])


def _parse_puzzle_hash(puzzle_hash: str) -> bytes:
    """Accept hex puzzle_hash, return bytes."""
    try:
        if puzzle_hash.startswith("xch1"):
            ph_bytes = decode_puzzle_hash(puzzle_hash)
        else:
            ph_bytes = bytes.fromhex(puzzle_hash)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid address or puzzle_hash")
    if len(ph_bytes) != 32:
        raise HTTPException(status_code=400, detail="puzzle_hash must be 32 bytes (64 hex chars)")
    return ph_bytes


def _coin_to_response(coin: Coin) -> CoinResponse:
    return CoinResponse(
        coin_id=coin.coin_id.hex(),
        puzzle_hash=coin.puzzle_hash.hex(),
        amount_mojo=coin.amount,
        created_height=coin.created_height,
        spent_height=coin.spent_height,
        coinbase=coin.coinbase,
    )


@router.get("/balance/{address}", response_model=AddressResponse)
async def get_address_balance(address: str, db: AsyncSession = Depends(get_db)):
    ph_bytes = _parse_puzzle_hash(address)
    result = await db.execute(
        select(func.coalesce(func.sum(Coin.amount), 0))
        .where(Coin.puzzle_hash == ph_bytes, Coin.spent_height.is_(None))
    )
    balance = result.scalar_one()
    return AddressResponse(puzzle_hash=address, balance_mojo=balance)


@router.get("/utxos/{address}", response_model=list[CoinResponse])
async def get_address_utxos(
    address: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    ph_bytes = _parse_puzzle_hash(address)
    result = await db.execute(
        select(Coin)
        .where(Coin.puzzle_hash == ph_bytes, Coin.spent_height.is_(None))
        .order_by(Coin.created_height)
        .limit(limit)
        .offset(offset)
    )
    coins = result.scalars().all()
    return [_coin_to_response(c) for c in coins]


@router.get("/history/{address}", response_model=HistoryResponse)
async def get_address_history(
    address: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    ph_bytes = _parse_puzzle_hash(address)

    count_result = await db.execute(
        select(func.count()).select_from(Coin).where(Coin.puzzle_hash == ph_bytes)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Coin)
        .where(Coin.puzzle_hash == ph_bytes)
        .order_by(Coin.created_height)
        .limit(limit)
        .offset(offset)
    )
    coins = result.scalars().all()

    return HistoryResponse(
        items=[_coin_to_response(c) for c in coins],
        total=total,
        limit=limit,
        offset=offset,
    )
