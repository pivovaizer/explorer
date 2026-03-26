from pydantic import BaseModel, ConfigDict


class BlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    height: int
    header_hash: str
    prev_hash: str
    timestamp: int
    is_transaction_block: bool


class LastBlockResponse(BaseModel):
    number: int
    hash: str
    type: str
    timestamp: int | None
    farmer_address: str | None
    pool_address: str | None
    block_reward: float
    pool_amount: float
    farmer_amount: float
    transferred_amount: float


class BlockInfoResponse(BaseModel):
    number: int
    hash: str
    type: str
    timestamp: int | None
    farmer_address: str | None
    pool_address: str | None
    block_reward: float
    pool_amount: float
    farmer_amount: float
    transferred_amount: float
    addition_count: int
    removal_count: int
    reward_count: int
