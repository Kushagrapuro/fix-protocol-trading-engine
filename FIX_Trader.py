import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class FixTag(Enum):
    BEGIN_STRING = "8"
    BODY_LENGTH = "9"
    MSG_TYPE = "35"
    SENDER_COMP_ID = "49"
    TARGET_COMP_ID = "56"
    MSG_SEQ_NUM = "34"
    SENDING_TIME = "52"
    CL_ORD_ID = "11"
    SIDE = "54"
    SYMBOL = "55"
    ORDER_QTY = "38"
    PRICE = "44"
    ORD_TYPE = "40"
    CHECKSUM = "10"

class MsgType(Enum):
    NEW_ORDER_SINGLE = "D"

class Side(Enum):
    BUY = "1"
    SELL = "2"

class OrdType(Enum):
    LIMIT = "2"

@dataclass
class OrderRequest:
    cl_ord_id: str
    side: Side
    symbol: str
    quantity: float
    price: float
    ord_type: OrdType = OrdType.LIMIT

class FixMessageBuilder:
    def __init__(self, sender: str, target: str, version: str = "FIX.4.4"):
        self.sender = sender
        self.target = target
        self.version = version
        self.seq_num = 1

    def build_new_order(self, order: OrderRequest) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
        standard_fields = [
            (FixTag.BEGIN_STRING, self.version),
            (FixTag.MSG_TYPE, MsgType.NEW_ORDER_SINGLE.value),
            (FixTag.SENDER_COMP_ID, self.sender),
            (FixTag.TARGET_COMP_ID, self.target),
            (FixTag.MSG_SEQ_NUM, str(self.seq_num)),
            (FixTag.SENDING_TIME, timestamp),
        ]
        order_fields = [
            (FixTag.CL_ORD_ID, order.cl_ord_id),
            (FixTag.SIDE, order.side.value),
            (FixTag.SYMBOL, order.symbol),
            (FixTag.ORDER_QTY, str(order.quantity)),
            (FixTag.PRICE, str(order.price)),
            (FixTag.ORD_TYPE, order.ord_type.value),
        ]
        self.seq_num += 1
        return self._serialize(standard_fields + order_fields)

    def _serialize(self, fields: List[Tuple[FixTag, str]]) -> str:
        body = "\x01".join(f"{tag.value}={val}" for tag, val in fields) + "\x01"
        body_length = len(body)
        full_message = f"8={self.version}\x019={body_length}\x01{body}"
        checksum = sum(ord(c) for c in full_message) % 256
        full_message += f"10={checksum:03d}\x01"
        return full_message

class FixMessageParser:
    TAG_DEFINITIONS = {
        FixTag.BEGIN_STRING: "BeginString (Protocol Version)",
        FixTag.BODY_LENGTH: "BodyLength (Message Size)",
        FixTag.MSG_TYPE: "MsgType (Message Type)",
        FixTag.SENDER_COMP_ID: "SenderCompID (Firm Identifier)",
        FixTag.TARGET_COMP_ID: "TargetCompID (Exchange Identifier)",
        FixTag.MSG_SEQ_NUM: "MsgSeqNum (Sequence Number)",
        FixTag.SENDING_TIME: "SendingTime (UTC Timestamp)",
        FixTag.CL_ORD_ID: "ClOrdID (Unique Client Order ID)",
        FixTag.SIDE: "Side (Trade Direction)",
        FixTag.SYMBOL: "Symbol (Financial Instrument)",
        FixTag.ORDER_QTY: "OrderQty (Volume)",
        FixTag.PRICE: "Price (Limit Price)",
        FixTag.ORD_TYPE: "OrdType (Execution Logic)",
        FixTag.CHECKSUM: "Checksum (Data Integrity)",
    }

    VALUE_TRANSLATIONS = {
        FixTag.MSG_TYPE: {"D": "D (New Order Single)"},
        FixTag.SIDE: {"1": "1 (BUY ORDER)", "2": "2 (SELL ORDER)"},
        FixTag.ORD_TYPE: {"2": "2 (LIMIT ORDER)"},
    }

    @classmethod
    def parse(cls, raw_message: str) -> Dict[FixTag, str]:
        logger.info("Parsing incoming FIX message stream...")
        parsed_data = {}
        pairs = raw_message.strip("\x01").split("\x01")
        
        for pair in pairs:
            if "=" not in pair:
                continue
            tag_str, value = pair.split("=", 1)
            try:
                tag = FixTag(tag_str)
                parsed_data[tag] = value
                definition = cls.TAG_DEFINITIONS.get(tag, f"Unknown Tag ({tag_str})")
                display_value = cls.VALUE_TRANSLATIONS.get(tag, {}).get(value, value)
                logger.info(f"Tag {tag.value:<3} | {definition:<35} : {display_value}")
            except ValueError:
                logger.warning(f"Unrecognized tag in stream: {tag_str}")
                
        return parsed_data

def main():
    logger.info("Initializing Electronic Trading Engine Simulation")
    builder = FixMessageBuilder(sender="MY_TRADING_DESK", target="LIQUIDITY_EXCHANGE")
    
    order = OrderRequest(
        cl_ord_id="ORD-10001",
        side=Side.BUY,
        symbol="AAPL",
        quantity=500.0,
        price=175.50
    )
    
    raw_msg = builder.build_new_order(order)
    logger.info(f"Generated Raw FIX Stream:\n{repr(raw_msg)}")
    
    FixMessageParser.parse(raw_msg)
    logger.info("Simulation complete. All fields validated successfully.")

if __name__ == "__main__":
    main()
