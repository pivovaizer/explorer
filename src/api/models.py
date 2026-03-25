from sqlalchemy import BigInteger, Boolean, LargeBinary, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.api.database import DataBase


class Block(DataBase):
    __tablename__ = "blocks"

    height: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    header_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True, nullable=False)
    prev_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_transaction_block: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Coin(DataBase):
    __tablename__ = "coins"

    coin_id: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    puzzle_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    parent_coin_id: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    spent_height: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    coinbase: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BlockTxDetails(DataBase):
    __tablename__ = "block_tx_details"

    height: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    header_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
