import datetime

class FixMessageBuilder:
    def __init__(self, sender, target, version="FIX.4.4"):
        self.sender = sender
        self.target = target
        self.version = version
        self.seq_num = 1

    def build_new_order(self, cl_ord_id, side, symbol, quantity, price):
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
        fields = [
            ("8", self.version), ("35", "D"), ("49", self.sender),
            ("56", self.target), ("34", str(self.seq_num)), ("52", timestamp),
            ("11", cl_ord_id), ("54", side), ("55", symbol),
            ("38", str(quantity)), ("44", str(price)), ("40", "2")
        ]
        self.seq_num += 1
        return self._serialize(fields)

    def _serialize(self, fields):
        body = "\x01".join(f"{t}={v}" for t, v in fields) + "\x01"
        body_length = len(body)
        full_message = f"8={self.version}\x019={body_length}\x01{body}"
        checksum = sum(ord(c) for c in full_message) % 256
        return full_message + f"10={checksum:03d}\x01"

class FixMessageParser:
    TAG_DEFINITIONS = {
        '8': "BeginString", '9': "BodyLength", '35': "MsgType",
        '49': "SenderCompID", '56': "TargetCompID", '34': "MsgSeqNum",
        '52': "SendingTime", '11': "ClOrdID", '54': "Side",
        '55': "Symbol", '38': "OrderQty", '44': "Price",
        '40': "OrdType", '10': "Checksum"
    }

    @classmethod
    def parse(cls, raw_message):
        print("Parsing incoming FIX message stream...")
        pairs = raw_message.strip("\x01").split("\x01")
        for pair in pairs:
            if "=" not in pair:
                continue
            tag, value = pair.split("=", 1)
            definition = cls.TAG_DEFINITIONS.get(tag, f"Unknown ({tag})")
            if tag == '35' and value == 'D': value = "D (New Order Single)"
            if tag == '54' and value == '1': value = "1 (BUY)"
            if tag == '54' and value == '2': value = "2 (SELL)"
            if tag == '40' and value == '2': value = "2 (LIMIT)"
            print(f"Tag {tag:<3} | {definition:<25} : {value}")

if __name__ == "__main__":
    print("Initializing Electronic Trading Engine")
    builder = FixMessageBuilder("MY_TRADING_DESK", "LIQUIDITY_EXCHANGE")
    raw_msg = builder.build_new_order("ORD-10001", "1", "AAPL", 500.0, 175.50)
    print(f"Generated Raw FIX Stream:\n{repr(raw_msg)}")
    FixMessageParser.parse(raw_msg)
    print("Simulation complete.")
