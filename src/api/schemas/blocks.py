from pydantic import BaseModel, ConfigDict, Field


class BlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    height: int
    header_hash: str
    prev_hash: str
    timestamp: int
    is_transaction_block: bool


