from fastapi import APIRouter

from src.api.schemas.blocks import BlockResponse


router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.get("/", response_model=list[BlockResponse])
async def get_blocks(
    start_ts: int | None = None,
    end_ts: int | None = None,
    limit: int = 20,
    offset: int = 0,
):  # TODO: USE from database
    return [
        BlockResponse(
            height=i,
            header_hash="a" * 64,
            prev_hash="b" * 64,
            timestamp=1234567890 + i,
            is_transaction_block=True,
        )
        for i in range(offset, offset + limit)
    ]


@router.get("/by_hash/{block_hash}", response_model=BlockResponse)
async def get_block_by_hash(block_hash: str):
     # TODO: USE from database
     return BlockResponse(
        height=0,
        header_hash="a" * 64,
        prev_hash="b" * 64,
        timestamp=1234567890,
        is_transaction_block=True,
    )


@router.get("/{height}", response_model=BlockResponse)
async def get_block(height: int):
    # TODO: USE from database
    return BlockResponse(
        height=height,
        header_hash="a" * 64,
        prev_hash="b" * 64,
        timestamp=1234567890,
        is_transaction_block=True,
    )





    