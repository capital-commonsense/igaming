# DC online casinos (B26-0656): data and sources

The model, graphics and source documents behind Capital Commonsense's analysis of
B26-0656, the Internet Gaming and Consumer Protection Act of 2026.

- [`METHODS.md`](METHODS.md): how each graphic was built and what backs the article's claims.
- [`LIST_OF_CLAIMS.md`](LIST_OF_CLAIMS.md): every number shown, its derivation, the verbatim
  source quote and the saved source file.
- `outputs/figures/`: the graphics (SVG and PNG, plain and share versions) with alt text.

## Reproduce

```sh
uv sync
uv run pytest                   # model tests, plus every quote checked against its saved source
uv run dc-igaming all           # rebuild every CSV, figure, alt text file and LIST_OF_CLAIMS.md
```

Individual steps:

```sh
uv run dc-igaming flow          # money-flow CSVs and the "Follow one dollar" graphic
uv run dc-igaming projections   # GambetDC projections vs. actuals
uv run dc-igaming harms         # research findings grid
uv run dc-igaming claims-doc    # regenerate LIST_OF_CLAIMS.md
uv run dc-igaming fetch-sources # re-download source documents listed in the manifest
```

Rebuilding the graphics, and the tests that render them, needs Capital Commonsense's brand
kit at `brand_kit/`, which isn't included. The fonts (IBM Plex Sans and Newsreader) are
freely licensed; the logos are not. The model, claims and source checks run without it.

## Layout

| Path | What |
|---|---|
| `model/params.yaml` | Every model input, with unit, source and status (`verified`, `reported` or `assumption`). |
| `data/claims.yaml` | Every sourced number and article claim, with verbatim quotes. |
| `data/sources/` | Saved copies of every source, listed in `manifest.yaml` with URL, date and SHA-256. Kept under a fair-use rationale for verification; they will be taken down on request. |
| `src/dc_igaming/` | Model (`flow.py`), graphics (`diagram.py`, `projections.py`, `harms.py`), alt text and the claims list generator. |
| `outputs/` | CSVs: `one_dollar_cents.csv`, `flows_usd.csv`, `flow_summary.csv`, `flow_sensitivity.csv`, `parameter_provenance.csv`. |
| `tests/` | Model, rendering and source checks. |

## Model in brief

- Revenue comes from the DC CFO's fiscal impact statement on the committee print
  (fiscal 2030). Adjusted gross revenue, which equals DC players' combined net loss, is
  each 2% assessment ÷ 2%.
- Every share is cents per $1 of net player losses, and the slices sum to exactly $1.
- The headline (the city nets about 24¢) is the CFO's own net impact on resources ÷ that
  revenue.
