import datetime

def create_fix_message(msg_type, side, symbol, quantity, price):
    SOH = "|"
    now = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")
    msg_parts = [
        "8=FIX.4.4",
        "35=" + msg_type,
        "49=MY_TRADING_DESK",
        "56=LIQUIDITY_EXCHANGE",
        "34=1",
        f"52={now}"
    ]
    if msg_type == "D":
        msg_parts.extend([
            "11=ORDER_ID_10001",
            f"54={side}",
            f"55={symbol}",
            f"38={quantity}",
            f"44={price}",
            "40=2"
        ])
    return SOH.join(msg_parts) + SOH

def parse_fix_message(raw_message):
    tag_dictionary = {
        '8': "BeginString", '35': "MsgType", '49': "SenderCompID",
        '56': "TargetCompID", '34': "MsgSeqNum", '52': "SendingTime",
        '11': "ClOrdID", '54': "Side", '55': "Symbol",
        '38': "OrderQty", '44': "Price", '40': "OrdType"
    }
    print("\nParsing Live Trading Message Traffic...")
    pairs = raw_message.strip('|').split('|')
    for pair in pairs:
        if '=' in pair:
            tag, value = pair.split('=', 1)
            friendly_name = tag_dictionary.get(tag, f"Unknown Tag ({tag})")
            if tag == '35' and value == 'D': value = "D (New Order Single)"
            if tag == '54' and value == '1': value = "1 (BUY)"
            if tag == '54' and value == '2': value = "2 (SELL)"
            if tag == '40' and value == '2': value = "2 (LIMIT)"
            print(f"Tag {tag:<3} | {friendly_name:<25} : {value}")

if __name__ == "__main__":
    print("=== STARTING ELECTRONIC TRADING ENGINE ===")
    raw_order = create_fix_message("D", "1", "AAPL", 500, 175.50)
    print(f"\nRaw FIX String:\n{raw_order}")
    parse_fix_message(raw_order)
    print("\n=== SIMULATION COMPLETE ===")
