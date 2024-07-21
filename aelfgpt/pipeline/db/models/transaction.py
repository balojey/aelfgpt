from typing import List
from pipeline.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Integer, ARRAY


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(primary_key=True)
    block_hash: Mapped[str] = mapped_column(String())
    error: Mapped[str | None] = mapped_column(String())
    return_value: Mapped[str] = mapped_column(String())
    status: Mapped[str] = mapped_column(String())
    transaction_from: Mapped[str] = mapped_column(String())
    method_name: Mapped[str] = mapped_column(String())
    method_params: Mapped[dict] = mapped_column(JSON())
    ref_block_number: Mapped[str] = mapped_column(Integer())
    ref_block_prefix: Mapped[str] = mapped_column(String())
    signature: Mapped[str] = mapped_column(String())
    transaction_to: Mapped[str] = mapped_column(String())
    transaction_size: Mapped[str] = mapped_column(Integer())
    logs: Mapped[List] = mapped_column(ARRAY(JSON))
