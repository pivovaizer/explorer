from fastapi import APIRouter

from src.api.schemas.addresses import AddressResponse, CoinResponse, HistoryResponse


router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("/{puzzle_hash}/balance", response_model=AddressResponse)
async def get_address_balance(puzzle_hash: str):
     # TODO: USE from database
     return AddressResponse(
        puzzle_hash=puzzle_hash,
        balance_mojo=10000000,
    )


@router.get("/{puzzle_hash}/utxos", response_model=list[CoinResponse])
async def get_address_utxos(puzzle_hash: str, limit: int = 20, offset: int = 0):
    # TODO: USE from database
    return [
        CoinResponse(
            coin_id=f"coin_{i}",
            puzzle_hash=puzzle_hash,
            amount_mojo=1000000,
            created_height=100 + i,
            spent_height=None,
            coinbase=False,
        )
        for i in range(offset, offset + limit)
    ]

@router.get("/{puzzle_hash}/history", response_model=HistoryResponse)
async def get_address_history(puzzle_hash: str):
    # TODO: USE from database
    return HistoryResponse(
        items=[],
        total=0,
        limit=20,
        offset=0,
    )




    