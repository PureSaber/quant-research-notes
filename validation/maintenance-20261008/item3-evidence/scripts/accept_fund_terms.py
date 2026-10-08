"""Check the new fee/precision software against published prospectus examples, not trades."""
import json
from dataclasses import replace
from pathlib import Path

from quant_fund.data import Fund
from quant_fund.dealing import ExecutionPolicy, redemption, subscription

root = Path(__file__).resolve().parent
source = next(row for row in json.loads((root / "official-source-receipts.json").read_text())
              if row["name"] == "fullgoal-000191-202606")
text = (root / "scratch" / "official" / "fullgoal.txt").read_text(encoding="utf-8")
for expected in ("39,682.54", "317.46", "38,156.29", "38,461.54", "10,149.84"):
    assert expected in text
policy = ExecutionPolicy(subscription_tiers=[[0, "rate", "0.008"], [1000000, "rate", "0.005"],
                                            [5000000, "fixed", "1000"]],
    money_decimals=2, share_decimals=2, money_rounding="half_up", share_rounding="half_up",
    redemption_fee_rounding="aggregate", residual_destination="fund",
    source_ref=source["url"] + "#pages-70-72", source_sha256=source["sha256"])
fund = Fund(fund_id="EXAMPLE_A", name="Published arithmetic example only", manager="Example",
    strategy="bond", kind="public", inception="2013-06-25", known_at="2026-10-08",
    execution_policy=policy, sell_tiers=[[100000, 0.001]])
buy = subscription(fund, 40000, 1.040)
assert buy["fee"] == 317.46 and buy["shares"] == 38156.29
zero = replace(fund, execution_policy=replace(policy, subscription_tiers=[[0, "rate", 0]]))
assert subscription(zero, 40000, 1.040)["shares"] == 38461.54
sale = redemption(fund, 10000, 1.016, [(10000, 180)])
assert sale["fee"] == 10.16 and round(sale["gross"] - sale["fee"], 2) == 10149.84
result = {"source_url": source["url"], "source_sha256": source["sha256"],
    "captured_at": source["captured_at"], "published_arithmetic_examples_passed": 3,
    "whole_product_terms_certified": False, "real_trade_confirmations_supplied": 0,
    "bank_receipts_supplied": 0, "real_business_certified": False,
    "scope": "A subscription, zero-fee subscription, and specified-rate redemption examples only"}
(root / "fund-terms-source-acceptance.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
