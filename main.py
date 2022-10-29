from ape import networks, Contract


if __name__ == "__main__":
    with networks.parse_network_choice("ethereum"):
        bond_manager = Contract("0x57619FE9C539f890b19c61812226F9703ce37137")
        lusd3crv_pool = Contract("0xEd279fDD11cA84bEef15AF5D39BB4d4bEE23F0cA")
        blusd_lusd3crv_pool = Contract("0x74ED5d42203806c8CDCf2F04Ca5F60DC777b901c")

        df = bond_manager.BondCancelled.query(
            "transaction_hash", "block_number", "bondId", start_block=15674057
        )

        def get_accrued_blusd(bond_id, block_num):
            return (
                bond_manager.calcAccruedBLUSD(bond_id, block_identifier=block_num - 1)
                / 1e18
            )

        df["accrued_blusd"] = df.apply(
            lambda x: get_accrued_blusd(x["bondId"], x["block_number"]), axis=1
        )

        lusd_rate = lusd3crv_pool.get_dy(0, 1, int(1e18)) / 1e18
        blusd_rate = blusd_lusd3crv_pool.get_dy(0, 1, int(1e18)) / 1e18

        df["usd_value"] = df["accrued_blusd"].apply(
            lambda x: x * lusd_rate * blusd_rate
        )

        df.to_csv("blusd_forfeited.csv")
