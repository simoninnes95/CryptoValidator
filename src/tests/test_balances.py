import polars as pl

def test_balances():

    wallets = pl.read_csv("data/wallets.csv")
    api_results = pl.read_csv("results/api_results.csv")

    joined = api_results.join(wallets, 
                            left_on="Address", 
                            right_on="address" ,  
                            how="inner")

    validated_df = joined.filter(pl.col("Balance") == pl.col("balance"))
    flagged_df = joined.filter(pl.col("Balance") != pl.col("balance"))
    null_df = joined.filter(pl.col("Balance").is_null() | pl.col("balance").is_null())
    
    validated_df.write_csv("results/validated.csv")
    flagged_df.write_csv("results/flagged.csv")
    null_df.write_csv("results/nulls.csv")

    return test_records(validated_df, flagged_df, null_df, joined.count())

def test_records(validated_df, flagged_df, null_df, expected_count):
    return validated_df.count() + flagged_df.count() + null_df.count() == expected_count
