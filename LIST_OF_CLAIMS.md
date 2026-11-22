# List of claims

<!-- GENERATED FILE: do not edit by hand. Regenerate with `uv run dc-igaming claims-doc`. -->
<!-- tests/test_claims_doc.py fails if this file is out of date. -->

Every number and factual statement in the three graphics, with how it was derived and where it comes from. A reader should be able to check each item without trusting the authors.

## How to verify

```sh
uv sync
uv run pytest                  # all checks below, including quote-in-source tests
uv run dc-igaming all          # re-render every graphic and CSV from the inputs
uv run dc-igaming claims-doc   # regenerate this file
shasum -a 256 data/sources/*   # compare with the sha256 column in the source register
```

Every item below is one of three kinds:

- **Checked quote**: a claim in [`data/claims.yaml`](data/claims.yaml) with verbatim quotes. `tests/test_claims.py` extracts the text of the saved source file and fails unless every quote appears in it (after whitespace, quote-mark and ligature normalization), and fails if the file's sha256 differs from the manifest. To check by hand, open the file in `data/sources/` and search for the quote.
- **Model output**: computed from parameters in [`model/params.yaml`](model/params.yaml) by [`src/dc_igaming/flow.py`](src/dc_igaming/flow.py). The formula is given; golden-value tests are in `tests/test_flow.py`. Each parameter is marked `verified` (checked against a primary source), `reported` (checked against secondary reporting only) or `assumption` (no source).
- **Definitional**: true by construction (for example, the income-tax panel's 100¢).

## 1. Follow one dollar (Sankey)

Files: `outputs/figures/follow_one_dollar_central.{svg,png}` and `_share` versions. Code: `src/dc_igaming/diagram.py`.

**The “$1” is DC players' combined net loss**: everything wagered minus everything paid back as winnings, including winnings to players who finish ahead. That equals operators' gross gaming revenue (GGR). Shares are cents per $1 of GGR. The out-of-state share is the residual, so the slices sum to exactly $1 (`tests/test_flow.py::test_every_dollar_of_net_loss_is_accounted_for`). There is no “winners” slice: taken together, players lose.

### Numbers shown (central scenario)

| Shown on graphic | Value | Derivation | Inputs and supporting claims |
|---|---|---|---|
| Headline: “the city nets 24 cents” | 23.8¢ | CFO net impact on resources ÷ AGR (= community impact assessment ÷ 2%). The model rebuilds the CFO's net line from its parts and matches it exactly (`tests/test_flow.py::test_net_impact_reproduces_cfo_line`) | `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030); `constants.assessment_rate`; [`fis_community_impact`](#fis_community_impact), [`fis_regulatory_assessment`](#fis_regulatory_assessment); [`fis_net_impact_fy2030`](#fis_net_impact_fy2030) |
| $1 (net of winnings) | 100¢ | Denominator: players' combined net loss = adjusted gross revenue; promotional credits are not counted as wagers | [`fis_agr_definition`](#fis_agr_definition), [`print_promo_credits`](#print_promo_credits) |
| Implied adjusted gross revenue | $66.8M/yr | community impact assessment ÷ 2%, cross-checked against the regulatory assessment | `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030); `scenarios.central.regulatory_assessment`; [`fis_regulatory_fy2030`](#fis_regulatory_fy2030); `constants.assessment_rate`; [`fis_community_impact`](#fis_community_impact), [`fis_regulatory_assessment`](#fis_regulatory_assessment) |
| 57¢ leaves DC | 57¢ | AGR − everything paid to DC − dealer pay − vendors, ÷ AGR. The residual, so slices sum to $1 | `scenarios.central.tax_revenue`; [`fis_tax_fy2030`](#fis_tax_fy2030); `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030); `scenarios.central.regulatory_assessment`; [`fis_regulatory_fy2030`](#fis_regulatory_fy2030); `scenarios.central.license_fees`; [`fis_license_fy2030`](#fis_license_fy2030); `scenarios.central.jobs`; [`igaming_union_jobs`](#igaming_union_jobs), [`fis_live_dealer_requirements`](#fis_live_dealer_requirements); `scenarios.central.comp_per_job`; `scenarios.central.local_vendor_spend`; [`fis_cbe_requirement`](#fis_cbe_requirement) |
| DC general fund (tax) | 22.9¢ | (tax − $750K set-aside) ÷ AGR | `scenarios.central.tax_revenue`; [`fis_tax_fy2030`](#fis_tax_fy2030); `constants.treatment_setaside`; [`fis_setaside`](#fis_setaside) |
| DC community impact fund | 2¢ | 2% assessment ÷ AGR | `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030) |
| DC addiction services | 1.1¢ | $750K ÷ AGR | `constants.treatment_setaside`; [`fis_setaside`](#fis_setaside) |
| DC license fees | 0.24¢ | FY2030 license fees ÷ AGR | `scenarios.central.license_fees`; [`fis_license_fy2030`](#fis_license_fy2030) |
| Regulating the market (OLG) | 2¢ | 2% regulatory assessment ÷ AGR; the CFO offsets it with equal OLG costs | `scenarios.central.regulatory_assessment`; [`fis_regulatory_fy2030`](#fis_regulatory_fy2030); `scenarios.central.olg_regulatory_costs`; [`fis_olg_costs_fy2030`](#fis_olg_costs_fy2030) |
| Dealers' pay | 10.3¢ | jobs × (pay − dues) ÷ AGR | `scenarios.central.jobs`; [`igaming_union_jobs`](#igaming_union_jobs), [`fis_live_dealer_requirements`](#fis_live_dealer_requirements); `scenarios.central.comp_per_job`; `constants.union_dues_per_member`; [`local25_dues_rate_2025`](#local25_dues_rate_2025), [`local25_dues_receipts_2025`](#local25_dues_receipts_2025), [`local25_members_2025`](#local25_members_2025) |
| Union dues (UNITE HERE Local 25) | 0.19¢ | jobs × dues ÷ AGR | `scenarios.central.jobs`; [`igaming_union_jobs`](#igaming_union_jobs), [`fis_live_dealer_requirements`](#fis_live_dealer_requirements); `constants.union_dues_per_member`; [`local25_dues_rate_2025`](#local25_dues_rate_2025), [`local25_dues_receipts_2025`](#local25_dues_receipts_2025), [`local25_members_2025`](#local25_members_2025) |
| DC local vendors | 4.5¢ | vendor spending ÷ AGR | `scenarios.central.local_vendor_spend`; [`fis_cbe_requirement`](#fis_cbe_requirement) |
| Or: $1 of income tax → 100¢ to DC | 100¢ | Definitional: income tax is collected by DC directly |  |
| Fine print: tax rates | 25%; live dealer 12.5% | as stated in the committee print | `constants.tax_rate`; [`fis_tax_rates`](#fis_tax_rates), [`print_tax_rates`](#print_tax_rates); `constants.live_dealer_tax_rate`; [`fis_tax_rates`](#fis_tax_rates), [`print_tax_rates`](#print_tax_rates) |
| Fine print: blended tax rate | 24.05% | CFO tax ÷ AGR (implies 7.6% of AGR from live-dealer games) | `scenarios.central.tax_revenue`; [`fis_tax_fy2030`](#fis_tax_fy2030); `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030) |
| Fine print: each 2% assessment | $1.3M | CFO table, FY2030 | `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030) |
| Fine print: red slices total | 26.3¢ | (tax + community impact + license fees) ÷ AGR | `scenarios.central.tax_revenue`; [`fis_tax_fy2030`](#fis_tax_fy2030); `scenarios.central.community_impact`; [`fis_community_impact_fy2030`](#fis_community_impact_fy2030); `scenarios.central.license_fees`; [`fis_license_fy2030`](#fis_license_fy2030) |
| Fine print: lost lottery and sports-betting revenue | $1.6M/yr (2.5¢) | CFO table, FY2030 | `scenarios.central.lottery_loss`; [`fis_lottery_loss_fy2030`](#fis_lottery_loss_fy2030); `scenarios.central.sports_wagering_loss`; [`fis_sports_loss_fy2030`](#fis_sports_loss_fy2030) |
| Fine print: net gain | $15.9M (23.8¢) | red slices − lost revenue (the regulatory assessment and OLG costs cancel) | [`fis_net_impact_fy2030`](#fis_net_impact_fy2030) |
| Fine print: jobs, pay, vendors | 100 jobs; $70K; $3.0M | committee estimate; assumption; assumption | `scenarios.central.jobs`; [`igaming_union_jobs`](#igaming_union_jobs), [`fis_live_dealer_requirements`](#fis_live_dealer_requirements); `scenarios.central.comp_per_job`; `scenarios.central.local_vendor_spend`; [`fis_cbe_requirement`](#fis_cbe_requirement) |
| Fine print: income-tax equivalent | 0.43% | net gain ÷ FY2026 individual income tax | `constants.fy26_individual_income_tax`; [`iit_fy2026`](#iit_fy2026) |
| Fine print: dues rate | $105/month ($1,260/yr); range $59.92–$105.00 | top of Local 25's reported regular dues range × 12 | [`local25_dues_rate_2025`](#local25_dues_rate_2025) |
| Fine print: dues receipts per member | $1,274 | $7.8M ÷ 6,101 members (consistency check on the rate) | [`local25_dues_receipts_2025`](#local25_dues_receipts_2025), [`local25_members_2025`](#local25_members_2025) |
| Fine print: total dues | $126K/yr | jobs × dues | `scenarios.central.jobs`; [`igaming_union_jobs`](#igaming_union_jobs), [`fis_live_dealer_requirements`](#fis_live_dealer_requirements); `constants.union_dues_per_member`; [`local25_dues_rate_2025`](#local25_dues_rate_2025), [`local25_dues_receipts_2025`](#local25_dues_receipts_2025), [`local25_members_2025`](#local25_members_2025) |

### Inputs

| Parameter | Value | Unit | Status | Source | Claims |
|---|---|---|---|---|---|
| `constants.tax_rate` | 0.25 | tax rate on adjusted gross internet gaming revenue (AGR) | verified (primary source) | CFO fiscal impact statement on the B26-0656 committee print | [`fis_tax_rates`](#fis_tax_rates), [`print_tax_rates`](#print_tax_rates) |
| `constants.live_dealer_tax_rate` | 0.125 | tax rate on live-dealer AGR (used to check the CFO's implied blended rate) | verified (primary source) | CFO fiscal impact statement on the B26-0656 committee print | [`fis_tax_rates`](#fis_tax_rates), [`print_tax_rates`](#print_tax_rates) |
| `constants.assessment_rate` | 0.02 | share of AGR for each of the community impact and regulatory assessments | verified (primary source) | CFO fiscal impact statement on the B26-0656 committee print | [`fis_community_impact`](#fis_community_impact), [`fis_regulatory_assessment`](#fis_regulatory_assessment) |
| `constants.treatment_setaside` | 750,000 | USD per year, first tax dollars to the Department of Behavioral Health | verified (primary source) | CFO fiscal impact statement (D.C. Official Code § 36-681.01) | [`fis_setaside`](#fis_setaside) |
| `constants.union_dues_per_member` | 1,260 | USD per member per year | verified (primary source) | UNITE HERE Local 25 2025 Form LM-2 (DOL file no. 506-434), item 21: regular dues $59.92-$105.00 per member per month. Uses the top of the range ($105 x 12), which matches 2025 dues receipts per member ($7,772,376 / 6,101 = $1,274). | [`local25_dues_rate_2025`](#local25_dues_rate_2025), [`local25_dues_receipts_2025`](#local25_dues_receipts_2025), [`local25_members_2025`](#local25_members_2025) |
| `constants.fy26_individual_income_tax` | 3,699,357,000 | USD, FY2026 DC individual income tax estimate | verified (primary source) | DC OCFO June 2026 revenue estimate letter, Table 1 ($ in thousands): FY2026 Individual Income 3,699,357. | [`iit_fy2026`](#iit_fy2026) |
| `scenarios.central.tax_revenue` | 16,056,000 | USD per year, tax on gaming revenue (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_tax_fy2030`](#fis_tax_fy2030) |
| `scenarios.central.community_impact` | 1,335,000 | USD per year, community impact assessment (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_community_impact_fy2030`](#fis_community_impact_fy2030) |
| `scenarios.central.regulatory_assessment` | 1,335,000 | USD per year, regulatory assessment (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_regulatory_fy2030`](#fis_regulatory_fy2030) |
| `scenarios.central.olg_regulatory_costs` | 1,335,000 | USD per year, Office of Lottery and Gaming regulatory costs (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_olg_costs_fy2030`](#fis_olg_costs_fy2030) |
| `scenarios.central.license_fees` | 160,000 | USD per year, license fee revenue (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_license_fy2030`](#fis_license_fy2030) |
| `scenarios.central.lottery_loss` | 1,130,000 | USD per year, decrease in lottery earnings (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_lottery_loss_fy2030`](#fis_lottery_loss_fy2030) |
| `scenarios.central.sports_wagering_loss` | 520,000 | USD per year, decrease in sports wagering taxes (FY2030) | verified (primary source) | CFO fiscal impact statement, financial plan table | [`fis_sports_loss_fy2030`](#fis_sports_loss_fy2030) |
| `scenarios.central.hold` | 0.035 | AGR / handle (CSV outputs only; not shown in any graphic) | **assumption** | assumption: player-friendly vs. PA online slots ~3.8% (PGCB, March 2026) |  |
| `scenarios.central.jobs` | 100 | union live-dealer jobs in DC | reported (secondary source) | Human Services Committee estimate (Axios DC, Nov 18 2026) | [`igaming_union_jobs`](#igaming_union_jobs), [`fis_live_dealer_requirements`](#fis_live_dealer_requirements) |
| `scenarios.central.comp_per_job` | 70,000 | USD per job per year, fully loaded | **assumption** | assumption: typical casino dealer pay with benefits |  |
| `scenarios.central.local_vendor_spend` | 3,000,000 | USD per year to DC certified local businesses | **assumption** | assumption. The committee print requires 35% of an operator's DC-related operating budget to go to certified business enterprises, but the budget's size isn't specified and waivers are deemed approved after 30 days (fis_cbe_requirement). | [`fis_cbe_requirement`](#fis_cbe_requirement) |

The steady-state year is fiscal 2030, the last year of the CFO's financial plan. Fiscal 2028 includes $12.3M of one-time operator license fees, and fiscal 2027 has no revenue.

## 2. Projections vs. actuals

Files: `outputs/figures/projections_vs_actuals.{svg,png}` and `_share` versions. Code: `src/dc_igaming/projections.py`.

| Shown on graphic | Value | Basis | Supporting claims |
|---|---|---|---|
| Title: “DC’s last gambling forecast delivered 13.5 cents on the dollar” | 13.5% | FY2022 actual ÷ FY2022 projection | [`gambetdc_fy2022_actual`](#gambetdc_fy2022_actual), [`gambetdc_fy2022_projection`](#gambetdc_fy2022_projection) |
| GambetDC sports betting, FY2021: Projected Nov. 2018 | $27M | USD, projected FY2021 sports wagering revenue to DC | [`gambetdc_fy2021_projection_2018`](#gambetdc_fy2021_projection_2018) |
| GambetDC sports betting, FY2021: Revised Feb. 2021 | $6.2M | USD, FY2021 revenue the DC Council expected (Feb. 2021) | [`gambetdc_fy2021_projection_2021`](#gambetdc_fy2021_projection_2021) |
| GambetDC sports betting, FY2021: Actual | $0 | USD, FY2021 net transfer to DC | [`gambetdc_fy2021_actual`](#gambetdc_fy2021_actual) |
| Note above bar: “lost $4M” | lost $4M |  | [`gambetdc_fy2021_loss`](#gambetdc_fy2021_loss) |
| GambetDC sports betting, FY2022: Projected | $20M | USD, revenue city officials once estimated for 2022 | [`gambetdc_fy2022_projection`](#gambetdc_fy2022_projection) |
| GambetDC sports betting, FY2022: Actual | $2.7M | USD, FY2022 net transfer to DC | [`gambetdc_fy2022_actual`](#gambetdc_fy2022_actual) |
| Note above bar: “13.5% of estimate” | 13.5% of estimate |  | [`gambetdc_fy2022_actual`](#gambetdc_fy2022_actual), [`gambetdc_fy2022_projection`](#gambetdc_fy2022_projection) |
| Online casino (B26-0656), fiscal 2030: Projected (DC CFO) | $15.9M | USD, FY2030 net impact on District resources | [`fis_net_impact_fy2030`](#fis_net_impact_fy2030) |
| Online casino (B26-0656), fiscal 2030: Actual | ? | Not yet known: the program hasn't launched |  |
| Fine print: other estimate | $50M a year | Annual gaming tax estimate from an economic analysis cited at markup, as reported by Covers | [`igaming_other_estimate`](#igaming_other_estimate) |
| Fine print: lawmakers' $73M over four years | $73M | Four-year gaming tax estimate attributed to lawmakers by Axios DC | [`igaming_committee_estimate`](#igaming_committee_estimate) |

GambetDC actuals are net transfers to the District reported by the Office of Lottery and Gaming. GambetDC projections are as reported at the time. The online casino bar shows the DC Chief Financial Officer's projected net impact on District resources in FY2030 from the fiscal impact statement on the committee print.

## 3. Research findings (“What researchers find when gambling moves onto phones”)

Files: `outputs/figures/research_findings.{svg,png}` and `_share` versions. Code: `src/dc_igaming/harms.py`.

| Headline | Finding as worded | Evidence type label | Citation shown | Supporting claims |
|---|---|---|---|---|
| +25–30% | at the high end, three to four years after a state's online sports betting launch | Online sports betting · ~7M consumers | Hollenbeck, Larsen & Proserpio, working paper (Oct. 2024) | [`bankruptcy`](#bankruptcy), [`hollenbeck_sample`](#hollenbeck_sample) |
| +8% | approximate rise in the average amount owed after online sports betting became legal | Online sports betting · ~7M consumers | Hollenbeck, Larsen & Proserpio, working paper (Oct. 2024) | [`collections`](#collections), [`hollenbeck_sample`](#hollenbeck_sample) |
| −$0.99 | for every $1 bet on sports online. Among strapped households, card debt and overdrafts rise | Online sports betting · bank transactions | Baker et al., NBER WP 33108 (2024) | [`investment_crowd_out`](#investment_crowd_out), [`constrained_households`](#constrained_households), [`baker_data`](#baker_data) |
| +8.5–9.6% | where sports betting is legal, in reported partner violence after NFL home-team upsets: a bigger spike than where betting isn't legal | Sports betting · police reports, 2011–2022 | Arnesen & Matsuzawa, CHEPS WP (2025) | [`ipv`](#ipv), [`ipv_data`](#ipv_data) |
| 15× | vs. the general population, among Swedish patients aged 20–74 with diagnosed gambling disorder | Association · Swedish clinical cohort | Karlsson & Håkansson, J. Behavioral Addictions (2018) | [`suicide`](#suicide), [`karlsson_data`](#karlsson_data) |
| 60% | of French online and account-based gambling revenue came from the 8.7% of players flagged as likely problem gamblers | Online + account-based gambling · France, H2 2025 | France ANJ (2026) | [`anj_concentration`](#anj_concentration) |
| 10× | among New Jersey gamblers who bet only online (11.3%) vs. only in person (1.1%) | Association · New Jersey, 2020–21 survey | Nower, Stanmyre & Anthony, Rutgers report to NJ DGE (2023) | [`nj_venue_disorder`](#nj_venue_disorder), [`nj_survey_dates`](#nj_survey_dates) |
| +87% | and texts to Connecticut's problem-gambling helpline, Nov. 2021 vs. Nov. 2020 | Online casino + sports betting · Connecticut | CT Mirror (Jan. 23, 2022) | [`ct_helpline`](#ct_helpline), [`ct_products`](#ct_products) |
| 50%+ | of calls to Pennsylvania's problem-gambling helpline involved problematic online gambling | Online casino + sports betting · Pennsylvania | Penn State SSRI, 2025 PA online gambling report | [`pa_helpline`](#pa_helpline), [`pa_products`](#pa_products) |

Each headline is a number plus the harm it measures, set under the number in bold serif. Derived headlines: `10×` is 11.3% ÷ 1.1% (New Jersey, Table 28), rounded *down* from 10.3 so it never overstates. `+87%` is (583 − 311) ÷ 311, also rounded down. `+25–30%` is the high end the October 2024 draft reports (“as much as”), and the tile says so. `+8.5–9.6%` is the authors' controlled estimate of the rise in partner violence after an upset loss where betting is legal (section 5.1). The paper finds that effect is larger where betting is legal (interaction significant at the 10% level). The label says “domestic violence”; the paper measures intimate partner violence, a subset, and the finding text says “partner violence”. `+8%` (“roughly” in the source, “approximate” on the tile), `−$0.99`, `15×`, `60%` and `50%+` restate the quoted figures directly.

Fine-print caveats on the graphic: none of these are DC estimates; the financial and NFL findings cover sports betting, and few studies isolate online casino games; Connecticut launched online casino games and sports betting together; helpline figures measure service contacts; the New Jersey and Swedish results compare groups of people and do not show that gambling caused the differences.

## 4. Claim register

Every claim in `data/claims.yaml`. The quotes are checked against the saved source by `tests/test_claims.py`.

### gambetdc_fy2021_projection_2018

- **Value:** 27,000,000 (USD, projected FY2021 sports wagering revenue to DC)
- **Source:** Casino.org (citing DCist), “GamBetDC, Controversial Washington DC Sports Bet App, Lost $4M Last Year” (2022-03) — [https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/](https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/)
- **Local copy:** [`data/sources/casinoorg_2021_gambetdc_lost_4m.html`](data/sources/casinoorg_2021_gambetdc_lost_4m.html)
- **Verbatim quotes:**
  - “the $27 million that former DC CFO Jeffrey DeWitt projected for 2021 back in November 2018”
- **Used in:** Projections chart bar

### gambetdc_fy2021_projection_2021

- **Value:** 6,200,000 (USD, FY2021 revenue the DC Council expected (Feb. 2021))
- **Source:** Casino.org (citing DCist), “GamBetDC, Controversial Washington DC Sports Bet App, Lost $4M Last Year” (2022-03) — [https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/](https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/)
- **Local copy:** [`data/sources/casinoorg_2021_gambetdc_lost_4m.html`](data/sources/casinoorg_2021_gambetdc_lost_4m.html)
- **Verbatim quotes:**
  - “The DC Council said in February 2021 it expected the platform to bring in $6.2 million for the district”
- **Used in:** Projections chart bar

### gambetdc_fy2021_actual

- **Value:** 0 (USD, FY2021 net transfer to DC)
- **Source:** DC Office of the Chief Financial Officer, “Office of Lottery and Gaming, FY21-22 Performance Oversight Hearing Presentation” (2022-03) — [https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/release_content/attachments/OLG%20FY21-22%20Performance%20Oversight%20Hearing%20Presentation.pdf](https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/release_content/attachments/OLG%20FY21-22%20Performance%20Oversight%20Hearing%20Presentation.pdf)
- **Local copy:** [`data/sources/olg_fy21_22_oversight_presentation.pdf`](data/sources/olg_fy21_22_oversight_presentation.pdf)
- **Verbatim quotes:**
  - “GambetDC did not provide a net transfer to the District in FY21”
- **Used in:** Projections chart bar

### gambetdc_fy2021_loss

- **Value:** 4,000,000 (USD, FY2021 operating loss)
- **Source:** Casino.org (citing DCist), “GamBetDC, Controversial Washington DC Sports Bet App, Lost $4M Last Year” (2022-03) — [https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/](https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/)
- **Local copy:** [`data/sources/casinoorg_2021_gambetdc_lost_4m.html`](data/sources/casinoorg_2021_gambetdc_lost_4m.html)
- **Verbatim quotes:**
  - “booked a $4 million loss in its first full year”
- **Used in:** Projections chart note/fine print

### gambetdc_fy2022_projection

- **Value:** 20,000,000 (USD, revenue city officials once estimated for 2022)
- **Source:** DCist, “D.C.'s sports betting app is still underperforming” (2022-03-03) — [https://dcist.com/story/22/03/03/dc-lottery-app-underperforms/](https://dcist.com/story/22/03/03/dc-lottery-app-underperforms/)
- **Local copy:** [`data/sources/dcist_2022_lottery_app_underperforms.html`](data/sources/dcist_2022_lottery_app_underperforms.html)
- **Verbatim quotes:**
  - “one-tenth of the $20 million city officials once estimated”
- **Used in:** Projections chart bar

### gambetdc_fy2022_actual

- **Value:** 2,700,000 (USD, FY2022 net transfer to DC)
- **Source:** DC Office of the Chief Financial Officer, “Office of Lottery and Gaming, 2022-2023 Performance Oversight Hearing Testimony Slides” (2023-02) — [https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/release_content/attachments/OLG%202022-2023%20Performance%20Oversight%20Hearing%20Testimony%20Slides.pdf](https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/release_content/attachments/OLG%202022-2023%20Performance%20Oversight%20Hearing%20Testimony%20Slides.pdf)
- **Local copy:** [`data/sources/olg_fy22_23_oversight_slides.pdf`](data/sources/olg_fy22_23_oversight_slides.pdf)
- **Verbatim quotes:**
  - “Net transfer to the District of $2.7 million”
- **Used in:** Projections chart bar

### igaming_committee_estimate

- **Value:** 18,250,000 (USD per year (committee's $73M over four years / 4))
- **Source:** Axios DC, “D.C. moves to expand legal gambling with online gaming” (2026-11-18) — [https://www.axios.com/local/washington-dc/2026/11/18/online-gaming-dc-gambling](https://www.axios.com/local/washington-dc/2026/11/18/online-gaming-dc-gambling)
- **Local copy:** [`data/sources/axios_2026_dc_online_gaming.pdf`](data/sources/axios_2026_dc_online_gaming.pdf)
- **Verbatim quotes:**
  - “sweep up $73 million in new tax revenue over four years”
  - “will bring in $73 million in tax revenue over four years (not $500 million over five years)”
- **Used in:** Projections chart note/fine print

### igaming_union_jobs

- **Value:** 100 (union live-dealer jobs the committee expects (used in the Sankey))
- **Source:** Axios DC, “D.C. moves to expand legal gambling with online gaming” (2026-11-18) — [https://www.axios.com/local/washington-dc/2026/11/18/online-gaming-dc-gambling](https://www.axios.com/local/washington-dc/2026/11/18/online-gaming-dc-gambling)
- **Local copy:** [`data/sources/axios_2026_dc_online_gaming.pdf`](data/sources/axios_2026_dc_online_gaming.pdf)
- **Verbatim quotes:**
  - “The Human Services Committee believes the online gaming bill will create 100 union jobs”
  - “the bill requires actual employees streaming themselves dealing cards to players online”
- **Used in:** Sankey input `scenarios.central.jobs`

### igaming_other_estimate

- **Value:** 50,000,000 (USD per year, economic analysis cited at the committee markup)
- **Source:** Covers, “DC Online Casino Bill Advances Out of Council Committee” (2026-11-18) — [https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026](https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026)
- **Local copy:** [`data/sources/covers_2026_dc_igaming_committee.html`](data/sources/covers_2026_dc_igaming_committee.html)
- **Verbatim quotes:**
  - “potentially generating approximately $50 million annually”
- **Used in:** Projections chart note/fine print

### bankruptcy

- **Value:** 25, 30 (% increase in likelihood of bankruptcy filing, 3-4 years after online sports betting legalization)
- **Source:** Hollenbeck, Larsen & Proserpio. October 2024 working-paper draft; the bankruptcy and collections figures are from its section 4.2. Copy hosted by the Minnesota Senate Finance Committee., “The Financial Consequences of Legalized Sports Betting (working paper, Oct. 2024)” (2024-10) — [https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf](https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf)
- **Local copy:** [`data/sources/hollenbeck_2024_financial_consequences.pdf`](data/sources/hollenbeck_2024_financial_consequences.pdf)
- **Verbatim quotes:**
  - “Three to four years after the legalization of online sports gambling”
  - “the likelihood of bankruptcy filing increases by as much as 25-30% when compared to pre-treatment levels”
- **Used in:** Research findings tile `bankruptcy` (headline)

### hollenbeck_sample

- **Value:** 7,000,000 (consumers in the UC Consumer Credit Panel (tile label "7M credit files"))
- **Source:** Hollenbeck, Larsen & Proserpio. October 2024 working-paper draft; the bankruptcy and collections figures are from its section 4.2. Copy hosted by the Minnesota Senate Finance Committee., “The Financial Consequences of Legalized Sports Betting (working paper, Oct. 2024)” (2024-10) — [https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf](https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf)
- **Local copy:** [`data/sources/hollenbeck_2024_financial_consequences.pdf`](data/sources/hollenbeck_2024_financial_consequences.pdf)
- **Verbatim quotes:**
  - “a sample of roughly 7 million U.S. adults”
- **Used in:** Research findings tile `bankruptcy` (text/label); Research findings tile `collections` (text/label)

### collections

- **Value:** 8 (% increase in the average amount of debt in collections after online sports betting became legal)
- **Source:** Hollenbeck, Larsen & Proserpio. October 2024 working-paper draft; the bankruptcy and collections figures are from its section 4.2. Copy hosted by the Minnesota Senate Finance Committee., “The Financial Consequences of Legalized Sports Betting (working paper, Oct. 2024)” (2024-10) — [https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf](https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf)
- **Local copy:** [`data/sources/hollenbeck_2024_financial_consequences.pdf`](data/sources/hollenbeck_2024_financial_consequences.pdf)
- **Verbatim quotes:**
  - “We observe a significant increase in collections when focusing on online accessibility, translating to a roughly 8% average increase”
  - “changes in the amount of debt in collection on account”
- **Used in:** Research findings tile `collections` (headline)

### investment_crowd_out

- **Value:** 0.99 (USD less net investment per $1 of online sports betting)
- **Source:** Baker, Balthrop, Johnson, Kotter & Pisciotta; NBER Working Paper 33108, “Gambling Away Stability: Sports Betting's Impact on Vulnerable Households” (2024-11) — [https://www.nber.org/system/files/working_papers/w33108/w33108.pdf](https://www.nber.org/system/files/working_papers/w33108/w33108.pdf)
- **Local copy:** [`data/sources/baker_2024_nber_w33108.pdf`](data/sources/baker_2024_nber_w33108.pdf)
- **Verbatim quotes:**
  - “$1 of online sports betting reduces net investments by $0.99”
  - “robo-advisors that are primarily used for long-term savings”
- **Used in:** Research findings tile `investment_crowd_out` (headline)

### constrained_households

- **Value:** n/a (qualitative) (qualitative)
- **Source:** Baker, Balthrop, Johnson, Kotter & Pisciotta; NBER Working Paper 33108, “Gambling Away Stability: Sports Betting's Impact on Vulnerable Households” (2024-11) — [https://www.nber.org/system/files/working_papers/w33108/w33108.pdf](https://www.nber.org/system/files/working_papers/w33108/w33108.pdf)
- **Local copy:** [`data/sources/baker_2024_nber_w33108.pdf`](data/sources/baker_2024_nber_w33108.pdf)
- **Verbatim quotes:**
  - “credit card debt increases, available credit decreases, and overdraft frequency rises”
- **Used in:** Research findings tile `investment_crowd_out` (text/label)

### ipv

- **Value:** 8.5, 9.6 (% rise in reported intimate partner violence after an NFL home-team upset loss where sports betting is legal (section 5.1, from the Poisson models in Table 1). The paper finds the upset-loss effect is larger where betting is legal (interaction significant at the 10% level).)
- **Source:** Arnesen & Matsuzawa; CHEPS Working Paper 20251001, San Diego State University, “Sports Betting Legalization Amplifies Emotional Cues & Intimate Partner Violence” (2025-10-30) — [https://cheps.sdsu.edu/_resources/docs/working-papers/cheps-wp-20251001.pdf](https://cheps.sdsu.edu/_resources/docs/working-papers/cheps-wp-20251001.pdf)
- **Local copy:** [`data/sources/arnesen_matsuzawa_2025_cheps.pdf`](data/sources/arnesen_matsuzawa_2025_cheps.pdf)
- **Verbatim quotes:**
  - “are higher when sports betting is legal (19% vs. 3.6% increase)”
  - “NFL home team upset losses and reported intimate partner violence (IPV)”
  - “when sports betting is legal, IPVs increase by 8.5 to 9.6%”
  - “legalized gambling increases the impact of upset losses on IPV by 10 percentage points”
  - “about 6 to 7 percentage points larger than in states without sports betting”
  - “upset loss on IPVs by 4.1 to 6.31 percentage points”
  - “states that legalized mobile betting drive our results”
- **Used in:** Research findings tile `ipv` (headline)

### ipv_data

- **Value:** n/a (qualitative) (qualitative (tile label "police reports, 2011-2022"))
- **Source:** Arnesen & Matsuzawa; CHEPS Working Paper 20251001, San Diego State University, “Sports Betting Legalization Amplifies Emotional Cues & Intimate Partner Violence” (2025-10-30) — [https://cheps.sdsu.edu/_resources/docs/working-papers/cheps-wp-20251001.pdf](https://cheps.sdsu.edu/_resources/docs/working-papers/cheps-wp-20251001.pdf)
- **Local copy:** [`data/sources/arnesen_matsuzawa_2025_cheps.pdf`](data/sources/arnesen_matsuzawa_2025_cheps.pdf)
- **Verbatim quotes:**
  - “2011-2022 crime data from NIBRS”
- **Used in:** Research findings tile `ipv` (text/label)

### suicide

- **Value:** 15 (times general-population suicide mortality, people diagnosed with gambling disorder)
- **Source:** Karlsson & Håkansson; Journal of Behavioral Addictions 7(4), 1091-1099, “Gambling disorder, increased mortality, suicidality, and associated comorbidity: A longitudinal nationwide register study” (2018-12) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC6376387/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6376387/)
- **Local copy:** [`data/sources/karlsson_hakansson_2018_pmc.html`](data/sources/karlsson_hakansson_2018_pmc.html)
- **Verbatim quotes:**
  - “a 15-fold increase in suicide mortality”
  - “SMR for suicide indicated a 15.1 times increase for men and women 20-74 years of age”
  - “Men and women 15.1* [8.7 to 21.6]”
- **Used in:** Research findings tile `suicide` (headline)

### nj_venue_disorder

- **Value:** 1.1, 11.3 (% of past-year gamblers screening as probable disorder (high risk): land-based only vs. online only, New Jersey (Table 28). Tile shows 11.3 / 1.1 rounded down to 10x.)
- **Source:** Nower, Stanmyre & Anthony, Rutgers Center for Gambling Studies; report to the New Jersey Division of Gaming Enforcement. Survey fieldwork Dec. 2020 to May 2021., “The Prevalence of Online and Land-Based Gambling in New Jersey (second report)” (2023) — [https://www.nj.gov/oag/ge/2023news/PrevalenceReport2023Final.pdf](https://www.nj.gov/oag/ge/2023news/PrevalenceReport2023Final.pdf)
- **Local copy:** [`data/sources/rutgers_2023_nj_prevalence.pdf`](data/sources/rutgers_2023_nj_prevalence.pdf)
- **Verbatim quotes:**
  - “Table 28. Gambling by Combined Risk Level and Venue”
  - “Probable Disorder (High Risk)”
  - “Online Only 201 67.9 62 20.9 33 11.3”
  - “Land-based Only 872 85.4* 137 13.5 11 1.1”
- **Used in:** Research findings tile `nj_venue_disorder` (headline)

### nj_survey_dates

- **Value:** n/a (qualitative) (qualitative (tile label "2020-21 survey"))
- **Source:** Nower, Stanmyre & Anthony, Rutgers Center for Gambling Studies; report to the New Jersey Division of Gaming Enforcement. Survey fieldwork Dec. 2020 to May 2021., “The Prevalence of Online and Land-Based Gambling in New Jersey (second report)” (2023) — [https://www.nj.gov/oag/ge/2023news/PrevalenceReport2023Final.pdf](https://www.nj.gov/oag/ge/2023news/PrevalenceReport2023Final.pdf)
- **Local copy:** [`data/sources/rutgers_2023_nj_prevalence.pdf`](data/sources/rutgers_2023_nj_prevalence.pdf)
- **Verbatim quotes:**
  - “The fieldwork for the telephone interviews took place between December 9, 2020, and April 30, 2021”
  - “from December 22, 2020, through May 8, 2021”
- **Used in:** Research findings tile `nj_venue_disorder` (text/label)

### ct_helpline

- **Value:** 311, 583 (calls and texts to the CT problem-gambling helpline, Nov. 2020 vs Nov. 2021)
- **Source:** CT Mirror, “CT tracks online gambling closely, but not problem gambling” (2022-01-23) — [https://ctmirror.org/2022/01/23/ct-tracks-online-gambling-closely-but-not-problem-gambling/](https://ctmirror.org/2022/01/23/ct-tracks-online-gambling-closely-but-not-problem-gambling/)
- **Local copy:** [`data/sources/ctmirror_2022_problem_gambling.html`](data/sources/ctmirror_2022_problem_gambling.html)
- **Verbatim quotes:**
  - “Calls and texts in those same months went from 311 to 583, an 87% increase”
- **Used in:** Research findings tile `ct_helpline` (headline)

### pa_helpline

- **Value:** 50 (% of PA 1-800-GAMBLER calls related to online gambling (more than))
- **Source:** Penn State Social Science Research Institute, “Online gambling participation increased in Pennsylvania in 2025, report finds” (2026-01-22) — [https://www.psu.edu/news/social-science-research-institute/story/online-gambling-participation-increased-pennsylvania-2025](https://www.psu.edu/news/social-science-research-institute/story/online-gambling-participation-increased-pennsylvania-2025)
- **Local copy:** [`data/sources/psu_2025_pa_online_gambling.html`](data/sources/psu_2025_pa_online_gambling.html)
- **Verbatim quotes:**
  - “with over 50% of calls related to problematic online gambling”
- **Used in:** Research findings tile `pa_helpline` (headline)

### anj_concentration

- **Value:** 8.7, 60 (% of registered players flagged as likely problem gamblers / % of GGR they produce, second half of 2025, online and account-based gambling in France)
- **Source:** Autorité nationale des jeux (France), “The algorithm developed by the ANJ reveals an alarming and rising number of problem gamblers” (2026-05) — [https://anj.fr/algorithm-developed-anj-reveals-alarming-and-rising-number-problem-gamblers](https://anj.fr/algorithm-developed-anj-reveals-alarming-and-rising-number-problem-gamblers)
- **Local copy:** [`data/sources/anj_2026_excessive_gamblers_algorithm.html`](data/sources/anj_2026_excessive_gamblers_algorithm.html)
- **Verbatim quotes:**
  - “In the second half of 2025, the algorithm identified 600,000 players who are highly likely to be problem gamblers”
  - “representing 8.7% of the total population of registered players”
  - “accounting for 60% of total GGR”
  - “licensed online operators and FDJ and PMU account-based gambling”
- **Used in:** Research findings tile `anj_concentration` (headline)

### md_sb761_withdrawn

- **Value:** n/a (qualitative) (qualitative. Maryland's 2026 internet gaming referendum bill was withdrawn after its hearing was canceled)
- **Source:** Maryland General Assembly, bill record, “SB 761 (2026 session): Expansion of Commercial Gaming - Internet Gaming Referendum” (2026-11-20) — [https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0761?ys=2026RS](https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0761?ys=2026RS)
- **Local copy:** [`data/sources/mga_2026_sb0761.html`](data/sources/mga_2026_sb0761.html)
- **Verbatim quotes:**
  - “Expansion of Commercial Gaming - Internet Gaming Referendum”
  - “In the Senate - Withdrawn by Sponsor”
  - “3/10/2026 Action Hearing canceled”
  - “3/13/2026 Action Withdrawn by Sponsor”
- **Used in:** Article text: Neighbors: Maryland's 2026 online casino referendum bill was withdrawn

### md_hb1343_no_vote

- **Value:** n/a (qualitative) (qualitative. The House online casino bill got a hearing and no further action; its record, retrieved after the session ended, still shows the hearing as its last step. It was also introduced in 2025 as HB 17.)
- **Source:** Maryland General Assembly, bill record (retrieved Nov. 20, 2026, after the session ended April 13, 2026), “HB 1343 (2026 session): Internet Gaming - Authorization and Implementation” (2026-11-20) — [https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/HB1343?ys=2026RS](https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/HB1343?ys=2026RS)
- **Local copy:** [`data/sources/mga_2026_hb1343.html`](data/sources/mga_2026_hb1343.html)
- **Verbatim quotes:**
  - “Internet Gaming - Authorization and Implementation”
  - “In the House - Hearing 3/05 at 1:00 p.m.”
  - “Introduced in a prior session as: HB0017 Session: 2025 Regular Session”
- **Used in:** Article text: Neighbors: Maryland's House online casino bill never got a vote (2025 and 2026)

### md_referendum_required

- **Value:** n/a (qualitative) (qualitative. Online casinos in Maryland would need voter approval in a statewide referendum)
- **Source:** Casino.org, “Maryland iGaming Dead for 2026, Bill to Prohibit Sweepstakes Casinos Remains” (2026-03-24) — [https://www.casino.org/news/maryland-igaming-dead-2026-bill-prohibit-sweepstakes-casinos-remains/](https://www.casino.org/news/maryland-igaming-dead-2026-bill-prohibit-sweepstakes-casinos-remains/)
- **Local copy:** [`data/sources/casinoorg_2026_md_igaming_dead.html`](data/sources/casinoorg_2026_md_igaming_dead.html)
- **Verbatim quotes:**
  - “Such gambling expansion would require voter approval through a statewide ballot referendum”
  - “Watson withdrew Senate Bill 761, the proposed internet gaming referendum”
  - “The regulatory statute is presumably dead with the shelving of SB761”
- **Used in:** Article text: Neighbors: Maryland would need a statewide referendum

### va_2026_no_final_vote

- **Value:** n/a (qualitative) (qualitative. Virginia's House and Senate passed different online casino bills and took no final vote)
- **Source:** Covers. Virginia's legislative information system serves 2026 bill records only through a script-driven site, so no primary record is saved., “Virginia Lawmakers Do Not Approve Online Casino Gaming Bill” (2026-03-16) — [https://www.covers.com/industry/virginia-online-casino-gaming-bill-not-approved-march-16-2026](https://www.covers.com/industry/virginia-online-casino-gaming-bill-not-approved-march-16-2026)
- **Local copy:** [`data/sources/covers_2026_va_igaming_not_approved.html`](data/sources/covers_2026_va_igaming_not_approved.html)
- **Verbatim quotes:**
  - “Virginia lawmakers failed to approve online casino legislation before the 2026 session ended”
  - “The House and Senate passed separate versions of the bill but could not reconcile differences before the legislature adjourned”
  - “there is no longer a route for legal online slots or table games in the commonwealth in 2026”
- **Used in:** Article text: Neighbors: Virginia's 2026 online casino bill died without a final vote

### va_reenactment_clause

- **Value:** n/a (qualitative) (qualitative. Even if passed in 2026, Virginia's bill would have needed a second vote in 2027)
- **Source:** Covers. Virginia's legislative information system serves 2026 bill records only through a script-driven site, so no primary record is saved., “Virginia Lawmakers Do Not Approve Online Casino Gaming Bill” (2026-03-16) — [https://www.covers.com/industry/virginia-online-casino-gaming-bill-not-approved-march-16-2026](https://www.covers.com/industry/virginia-online-casino-gaming-bill-not-approved-march-16-2026)
- **Local copy:** [`data/sources/covers_2026_va_igaming_not_approved.html`](data/sources/covers_2026_va_igaming_not_approved.html)
- **Verbatim quotes:**
  - “If passed in 2026, the legislation would have required lawmakers to approve the bill again in 2027”
  - “the failure to act in 2026 had no impact on a launch timeline”
- **Used in:** Article text: Neighbors: Virginia's bill required a second vote, so 2026 passage would not have launched a market

### pa_igaming_total_fy2425

- **Value:** 2,477,083,825 (USD, Pennsylvania iGaming revenue, fiscal year 2024/25)
- **Source:** Pennsylvania Gaming Control Board, “Pennsylvania Gaming Control Board fiscal year 2025/26 revenue release” (2026-07) — [https://gamingcontrolboard.pa.gov/node/713862](https://gamingcontrolboard.pa.gov/node/713862)
- **Local copy:** [`data/sources/pgcb_fy2526_release.html`](data/sources/pgcb_fy2526_release.html)
- **Verbatim quotes:**
  - “an 18.42% increase in revenue when compared to the $2,477,083,825 generated in Fiscal Year 2024/25”
- **Used in:** Article text: Game mix: Pennsylvania online casino revenue, FY2024/25

### pa_igaming_mix_fy2425

- **Value:** 1,800,000,000, 597,000,000, 29,000,000 (USD, Pennsylvania iGaming revenue by vertical, FY2024/25: slots (rounded to $1.8B in the report), table games, poker. Slots by subtraction from the exact total: about $1.851B (74.7%); tables 24.1%; poker 1.2%.)
- **Source:** Pennsylvania Gaming Control Board, “Pennsylvania Gaming Control Board Annual Report, Fiscal Year 2024/2025” (2025-09) — [https://gamingcontrolboard.pa.gov/sites/default/files/2025-09/PGCB%20Annual%20Report%202024-2025%20FINAL.pdf](https://gamingcontrolboard.pa.gov/sites/default/files/2025-09/PGCB%20Annual%20Report%202024-2025%20FINAL.pdf)
- **Local copy:** [`data/sources/pgcb_annual_report_2024_25.pdf`](data/sources/pgcb_annual_report_2024_25.pdf)
- **Verbatim quotes:**
  - “A breakdown of revenue by three distinct gaming verticals - iSlots, iTables, and iPoker”
  - “interactive slot machine revenue increased to $1.8 billion”
  - “revenue from interactive table games rose to $597 million”
  - “revenue from iPoker increased slightly to $29 million”
- **Used in:** Article text: Game mix: slots are about three-quarters of Pennsylvania online casino revenue

### pa_live_dealer_share

- **Value:** 60 (% of Pennsylvania iTables revenue from live-dealer games, FY2024/25 ("over 60%"). Live dealer is therefore at least 14.5% of all Pennsylvania iGaming revenue (0.60 x $597M / $2,477M) and at most 24.1% (all table revenue): 1.9 to 3.2 times the 7.6% implied by the DC CFO's FY2030 tax figures.)
- **Source:** Pennsylvania Gaming Control Board, “Pennsylvania Gaming Control Board Annual Report, Fiscal Year 2024/2025” (2025-09) — [https://gamingcontrolboard.pa.gov/sites/default/files/2025-09/PGCB%20Annual%20Report%202024-2025%20FINAL.pdf](https://gamingcontrolboard.pa.gov/sites/default/files/2025-09/PGCB%20Annual%20Report%202024-2025%20FINAL.pdf)
- **Local copy:** [`data/sources/pgcb_annual_report_2024_25.pdf`](data/sources/pgcb_annual_report_2024_25.pdf)
- **Verbatim quotes:**
  - “The iTables Live Dealer segment experienced significant growth in popularity among players throughout the fiscal year, now accounting for over 60% of total iTables revenue”
- **Used in:** Article text: Op-ed: the CFO's figures imply a live-dealer share 2-3 times smaller than Pennsylvania's

### dc_committee_vote

- **Value:** 3, 1 (Human Services Committee vote on B26-0656, Wednesday, Nov. 18, 2026 (for, against))
- **Source:** Covers, “DC Online Casino Bill Advances Out of Council Committee” (2026-11-18) — [https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026](https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026)
- **Local copy:** [`data/sources/covers_2026_dc_igaming_committee.html`](data/sources/covers_2026_dc_igaming_committee.html)
- **Verbatim quotes:**
  - “The bill passed out of the Human Services Committee 3-1, with Councilmembers Wendell Felder, Matt Frumin, and Zachary Parker voting in favor”
  - “Christina Henderson opposed the measure”
  - “Wednesday's vote moves the legislation toward consideration by the full council”
- **Used in:** Article text: Op-ed: B26-0656 cleared committee Nov. 18 on a 3-1 vote

### dc_unlimited_operators

- **Value:** n/a (qualitative) (qualitative. The bill sets no cap on the number of licensed operators)
- **Source:** Covers, “DC Online Casino Bill Advances Out of Council Committee” (2026-11-18) — [https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026](https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026)
- **Local copy:** [`data/sources/covers_2026_dc_igaming_committee.html`](data/sources/covers_2026_dc_igaming_committee.html)
- **Verbatim quotes:**
  - “The proposal would allow unlimited qualified online casino operators”
- **Used in:** Article text: Op-ed: the bill allows multiple operators

### fis_expedited_review

- **Value:** n/a (qualitative) (qualitative. Existing sports-wagering licensees get expedited review for an operator license)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Entities that already have a valid sports wagering Class A”
  - “are entitled to an expedited review”
- **Used in:** Article text: Op-ed: the bill gives sportsbook incumbents a leg up

### fis_player_location

- **Value:** n/a (qualitative) (qualitative. Internet games may be offered only to players physically in DC or in another jurisdiction that permits it)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “The bill requires internet gaming to be offered only when a player is physically located in the District (or in another jurisdiction that permits it)”
- **Used in:** Article text: Op-ed: games are playable only in DC or other jurisdictions that permit it

### reia_reciprocal_agreements

- **Value:** n/a (qualitative) (qualitative. The Mayor may sign reciprocal agreements letting players in other jurisdictions bet with DC operators)
- **Source:** DC Council Office of Racial Equity (via DC Council LIMS), “Racial Equity Impact Assessment: Committee Print, Bill 26-0656” (2026-11) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282)
- **Local copy:** [`data/sources/lims_b26_0656_reia_committee_print.pdf`](data/sources/lims_b26_0656_reia_committee_print.pdf)
- **Verbatim quotes:**
  - “The Mayor may enter into reciprocal agreements with other jurisdictions for internet gaming”
  - “to place wagers with an operator licensed in the District”
- **Used in:** Article text: Op-ed: out-of-state play runs through reciprocal agreements

### reia_revenue_from_residents

- **Value:** n/a (qualitative) (qualitative. The Council's racial equity office expects the revenue to come from DC residents' losses)
- **Source:** DC Council Office of Racial Equity (via DC Council LIMS), “Racial Equity Impact Assessment: Committee Print, Bill 26-0656” (2026-11) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282)
- **Local copy:** [`data/sources/lims_b26_0656_reia_committee_print.pdf`](data/sources/lims_b26_0656_reia_committee_print.pdf)
- **Verbatim quotes:**
  - “gambling revenue ultimately comes from District residents placing bets and losing”
- **Used in:** Article text: Op-ed: most revenue would likely come from residents

### council_period_26

- **Value:** n/a (qualitative) (qualitative. Council Period 26 covers 2025-2026)
- **Source:** DC Council Office of Racial Equity (via DC Council LIMS), “Racial Equity Impact Assessment: Committee Print, Bill 26-0656” (2026-11) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282)
- **Local copy:** [`data/sources/lims_b26_0656_reia_committee_print.pdf`](data/sources/lims_b26_0656_reia_committee_print.pdf)
- **Verbatim quotes:**
  - “During Council Period 26 (from 2025-2026)”
- **Used in:** Article text: Op-ed: time left in the Council period

### council_2026_remaining_meetings

- **Value:** n/a (qualitative) (qualitative. Remaining 2026 meetings after markup: Committee of the Whole Nov. 24 (filing deadline Nov. 18), legislative meeting Dec. 1, Committee of the Whole and legislative meeting Dec. 15; recess Dec. 23-31)
- **Source:** Council of the District of Columbia, “2026 Legislative Meeting and Committee of the Whole Meeting schedule” (2026-01-20) — [https://dccouncil.gov/wp-content/uploads/2026/01/2026-LEGISLATIVE-COW-Meetings-1-20-26.pdf](https://dccouncil.gov/wp-content/uploads/2026/01/2026-LEGISLATIVE-COW-Meetings-1-20-26.pdf)
- **Local copy:** [`data/sources/dccouncil_2026_legislative_calendar.pdf`](data/sources/dccouncil_2026_legislative_calendar.pdf)
- **Verbatim quotes:**
  - “NOVEMBER 24 (Nov. 18)”
  - “DECEMBER 1 (Nov. 25”
  - “DECEMBER 15 (Dec. 9)”
  - “Recess - December 23 through December 31”
- **Used in:** Article text: Op-ed: Council calendar for the rest of 2026

### gambetdc_sole_source

- **Value:** 215,000,000 (USD, Intralot's sole-source lottery contract that included the citywide sports-betting app)
- **Source:** DCist, “D.C.'s sports betting app is still underperforming” (2022-03-03) — [https://dcist.com/story/22/03/03/dc-lottery-app-underperforms/](https://dcist.com/story/22/03/03/dc-lottery-app-underperforms/)
- **Local copy:** [`data/sources/dcist_2022_lottery_app_underperforms.html`](data/sources/dcist_2022_lottery_app_underperforms.html)
- **Verbatim quotes:**
  - “a $215 million sole-source contract to develop and run the only sports-betting app”
- **Used in:** Article text: Op-ed: the sports-betting operator got a sole-source, no-bid contract

### intralot_settlement

- **Value:** 6,500,000 (USD, combined settlement paid by Intralot and Veterans Services Corporation to resolve the Attorney General's case over DC contracting laws (no admission of wrongdoing))
- **Source:** Washington City Paper, “The Companies Behind D.C.'s Sports Betting Deal Will Pay $6.5 Million Over Charges They Misled Regulators” (2025-01-14) — [https://washingtoncitypaper.com/article/756194/the-companies-behind-d-c-s-sports-betting-deal-will-pay-6-5-million-over-charges-they-misled-regulators/](https://washingtoncitypaper.com/article/756194/the-companies-behind-d-c-s-sports-betting-deal-will-pay-6-5-million-over-charges-they-misled-regulators/)
- **Local copy:** [`data/sources/wcp_2025_intralot_vsc_settlement.html`](data/sources/wcp_2025_intralot_vsc_settlement.html)
- **Verbatim quotes:**
  - “have agreed to pay the city a combined $6.5 million to settle a case pursued by Attorney General Brian Schwalb over alleged violations of D.C. contracting laws”
  - “Although the two companies do not admit wrongdoing”
  - “while circumventing the District's small business contracting laws”
  - “submitted more than 100 "fraudulent invoices" to city agencies by 2021”
- **Used in:** Article text: Op-ed: $6.5 million settlement over charges the companies misled regulators

### gambetdc_super_bowl_outage

- **Value:** n/a (qualitative) (qualitative. GambetDC didn't work on Apple devices for the whole 2022 Super Bowl)
- **Source:** DCist, “D.C.'s Troubled Sports-Betting App Didn't Work During The Super Bowl” (2022-02-14) — [https://dcist.com/story/22/02/14/dc-sports-betting-app-failed-super-bowl](https://dcist.com/story/22/02/14/dc-sports-betting-app-failed-super-bowl)
- **Local copy:** [`data/sources/dcist_2022_gambetdc_super_bowl.html`](data/sources/dcist_2022_gambetdc_super_bowl.html)
- **Verbatim quotes:**
  - “did not work for users of Apple phones and tablets during the entirety of the Super Bowl”
- **Used in:** Article text: Op-ed: GambetDC's operational failures

### gambetdc_super_bowl_compensation

- **Value:** 500,000 (USD, compensation Intralot paid the DC Lottery for the Super Bowl outage)
- **Source:** DCist, “Sports-Betting App Pays D.C. $500,000 Over Super Bowl Mishap” (2022-04-08) — [https://dcist.com/story/22/04/08/dc-get-compensation-for-sports-betting-app-mishap](https://dcist.com/story/22/04/08/dc-get-compensation-for-sports-betting-app-mishap)
- **Local copy:** [`data/sources/dcist_2022_gambetdc_compensation.html`](data/sources/dcist_2022_gambetdc_compensation.html)
- **Verbatim quotes:**
  - “The D.C. Lottery has received $500,000 in compensation from the operator of the city's official sports-betting app”
  - “criticized as clunky since it launched in mid-2020”
- **Used in:** Article text: Op-ed: GambetDC's operational failures

### betting_apps_perks_and_limits

- **Value:** n/a (qualitative) (qualitative. Sports-betting apps give perks to heavy losers and cap the bets of winners)
- **Source:** CBS News, “Online betting companies lavish losers with rewards while capping winners” (2026-10-26) — [https://www.cbsnews.com/news/online-betting-apps-losers-perks-limiting-winners/](https://www.cbsnews.com/news/online-betting-apps-losers-perks-limiting-winners/)
- **Local copy:** [`data/sources/cbs_2026_betting_apps_losers_winners.html`](data/sources/cbs_2026_betting_apps_losers_winners.html)
- **Verbatim quotes:**
  - “extravagant perks to customers who are losing large sums of money”
  - “a tactic sports betting platforms use to apply the brakes to gamblers who are having too much success”
- **Used in:** Article text: Op-ed: apps take a more predatory approach than casinos

### us_igaming_states

- **Value:** 7, 8 (US states with live / legalized real-money online casinos. Eight have legalized them; Maine (January 2026) has no launch date, so seven are live)
- **Source:** Casino.org (page updated Nov. 16, 2026; saved from a browser Nov. 22, 2026), “Best gambling sites in the US 2026” (2026-11-16) — [https://www.casino.org/us/gambling/](https://www.casino.org/us/gambling/)
- **Local copy:** [`data/sources/casinoorg_2026_us_gambling.pdf`](data/sources/casinoorg_2026_us_gambling.pdf)
- **Verbatim quotes:**
  - “Eight US states have legalized real-money online casinos”
  - “Pennsylvania, Michigan, New Jersey, West Virginia, Delaware, Connecticut, Rhode Island, and Maine”
  - “Maine legalized online casinos in January 2026, but there's no confirmed launch date yet”
- **Used in:** Article text: Op-ed: only seven states (with Maine set to join)

### ga_chinatown_meeting

- **Value:** n/a (qualitative) (qualitative. Tuesday 7 p.m. Gamblers Anonymous meeting at Second Baptist Church, 816 3rd St. NW, near Chinatown. Listed as a closed meeting)
- **Source:** Gamblers Anonymous meeting directory (saved from a browser Nov. 22, 2026), “Washington D.C. G.A. - Tuesday (meeting listing)” (2026-11-22) — [https://gamblersanonymous.org/](https://gamblersanonymous.org/)
- **Local copy:** [`data/sources/ga_2026_dc_meetings.pdf`](data/sources/ga_2026_dc_meetings.pdf)
- **Verbatim quotes:**
  - “Walkable from Chinatown and Judiciary Square Metro Stations”
  - “816 3rd St. NW”
  - “Closed Meeting”
- **Used in:** Article text: Op-ed: a Gamblers Anonymous meeting in Chinatown

### dc_igaming_2012_repeal

- **Value:** 10, 2 (DC Council vote to repeal online gambling, Feb. 7, 2012 (for repeal, against). Legalized the year before in a budget bill; never launched)
- **Source:** WTOP, “Curses! Profanity punctuates D.C.'s repeal of online gambling” (2012-02-07) — [https://wtop.com/news/2012/02/curses-profanity-punctuates-dcs-repeal-of-online-gambling](https://wtop.com/news/2012/02/curses-profanity-punctuates-dcs-repeal-of-online-gambling)
- **Local copy:** [`data/sources/wtop_2012_dc_repeals_online_gambling.html`](data/sources/wtop_2012_dc_repeals_online_gambling.html)
- **Verbatim quotes:**
  - “The D.C. Council voted 10-2 to repeal the nation's first government-sponsored online gambling program Tuesday”
  - “Online gambling was legalized in the nation's capital last year, but the program was never implemented”
  - “The program was then legalized as part of a budget bill that was approved without public comment”
- **Used in:** Article text: Op-ed: DC legalized and then repealed online gambling in 2011-12

### dc_budget_gap_fy2027

- **Value:** 1,100,000,000, 837,000,000 (USD. FY2027 budget gap the Mayor's proposal closed; projected "budget cliff" the Mayor says the Council's budget leaves for the next year (recurring programs funded with one-time money))
- **Source:** NBC4 Washington, “Bowser declines to sign budget, saying it will leave city with 'fiscal cliff'” (2026-07-29) — [https://www.nbcwashington.com/news/local/bowser-refuses-to-sign-2027-budget-says-it-will-leave-city-with-fiscal-cliff/4135318/](https://www.nbcwashington.com/news/local/bowser-refuses-to-sign-2027-budget-says-it-will-leave-city-with-fiscal-cliff/4135318/)
- **Local copy:** [`data/sources/nbc4_2026_bowser_budget_fiscal_cliff.html`](data/sources/nbc4_2026_bowser_budget_fiscal_cliff.html)
- **Verbatim quotes:**
  - “in an effort to cut costs amid a $1 billion budget gap”
  - “Bowser said her proposal closed a $1.1 billion gap through spending reductions, budgetary savings and the use of prior-year surplus”
  - “which she said will leave the next mayor and council with a "$837 million budget cliff."”
  - “concerns over the budget funding recurring programs with one-time money”
- **Used in:** Article text: Op-ed: DC faces a budget gap of nearly $1 billion

### fy2027_fund_balance_use

- **Value:** 597,500,000 (USD of fund balance (savings) used to balance the FY2027 local budget as proposed)
- **Source:** DC Office of the Chief Financial Officer, “Fiscal Impact Statement - Fiscal Year 2027 Local Budget Act of 2026” (2026-04-13) — [https://app.cfo.dc.gov/services/fiscal_impact/pdf/spring09/FIS%20FY%202027%20Local%20Budget%20Act.pdf](https://app.cfo.dc.gov/services/fiscal_impact/pdf/spring09/FIS%20FY%202027%20Local%20Budget%20Act.pdf)
- **Local copy:** [`data/sources/ocfo_2026_fis_fy2027_local_budget.pdf`](data/sources/ocfo_2026_fis_fy2027_local_budget.pdf)
- **Verbatim quotes:**
  - “$597.5 million of fund balance use”
- **Used in:** Article text: Op-ed: DC is spending down savings

### local25_dues_rate_2025

- **Value:** 59.92, 105 (USD per member per month, regular dues range (LM-2 item 21))
- **Source:** U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2025 (file no. 506-434)” (2025-12-31) — [https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form](https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form)
- **Local copy:** [`data/sources/olms_lm2_local25_937902.html`](data/sources/olms_lm2_local25_937902.html)
- **Verbatim quotes:**
  - “PERIOD COVERED From 01/01/2025 Through 12/31/2025”
  - “FILE NUMBER: 506-434”
  - “Regular Dues/Fees $59.92-$105.00 per Member per Month”
- **Used in:** Sankey input `constants.union_dues_per_member`; Sankey fine print (dues basis)

### local25_dues_receipts_2025

- **Value:** 7,772,376 (USD, dues and agency fees received in 2025 (LM-2 item 36))
- **Source:** U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2025 (file no. 506-434)” (2025-12-31) — [https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form](https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form)
- **Local copy:** [`data/sources/olms_lm2_local25_937902.html`](data/sources/olms_lm2_local25_937902.html)
- **Verbatim quotes:**
  - “36. Dues and Agency Fees $7,772,376”
- **Used in:** Sankey input `constants.union_dues_per_member`; Sankey fine print (dues basis)

### local25_members_2025

- **Value:** 6,101 (members at end of 2025 (LM-2 item 20; 0 agency fee payers))
- **Source:** U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2025 (file no. 506-434)” (2025-12-31) — [https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form](https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form)
- **Local copy:** [`data/sources/olms_lm2_local25_937902.html`](data/sources/olms_lm2_local25_937902.html)
- **Verbatim quotes:**
  - “How many members did the labor organization have at the end of the reporting period? 6,101”
  - “Agency Fee Payers* 0”
- **Used in:** Sankey input `constants.union_dues_per_member`; Sankey fine print (dues basis)

### local25_2024

- **Value:** 6,863,160, 5,349 (2024 dues receipts (USD) and year-end members, for consistency check)
- **Source:** U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2024 (file no. 506-434)” (2024-12-31) — [https://olmsapps.dol.gov/query/orgReport.do?rptId=912430&rptForm=LM2Form](https://olmsapps.dol.gov/query/orgReport.do?rptId=912430&rptForm=LM2Form)
- **Local copy:** [`data/sources/olms_lm2_local25_912430.html`](data/sources/olms_lm2_local25_912430.html)
- **Verbatim quotes:**
  - “PERIOD COVERED From 01/01/2024 Through 12/31/2024”
  - “36. Dues and Agency Fees $6,863,160”
  - “How many members did the labor organization have at the end of the reporting period? 5,349”
- **Used in:** Cross-check only (dues per member in prior years); not displayed

### local25_2023

- **Value:** 6,324,236, 4,953 (2023 dues receipts (USD) and year-end members, for consistency check)
- **Source:** U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2023 (file no. 506-434)” (2023-12-31) — [https://olmsapps.dol.gov/query/orgReport.do?rptId=888264&rptForm=LM2Form](https://olmsapps.dol.gov/query/orgReport.do?rptId=888264&rptForm=LM2Form)
- **Local copy:** [`data/sources/olms_lm2_local25_888264.html`](data/sources/olms_lm2_local25_888264.html)
- **Verbatim quotes:**
  - “PERIOD COVERED From 01/01/2023 Through 12/31/2023”
  - “36. Dues and Agency Fees $6,324,236”
  - “How many members did the labor organization have at the end of the reporting period? 4,953”
- **Used in:** Cross-check only (dues per member in prior years); not displayed

### iit_fy2026

- **Value:** 3,699,357,000 (USD, FY2026 DC individual income tax estimate (Table 1, $ in thousands))
- **Source:** DC Office of the Chief Financial Officer, “June 2026 Revenue Estimates (letter to the Mayor and Council)” (2026-06-30) — [https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/publication/attachments/June%202026%20Revenue_Estimate%20Letter%20063026.pdf](https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/publication/attachments/June%202026%20Revenue_Estimate%20Letter%20063026.pdf)
- **Local copy:** [`data/sources/ocfo_2026_june_revenue_estimate.pdf`](data/sources/ocfo_2026_june_revenue_estimate.pdf)
- **Verbatim quotes:**
  - “TABLE 1: REVENUE SUMMARY TABLE $ in Thousands ACTUAL FY2025 FY2026 FY2027 FY2028 FY2029 FY2030”
  - “Individual Income 3,605,177 3,699,357”
- **Used in:** Sankey input `constants.fy26_individual_income_tax`

### baker_data

- **Value:** n/a (qualitative) (qualitative (tile label "bank transactions"))
- **Source:** Baker, Balthrop, Johnson, Kotter & Pisciotta; NBER Working Paper 33108, “Gambling Away Stability: Sports Betting's Impact on Vulnerable Households” (2024-11) — [https://www.nber.org/system/files/working_papers/w33108/w33108.pdf](https://www.nber.org/system/files/working_papers/w33108/w33108.pdf)
- **Local copy:** [`data/sources/baker_2024_nber_w33108.pdf`](data/sources/baker_2024_nber_w33108.pdf)
- **Verbatim quotes:**
  - “using household transaction data and a staggered difference-in-differences framework”
- **Used in:** Research findings tile `investment_crowd_out` (text/label)

### karlsson_data

- **Value:** 2,099 (people with a gambling disorder diagnosis (tile label "Sweden"))
- **Source:** Karlsson & Håkansson; Journal of Behavioral Addictions 7(4), 1091-1099, “Gambling disorder, increased mortality, suicidality, and associated comorbidity: A longitudinal nationwide register study” (2018-12) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC6376387/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6376387/)
- **Local copy:** [`data/sources/karlsson_hakansson_2018_pmc.html`](data/sources/karlsson_hakansson_2018_pmc.html)
- **Verbatim quotes:**
  - “2,099 individuals with a GD diagnosis in the Swedish inpatient and/or outpatient specialist health care system”
- **Used in:** Research findings tile `suicide` (text/label)

### ct_products

- **Value:** n/a (qualitative) (qualitative (tile label "Online casino + sports betting"))
- **Source:** CT Mirror, “CT tracks online gambling closely, but not problem gambling” (2022-01-23) — [https://ctmirror.org/2022/01/23/ct-tracks-online-gambling-closely-but-not-problem-gambling/](https://ctmirror.org/2022/01/23/ct-tracks-online-gambling-closely-but-not-problem-gambling/)
- **Local copy:** [`data/sources/ctmirror_2022_problem_gambling.html`](data/sources/ctmirror_2022_problem_gambling.html)
- **Verbatim quotes:**
  - “the launch of sports betting and online casino gambling”
- **Used in:** Research findings tile `ct_helpline` (text/label)

### pa_products

- **Value:** n/a (qualitative) (qualitative (tile label "Online casino + sports betting"))
- **Source:** Penn State Social Science Research Institute, “Online gambling participation increased in Pennsylvania in 2025, report finds” (2026-01-22) — [https://www.psu.edu/news/social-science-research-institute/story/online-gambling-participation-increased-pennsylvania-2025](https://www.psu.edu/news/social-science-research-institute/story/online-gambling-participation-increased-pennsylvania-2025)
- **Local copy:** [`data/sources/psu_2025_pa_online_gambling.html`](data/sources/psu_2025_pa_online_gambling.html)
- **Verbatim quotes:**
  - “sports betting companies and online casinos”
- **Used in:** Research findings tile `pa_helpline` (text/label)

### fis_scope

- **Value:** n/a (qualitative) (which bill version the CFO's fiscal impact statement scores)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Draft Committee Print as provided to the Office of Revenue Analysis on November 17, 2026”
  - “FY 2027- FY 2030 ($ in thousands)”
- **Used in:** Sankey headline/fine print (tax base and net gain)

### fis_tax_rates

- **Value:** 0.25, 0.125 (tax rate on adjusted gross internet gaming revenue; live-dealer rate)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “taxed at 25 percent, except for live-dealer gaming which is taxed at 12.5 percent”
- **Used in:** Sankey input `constants.tax_rate`; Sankey input `constants.live_dealer_tax_rate`

### fis_agr_definition

- **Value:** n/a (qualitative) (definition of the tax base)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Adjusted gross gaming revenue is defined as gross internet gaming revenue minus winnings and cancelled, voided, or refunded wagers”
- **Used in:** Sankey headline/fine print (tax base and net gain)

### print_promo_credits

- **Value:** n/a (qualitative) (promotional credits are not counted as wagers (so the tax base equals players' net cash losses))
- **Source:** DC Council Office of Racial Equity (via DC Council LIMS), “Racial Equity Impact Assessment: Committee Print, Bill 26-0656” (2026-11) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282)
- **Local copy:** [`data/sources/lims_b26_0656_reia_committee_print.pdf`](data/sources/lims_b26_0656_reia_committee_print.pdf)
- **Verbatim quotes:**
  - “RACIAL EQUITY IMPACT ASSESSMENT: COMMITTEE PRINT, BILL 26-0656”
  - “Total amount of money and cash equivalents wagered by patrons on internet games; provided that promotional gaming credits are not treated as wagers unless required for accounting or auditing”
- **Used in:** Sankey headline/fine print (tax base and net gain)

### print_tax_rates

- **Value:** 0.25, 0.125 (same rates as stated in the committee-print assessment (cross-check))
- **Source:** DC Council Office of Racial Equity (via DC Council LIMS), “Racial Equity Impact Assessment: Committee Print, Bill 26-0656” (2026-11) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282)
- **Local copy:** [`data/sources/lims_b26_0656_reia_committee_print.pdf`](data/sources/lims_b26_0656_reia_committee_print.pdf)
- **Verbatim quotes:**
  - “Operators must pay 25% of their adjusted gross internet gaming revenue each month, with live-dealer gross revenue taxed at 12.5%”
- **Used in:** Sankey input `constants.tax_rate`; Sankey input `constants.live_dealer_tax_rate`

### fis_promo_cap

- **Value:** 0.0175 (cap on promotional gaming credits as a share of adjusted gross revenue)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Promotional gaming credits, including free wagers to attract customers, may not exceed 1.75 percent of an operators adjusted gross internet gaming revenue for the fiscal year”
- **Used in:** Sankey headline/fine print (tax base and net gain)

### fis_setaside

- **Value:** 750,000 (USD per year, first tax dollars to the Department of Behavioral Health)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “annually the first $750,000 of tax revenue in the Fund will be transferred to the Department of Behavioral Health (DBH)”
- **Used in:** Sankey input `constants.treatment_setaside`

### fis_community_impact

- **Value:** 0.02 (community impact assessment, share of adjusted gross revenue, and its uses)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “of two percent of adjusted gross internet gaming revenue to the District, which will also be deposited in the Fund”
  - “30 percent to DISB for debt management, financial counseling, consumer financial protection, and financial literacy programs and services”
  - “30 percent to the Office of Victim Services and Justice Grants (OVSJG), for domestic violence, intimate partner violence, survivor services, and family stability programs”
- **Used in:** Sankey input `constants.assessment_rate`

### fis_regulatory_assessment

- **Value:** 0.02 (regulatory assessment, share of adjusted gross revenue (funds OLG regulation))
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “of two percent of their adjusted gross internet gaming revenue to the District, to be deposited into a dedicated account in the General Fund”
  - “The Regulatory Assessment will be used solely for the administration, regulation, and enforcement of the bill by OLG”
- **Used in:** Sankey input `constants.assessment_rate`

### fis_live_dealer_requirements

- **Value:** n/a (qualitative) (live-dealer games required and must be played in a DC studio)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Applicants seeking to become Operators are required to offer live-dealer games”
  - “The bill requires all live-dealer games to be conducted at a physical studio in the District”
- **Used in:** Sankey input `scenarios.central.jobs`

### fis_cbe_requirement

- **Value:** 0.35 (share of DC-related operating budget to be contracted with certified local businesses (waivable))
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “at least 35 percent of the applicant's District-related operating budget for internet gaming will be contracted with one or more CBEs”
  - “If DSLBD does not deny or approve a waiver request within 30 days after submission, the waiver will be deemed approved”
- **Used in:** Sankey input `scenarios.central.local_vendor_spend`

### fis_tax_fy2030

- **Value:** 16,056,000 (USD, FY2030 tax on gaming revenue (FY2028 15,499; FY2029 15,758; $ thousands))
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Tax on gaming revenue(c) $0 $15,499 $15,758 $16,056 $47,314”
- **Used in:** Sankey input `scenarios.central.tax_revenue`

### fis_regulatory_fy2030

- **Value:** 1,335,000 (USD, FY2030 regulatory assessment revenue)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Regulatory Assessment (dedicated to OLG)(f) $0 $1,288 $1,310 $1,335 $3,932”
- **Used in:** Sankey input `scenarios.central.regulatory_assessment`

### fis_community_impact_fy2030

- **Value:** 1,335,000 (USD, FY2030 community impact assessment revenue)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Dedicated Tax - Community Impact Assessment(g) $0 $1,288 $1,310 $1,335 $3,932”
- **Used in:** Sankey input `scenarios.central.community_impact`

### fis_license_fy2030

- **Value:** 160,000 (USD, FY2030 license fee revenue (FY2028 includes one-time operator fees of $12.3M))
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “License Fee Revenue (b) $0 $12,320 $160 $160 $12,640”
- **Used in:** Sankey input `scenarios.central.license_fees`

### fis_lottery_loss_fy2030

- **Value:** 1,130,000 (USD, FY2030 decrease in lottery earnings)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Decrease in lottery earnings(d) $0 ($1,149) ($1,139) ($1,130) ($3,417)”
  - “as well as a reduction in traditional Lottery earnings”
- **Used in:** Sankey input `scenarios.central.lottery_loss`

### fis_sports_loss_fy2030

- **Value:** 520,000 (USD, FY2030 decrease in sports wagering taxes (legal age rises to 21))
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Decrease in sports wagering taxes(e) ($246) ($500) ($508) ($520) ($1,774)”
- **Used in:** Sankey input `scenarios.central.sports_wagering_loss`

### fis_olg_costs_fy2030

- **Value:** 1,335,000 (USD, FY2030 OLG regulatory costs)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “OLG Regulatory Costs ($1,288) ($1,310) ($1,335) ($3,932)”
- **Used in:** Sankey input `scenarios.central.olg_regulatory_costs`

### fis_net_impact_fy2030

- **Value:** 15,901,000 (USD, FY2030 net impact on District resources)
- **Source:** DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) — [https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301)
- **Local copy:** [`data/sources/lims_b26_0656_fis.pdf`](data/sources/lims_b26_0656_fis.pdf)
- **Verbatim quotes:**
  - “Net Impact on Resources ($246) $27,459 $15,580 $15,901 $58,694”
- **Used in:** Projections chart bar; Sankey headline/fine print (tax base and net gain)

## 5. Source register

| ID | Citation | URL | File | sha256 (prefix) | How obtained |
|---|---|---|---|---|---|
| `dcist_2022` | DCist, “D.C.'s sports betting app is still underperforming” (2022-03-03) | [link](https://dcist.com/story/22/03/03/dc-lottery-app-underperforms/) | `dcist_2022_lottery_app_underperforms.html` | `5e1c7d020c46…` | downloaded |
| `casinoorg_2021` | Casino.org (citing DCist), “GamBetDC, Controversial Washington DC Sports Bet App, Lost $4M Last Year” (2022-03) | [link](https://www.casino.org/news/controversial-dc-sport-betting-app-gambetdc-lost-4-million-last-year/) | `casinoorg_2021_gambetdc_lost_4m.html` | `dfc6df648f8f…` | downloaded |
| `olg_fy21_22` | DC Office of the Chief Financial Officer, “Office of Lottery and Gaming, FY21-22 Performance Oversight Hearing Presentation” (2022-03) | [link](https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/release_content/attachments/OLG%20FY21-22%20Performance%20Oversight%20Hearing%20Presentation.pdf) | `olg_fy21_22_oversight_presentation.pdf` | `602380c971a7…` | downloaded |
| `olg_fy22_23` | DC Office of the Chief Financial Officer, “Office of Lottery and Gaming, 2022-2023 Performance Oversight Hearing Testimony Slides” (2023-02) | [link](https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/release_content/attachments/OLG%202022-2023%20Performance%20Oversight%20Hearing%20Testimony%20Slides.pdf) | `olg_fy22_23_oversight_slides.pdf` | `c87d68fa5fbc…` | downloaded |
| `axios_2026` | Axios DC, “D.C. moves to expand legal gambling with online gaming” (2026-11-18) | [link](https://www.axios.com/local/washington-dc/2026/11/18/online-gaming-dc-gambling) | `axios_2026_dc_online_gaming.pdf` | `8b3baea5096c…` | manual |
| `covers_2026` | Covers, “DC Online Casino Bill Advances Out of Council Committee” (2026-11-18) | [link](https://www.covers.com/industry/dc-igaming-bill-advances-council-committee-november-18-2026) | `covers_2026_dc_igaming_committee.html` | `61c8bbdf70bf…` | downloaded |
| `mga_2026_sb0761` | Maryland General Assembly, bill record, “SB 761 (2026 session): Expansion of Commercial Gaming - Internet Gaming Referendum” (2026-11-20) | [link](https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0761?ys=2026RS) | `mga_2026_sb0761.html` | `ea522e41c21b…` | downloaded |
| `mga_2026_hb1343` | Maryland General Assembly, bill record (retrieved Nov. 20, 2026, after the session ended April 13, 2026), “HB 1343 (2026 session): Internet Gaming - Authorization and Implementation” (2026-11-20) | [link](https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/HB1343?ys=2026RS) | `mga_2026_hb1343.html` | `a447e2e3b260…` | downloaded |
| `casinoorg_2026_md` | Casino.org, “Maryland iGaming Dead for 2026, Bill to Prohibit Sweepstakes Casinos Remains” (2026-03-24) | [link](https://www.casino.org/news/maryland-igaming-dead-2026-bill-prohibit-sweepstakes-casinos-remains/) | `casinoorg_2026_md_igaming_dead.html` | `fa6349fa6d4e…` | downloaded |
| `covers_2026_va` | Covers. Virginia's legislative information system serves 2026 bill records only through a script-driven site, so no primary record is saved., “Virginia Lawmakers Do Not Approve Online Casino Gaming Bill” (2026-03-16) | [link](https://www.covers.com/industry/virginia-online-casino-gaming-bill-not-approved-march-16-2026) | `covers_2026_va_igaming_not_approved.html` | `6f8dcd9a3a7c…` | downloaded |
| `pgcb_ar_2025` | Pennsylvania Gaming Control Board, “Pennsylvania Gaming Control Board Annual Report, Fiscal Year 2024/2025” (2025-09) | [link](https://gamingcontrolboard.pa.gov/sites/default/files/2025-09/PGCB%20Annual%20Report%202024-2025%20FINAL.pdf) | `pgcb_annual_report_2024_25.pdf` | `7cbaf2733aac…` | downloaded |
| `pgcb_fy2526` | Pennsylvania Gaming Control Board, “Pennsylvania Gaming Control Board fiscal year 2025/26 revenue release” (2026-07) | [link](https://gamingcontrolboard.pa.gov/node/713862) | `pgcb_fy2526_release.html` | `72c0164b1bad…` | downloaded |
| `wcp_2025` | Washington City Paper, “The Companies Behind D.C.'s Sports Betting Deal Will Pay $6.5 Million Over Charges They Misled Regulators” (2025-01-14) | [link](https://washingtoncitypaper.com/article/756194/the-companies-behind-d-c-s-sports-betting-deal-will-pay-6-5-million-over-charges-they-misled-regulators/) | `wcp_2025_intralot_vsc_settlement.html` | `d61ed6f49edc…` | downloaded |
| `cbs_2026` | CBS News, “Online betting companies lavish losers with rewards while capping winners” (2026-10-26) | [link](https://www.cbsnews.com/news/online-betting-apps-losers-perks-limiting-winners/) | `cbs_2026_betting_apps_losers_winners.html` | `71f5c828ec56…` | downloaded |
| `wtop_2012` | WTOP, “Curses! Profanity punctuates D.C.'s repeal of online gambling” (2012-02-07) | [link](https://wtop.com/news/2012/02/curses-profanity-punctuates-dcs-repeal-of-online-gambling) | `wtop_2012_dc_repeals_online_gambling.html` | `714be3259b5c…` | downloaded |
| `ocfo_fis_fy27_budget` | DC Office of the Chief Financial Officer, “Fiscal Impact Statement - Fiscal Year 2027 Local Budget Act of 2026” (2026-04-13) | [link](https://app.cfo.dc.gov/services/fiscal_impact/pdf/spring09/FIS%20FY%202027%20Local%20Budget%20Act.pdf) | `ocfo_2026_fis_fy2027_local_budget.pdf` | `38e5764c8549…` | downloaded |
| `dcist_2022_superbowl` | DCist, “D.C.'s Troubled Sports-Betting App Didn't Work During The Super Bowl” (2022-02-14) | [link](https://dcist.com/story/22/02/14/dc-sports-betting-app-failed-super-bowl) | `dcist_2022_gambetdc_super_bowl.html` | `d87e2882ac01…` | downloaded |
| `dcist_2022_compensation` | DCist, “Sports-Betting App Pays D.C. $500,000 Over Super Bowl Mishap” (2022-04-08) | [link](https://dcist.com/story/22/04/08/dc-get-compensation-for-sports-betting-app-mishap) | `dcist_2022_gambetdc_compensation.html` | `05bed71a9ef7…` | downloaded |
| `dccouncil_2026_calendar` | Council of the District of Columbia, “2026 Legislative Meeting and Committee of the Whole Meeting schedule” (2026-01-20) | [link](https://dccouncil.gov/wp-content/uploads/2026/01/2026-LEGISLATIVE-COW-Meetings-1-20-26.pdf) | `dccouncil_2026_legislative_calendar.pdf` | `740503af3ec7…` | downloaded |
| `nbc4_2026_budget` | NBC4 Washington, “Bowser declines to sign budget, saying it will leave city with 'fiscal cliff'” (2026-07-29) | [link](https://www.nbcwashington.com/news/local/bowser-refuses-to-sign-2027-budget-says-it-will-leave-city-with-fiscal-cliff/4135318/) | `nbc4_2026_bowser_budget_fiscal_cliff.html` | `66de9af2601a…` | downloaded |
| `casinoorg_2026_us` | Casino.org (page updated Nov. 16, 2026; saved from a browser Nov. 22, 2026), “Best gambling sites in the US 2026” (2026-11-16) | [link](https://www.casino.org/us/gambling/) | `casinoorg_2026_us_gambling.pdf` | `c73db849cd59…` | manual |
| `ga_2026_dc` | Gamblers Anonymous meeting directory (saved from a browser Nov. 22, 2026), “Washington D.C. G.A. - Tuesday (meeting listing)” (2026-11-22) | [link](https://gamblersanonymous.org/) | `ga_2026_dc_meetings.pdf` | `0a2352661702…` | manual |
| `hollenbeck_2025` | Hollenbeck, Larsen & Proserpio. October 2024 working-paper draft; the bankruptcy and collections figures are from its section 4.2. Copy hosted by the Minnesota Senate Finance Committee., “The Financial Consequences of Legalized Sports Betting (working paper, Oct. 2024)” (2024-10) | [link](https://assets.senate.mn/committees/2025-2026/1007_Committee_on_Finance/The-Financial-Consequences-of-Legalized-Sports-Betting.pdf) | `hollenbeck_2024_financial_consequences.pdf` | `f79b7bfcbfe7…` | downloaded |
| `baker_2024` | Baker, Balthrop, Johnson, Kotter & Pisciotta; NBER Working Paper 33108, “Gambling Away Stability: Sports Betting's Impact on Vulnerable Households” (2024-11) | [link](https://www.nber.org/system/files/working_papers/w33108/w33108.pdf) | `baker_2024_nber_w33108.pdf` | `87f73b682bad…` | downloaded |
| `arnesen_2025` | Arnesen & Matsuzawa; CHEPS Working Paper 20251001, San Diego State University, “Sports Betting Legalization Amplifies Emotional Cues & Intimate Partner Violence” (2025-10-30) | [link](https://cheps.sdsu.edu/_resources/docs/working-papers/cheps-wp-20251001.pdf) | `arnesen_matsuzawa_2025_cheps.pdf` | `e35b70c87f09…` | downloaded |
| `karlsson_2018` | Karlsson & Håkansson; Journal of Behavioral Addictions 7(4), 1091-1099, “Gambling disorder, increased mortality, suicidality, and associated comorbidity: A longitudinal nationwide register study” (2018-12) | [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC6376387/) | `karlsson_hakansson_2018_pmc.html` | `36616c4c4686…` | downloaded |
| `ctmirror_2022` | CT Mirror, “CT tracks online gambling closely, but not problem gambling” (2022-01-23) | [link](https://ctmirror.org/2022/01/23/ct-tracks-online-gambling-closely-but-not-problem-gambling/) | `ctmirror_2022_problem_gambling.html` | `204e136d1e97…` | downloaded |
| `psu_2026` | Penn State Social Science Research Institute, “Online gambling participation increased in Pennsylvania in 2025, report finds” (2026-01-22) | [link](https://www.psu.edu/news/social-science-research-institute/story/online-gambling-participation-increased-pennsylvania-2025) | `psu_2025_pa_online_gambling.html` | `614fc94c903a…` | downloaded |
| `rutgers_2023` | Nower, Stanmyre & Anthony, Rutgers Center for Gambling Studies; report to the New Jersey Division of Gaming Enforcement. Survey fieldwork Dec. 2020 to May 2021., “The Prevalence of Online and Land-Based Gambling in New Jersey (second report)” (2023) | [link](https://www.nj.gov/oag/ge/2023news/PrevalenceReport2023Final.pdf) | `rutgers_2023_nj_prevalence.pdf` | `18ca58574b7f…` | downloaded |
| `anj_2026` | Autorité nationale des jeux (France), “The algorithm developed by the ANJ reveals an alarming and rising number of problem gamblers” (2026-05) | [link](https://anj.fr/algorithm-developed-anj-reveals-alarming-and-rising-number-problem-gamblers) | `anj_2026_excessive_gamblers_algorithm.html` | `a02bf86e18b6…` | downloaded |
| `olms_local25_2025` | U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2025 (file no. 506-434)” (2025-12-31) | [link](https://olmsapps.dol.gov/query/orgReport.do?rptId=937902&rptForm=LM2Form) | `olms_lm2_local25_937902.html` | `b4a0e23dd37a…` | downloaded |
| `olms_local25_2024` | U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2024 (file no. 506-434)” (2024-12-31) | [link](https://olmsapps.dol.gov/query/orgReport.do?rptId=912430&rptForm=LM2Form) | `olms_lm2_local25_912430.html` | `858921f7309e…` | downloaded |
| `olms_local25_2023` | U.S. Department of Labor, Office of Labor-Management Standards, “UNITE HERE Local 25, Form LM-2 Labor Organization Annual Report, 2023 (file no. 506-434)” (2023-12-31) | [link](https://olmsapps.dol.gov/query/orgReport.do?rptId=888264&rptForm=LM2Form) | `olms_lm2_local25_888264.html` | `fdf2bdfebf57…` | downloaded |
| `ocfo_2026` | DC Office of the Chief Financial Officer, “June 2026 Revenue Estimates (letter to the Mayor and Council)” (2026-06-30) | [link](https://cfo.dc.gov/sites/default/files/dc/sites/ocfo/publication/attachments/June%202026%20Revenue_Estimate%20Letter%20063026.pdf) | `ocfo_2026_june_revenue_estimate.pdf` | `eeeaae59fcf3…` | downloaded |
| `lims_fis_2026` | DC Office of the Chief Financial Officer (via DC Council LIMS), “Fiscal Impact Statement - Internet Gaming and Consumer Protection Act of 2026 (Bill 26-656, Draft Committee Print as provided Nov. 17, 2026)” (2026-11-18) | [link](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-FIS_Internet_Gaming_and_Consumer_Protection_Act.pdf?Id=250301) | `lims_b26_0656_fis.pdf` | `54ebc6260a1e…` | downloaded |
| `lims_reia_2026` | DC Council Office of Racial Equity (via DC Council LIMS), “Racial Equity Impact Assessment: Committee Print, Bill 26-0656” (2026-11) | [link](https://lims.dccouncil.gov/downloads/LIMS/61620/Other/B26-0656-REIA_B26-0656_Internet_Gaming_Print.pdf?Id=250282) | `lims_b26_0656_reia_committee_print.pdf` | `49d98f83e3c8…` | downloaded |

Full hashes are in `data/sources/manifest.yaml`. `manual` means the publisher blocks automated downloads and the copy was saved from a browser. Copies are kept under a fair-use rationale for verification and will be taken down on request.

