# uniswap-v3-positions

Rebuilds every Uniswap v3 liquidity position on Ethereum mainnet, and how much of each token it currently holds, from the raw event logs in BigQuery's public Ethereum dataset.

It's an Airflow DAG (run with the Astronomer CLI) that sets up BigQuery and then runs a dbt project through [Cosmos](https://github.com/astronomer/astronomer-cosmos), so each dbt model shows up as its own Airflow task.

## What the DAG does

```
begin → add_gcp_connection → add_dataset → add_reference_tables → transform (dbt) → end
```

1. **add_gcp_connection** creates (or updates) the `gcp` Airflow connection from the service account key.
2. **add_dataset** creates the BigQuery dataset if it doesn't exist.
3. **add_reference_tables** creates views over `bigquery-public-data.crypto_ethereum` (`blocks`, `transactions`, `logs`, `traces`, `tokens`) and the JavaScript UDFs that decode the events: `Mint`, `Burn`, `Swap`, `PoolCreated`, `IncreaseLiquidity`, `DecreaseLiquidity`, plus `decode_position`, which turns liquidity and a tick range into token amounts. The SQL lives in `include/utils/dataset.py`.
4. **transform** runs every model in `include/dbt/models/transform`.

## The dbt models

Everything starts from `filtered_logs`: the Ethereum logs whose first topic is one of the Uniswap v3 events, plus `Transfer`/`IncreaseLiquidity`/`DecreaseLiquidity` from the NonfungiblePositionManager (`0xc364…fe88`).

| Model | What it holds |
| --- | --- |
| `mint_logs`, `burn_logs` | Decoded pool `Mint` / `Burn` events (owner, tick range, liquidity, amounts) |
| `increase_liquidity_logs`, `decrease_liquidity_logs` | Decoded position manager events per NFT `token_id` |
| `pools` | Every pool from `PoolCreated`, with both tokens' decimals |
| `positions_calculation_data` | Each pool's state from its latest `Swap`: `sqrtPriceX96`, liquidity and tick |
| `liquidities` | Net liquidity (mints minus burns) per owner, pool and tick range |
| `positions` | `liquidities` turned into token amounts at the current pool price |
| `pm_nfts` | Each position NFT: its pool and tick range (from the `Mint` right before the NFT mint) and its current owner (latest `Transfer`) |
| `pm_liquidities` | Net liquidity per NFT |
| `pm_positions` | `pm_liquidities` turned into token amounts |

There are two views of the same liquidity:
- `positions` is what the pools see. Most liquidity is added through the position manager, so that contract shows up there as one huge owner.
- `pm_positions` splits that back out per NFT and attributes it to the wallet holding the NFT, which is usually what you want.

## Running it

You need Docker, the [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) and a GCP service account that can create datasets and run BigQuery jobs.

1. Save the service account key as `include/gcp/service_account.json` (gitignored).
2. Set `GCP_PROJECT` to your GCP project in `.env` (the Astro CLI passes `.env` into the containers). The dataset defaults to `uniswap_v3_positions`; set `BQ_DATASET` to use another name.
3. Start Airflow:

   ```sh
   astro dev start
   ```

   The UI is at http://localhost:8080 (`admin` / `admin`). The metadata Postgres is moved to port 5435 in `.astro/config.yaml` so it doesn't clash with a local Postgres.
4. Trigger the `uniswap_v3_positions` DAG by hand. It has no schedule.

dbt runs in its own virtualenv inside the image (see `Dockerfile`). Its `target/` and `logs/` folders are generated and not committed.

## Cost and caveats

- Each run scans the whole Ethereum `logs` table. That's several TB, so check your BigQuery pricing before triggering it. `filtered_logs` is a full table rebuild, not incremental.
- Amounts are floats. The UDFs return liquidity and amounts as JavaScript numbers (FLOAT64), so uint128/uint256 values lose precision above 2^53. Subtracting decreases from increases can leave a tiny non-zero remainder for a closed position, which then passes the `liquidity > 0` filter. Fixing it would mean returning strings from the UDFs and doing the math in `BIGNUMERIC`.
- Price comes from the latest swap. A pool with no swaps has no row in `positions_calculation_data`, so its positions are left out. Tokens without known decimals in `crypto_ethereum.tokens` are skipped too.
- Mainnet only. `decode_position` is called with chain id `1`.
- External UDF libraries. The decoders load `gs://blockchain-etl-bigquery/ethers.js` and `gs://libraries-bigquery/uniswap-v3-position.js`. Both have to be readable from your project.
- `include/soda/check_function.py` and the Soda virtualenv in the `Dockerfile` are set up for data quality checks, but no checks are written or wired into the DAG yet.

## License

MIT
