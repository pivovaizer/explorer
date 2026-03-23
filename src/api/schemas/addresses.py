from pydantic import BaseModel, Field, ConfigDict

class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    puzzle_hash: str
    balance_mojo: int


class CoinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    coin_id: str
    puzzle_hash: str
    amount_mojo: int
    created_height: int
    spent_height: int | None
    coinbase: bool


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[CoinResponse]
    total: int
    limit: int
    offset: int
