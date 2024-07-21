# from typing import List
# from pipeline.db.base import Base
# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy import String, JSON, Integer, ARRAY


# class Transaction(Base):
#     __tablename__ = "transactions"

    # id: Mapped[str] = mapped_column(primary_key=True)
    # block_hash: Mapped[str] = mapped_column(String())
    # error: Mapped[str | None] = mapped_column(String())
    # return_value: Mapped[str] = mapped_column(String())
    # status: Mapped[str] = mapped_column(String())
    # transaction_from: Mapped[str] = mapped_column(String())
    # method_name: Mapped[str] = mapped_column(String())
    # method_params: Mapped[dict] = mapped_column(JSON())
    # ref_block_number: Mapped[str] = mapped_column(Integer())
    # ref_block_prefix: Mapped[str] = mapped_column(String())
    # signature: Mapped[str] = mapped_column(String())
    # transaction_to: Mapped[str] = mapped_column(String())
    # transaction_size: Mapped[str] = mapped_column(Integer())
    # logs: Mapped[List] = mapped_column(ARRAY(JSON))


from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy.types import TypeDecorator, TEXT
import json

class JSONType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Transaction(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    block_hash: str
    error: Optional[str] = None
    return_value: str
    status: str
    transaction_from: str
    method_name: str
    method_params: Dict[Any, Any] = Field(sa_column=Field(JSONType))
    ref_block_number: str
    ref_block_prefix: str
    signature: str
    transaction_to: str
    transaction_size: str
    logs: List[Dict[Any, Any]] = Field(sa_column=Field(JSONType))
