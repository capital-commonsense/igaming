# Methods note: DC iGaming graphics

How the three Capital Commonsense graphics on B26-0656 (the Internet Gaming and Consumer
Protection Act of 2026) were built and how to check them. Every number in the graphics
is listed, with its basis, in [`LIST_OF_CLAIMS.md`](LIST_OF_CLAIMS.md).

## What the graphics are

1. **Follow one dollar** (`outputs/figures/follow_one_dollar_*`): where each $1 that DC
   residents lose to licensed online casinos would go, compared with $1 of income tax.
2. **Projections vs. actuals** (`outputs/figures/projections_vs_actuals*`): DC's record
   on gambling revenue forecasts (GambetDC) next to the forecast for this bill.
3. **Research findings** (`outputs/figures/research_findings*`): nine findings from
   studies of online sports betting and online casino gaming.

Each graphic also has a `_share` version with the Capital Commonsense header and footer.
The share version nests the plain graphic unchanged. Each figure has a `.alt.txt` file
with short and long alt text.

## 1. Follow one dollar

**Unit of account.** The "$1" is DC players' *combined net loss*: everything wagered
minus everything paid back as winnings, including winnings to players who finish ahead.
That equals operators' adjusted gross revenue (AGR), the bill's tax base. The committee
print doesn't count promotional credits as wagers, so the tax base and players' net cash
loss are the same thing. The graphic has no "winners" slice: taken together, players lose.

**Revenue side: the CFO's fiscal impact statement.** The model uses the DC Chief
Financial Officer's fiscal impact statement on the draft committee print (Nov. 17, 2026),
taking fiscal 2030 as the steady state. Fiscal 2028 includes one-time license fees, and
fiscal 2027 has no revenue.

- The CFO doesn't publish AGR, but each 2% assessment is $1,335,000. That implies AGR of
  $66.75M. The two assessments agree, and the model rejects inputs where they don't.
- Tax is 25% of AGR, and live-dealer games are taxed at 12.5%. The CFO's $16.06M in tax
  implies a blended rate of 24.05%.
- The first $750,000 of tax goes to addiction services, and the rest to the general fund.
- The community impact assessment (2%) funds debt counseling, domestic-violence services,
  gambling research and youth tech training.
- The regulatory assessment (2%) pays the Office of Lottery and Gaming to regulate the
  market. The CFO offsets it with equal costs, so it is drawn in grey, not red.
- License fees are $160,000 a year in steady state.

**The headline.** The District's net gain is the red slices (tax, community impact
assessment, license fees; 26.3¢) minus the lottery and sports-betting revenue the CFO
expects the city to lose ($1.65M a year, or 2.5¢). That is $15.9M, or **23.8¢ per $1**.
It equals the CFO's own "net impact on resources" line for fiscal 2030, and a test checks
that the model rebuilds it exactly.

**Private side.**

- **Dealer pay:** 100 live-dealer jobs, the Human Services Committee's estimate. The bill
  requires operators to offer live-dealer games from a DC studio. Pay is $70K a year,
  fully loaded (an assumption, labeled as such in the fine print).
- **Union dues:** $1,260 a year per dealer, from UNITE HERE Local 25's 2025 LM-2 filing,
  cross-checked against 2023 and 2024. Dues come out of dealer pay and are shown as their
  own slice.
- **Local vendors:** the bill requires 35% of an operator's DC-related operating budget to
  go to certified local businesses. The graphic uses $3M a year (an assumption, labeled as
  such in the fine print).
- **Out of state:** operators and suppliers get the remainder, 57¢. The slices sum to
  exactly $1, and tests enforce this.

**Income-tax comparison.** The right panel is definitional: income tax goes to DC
directly.

## 2. Projections vs. actuals

The bars compare GambetDC revenue projections with net transfers to the District:

- **FY2021:** projected at $27M (November 2018) and revised to $6.2M (February 2021).
  Actual net transfer was $0, and the app lost $4M.
- **FY2022:** projected at $20M. Actual net transfer was $2.7M.
- **The bill:** the CFO's projected net impact on District resources in fiscal 2030,
  $15.9M, beside a dashed "unknown" box. The fine print also notes lawmakers' $73M
  four-year figure and a $50M-a-year estimate cited at markup.

The actuals come from the Office of Lottery and Gaming's own oversight presentations, and
the GambetDC projections from contemporaneous reporting.

## 3. Research findings

Each finding appears verbatim in a saved copy of its source, and each tile states the
kind of gambling the evidence covers. The subtitle, "Research and help-seeking data from
outside DC", tells readers where the evidence comes from. Each headline pairs the number
with the harm it measures (for example, "+25–30% bankruptcy risk").

- **Bankruptcy:** Hollenbeck, Larsen & Proserpio (working paper, October 2024, section
  4.2): the likelihood of filing rises "by as much as 25-30%" three to four years after
  legalization, in a panel of about 7 million consumers. The tile says "at the high end".
- **Collections:** the average amount of debt in collections rises by about 8%.
- **Savings:** Baker et al. find each $1 of online sports betting reduces net investment
  by $0.99, measured as net deposits to brokerage accounts, including robo-advisers the
  paper describes as "primarily used for long-term savings". Among financially
  constrained households, credit card debt and overdrafts rise.
- **Online slots:** in the Gambling Survey for Great Britain (2023 data), the share of
  people scoring 8 or more on the Problem Gambling Severity Index was 5.9 times as high
  among those who played online slots in the past year as among all past-year gamblers
  ("nearly 6 times higher than average"), shown as 5×. The Gambling Commission's follow-up
  analysis finds the association remains significant after controlling for other gambling
  behaviour and other factors.
- **Suicide:** a standardized mortality ratio of 15.1 (95% interval 8.7–21.6) among
  Swedish patients aged 20–74 with diagnosed gambling disorder.
- **France:** the ANJ's detection algorithm, covering licensed online operators and FDJ
  and PMU account-based gambling in the second half of 2025, flagged 8.7% of registered
  players as likely problem gamblers. They produced 60% of gross gaming revenue.
- **New Jersey:** Rutgers' 2023 report to the Division of Gaming Enforcement (Table 28):
  11.3% of gamblers who bet only online screened as probable disorder (high risk),
  against 1.1% of those who bet only in person, shown as 10× (rounded down from 10.3×).
  New Jersey has licensed online casinos since 2013.
- **Connecticut helpline:** calls and texts rose 87%, November 2021 vs. November 2020
  (583 vs. 311), after online casinos and sports betting launched together (CT Mirror).
- **Pennsylvania helpline:** more than half of calls to the state's problem-gambling
  helpline involved online gambling (Penn State).

**Caveats printed on the graphic:** the findings are not DC estimates; the financial
findings come from studies of sports betting; Connecticut launched online casino
games and sports betting together; helpline figures measure service contacts; the British,
New Jersey and Swedish results compare groups of people.

## Article claims

Claims that back the article's text rather than a graphic carry an `article` field in
`data/claims.yaml`. They are checked against saved sources like every other claim and are
listed in `LIST_OF_CLAIMS.md` as "Article text".

**The bill and its timing.** B26-0656 passed the Human Services Committee 3–1 on
Nov. 18, 2026, with Councilmember Henderson opposed (Covers). The Council's 2026 schedule
leaves a Committee of the Whole meeting on Nov. 24, legislative meetings on Dec. 1 and
Dec. 15, and a recess from Dec. 23. The bill allows unlimited qualified operators (Covers)
and gives existing sports-wagering licensees an expedited review (CFO). Games may be
offered only to players physically in DC or in another jurisdiction that permits it, and
the Mayor may sign reciprocal agreements with other jurisdictions (CFO; Council Office of
Racial Equity).

**DC's budget.** NBC4 (July 2026) reports a $1 billion FY2027 budget gap, which the
Mayor's proposal closed at $1.1 billion, and a projected $837 million "budget cliff" the
following year from recurring programs funded with one-time money. The proposed FY2027
budget used $597.5 million of fund balance (CFO).

**Where the money goes.** In fiscal 2030 the District would collect $18.9 million from the
bill before offsets: $16.06 million in tax, $1.335 million each from the regulatory and
community impact assessments, and $160,000 in license fees (CFO). The committee print sends
the tax and the community impact assessment to the Internet Gaming Revenue Fund and the
regulatory assessment to the Lottery, Gambling, and Gaming Fund. Under D.C. Code § 36-681.01,
the first $750,000 of tax each year goes to the Department of Behavioral Health for
problem-gambling services, which the print limits to a contract with a third-party provider,
and the rest of the tax goes to the local fund. The community impact assessment is split 30%
to debt and financial counseling, 30% to domestic-violence and survivor services, 10% to
gambling research and 30% to youth technology training. The earmarks for problem gambling,
gambling research, domestic violence and financial counseling come to about $1.7 million, or
9% of the total.

**DC's gambling record.**

- **2011–12:** online gambling was legalized in a budget bill approved without public
  comment and never implemented. The Council repealed it 10–2 on Feb. 7, 2012 (WTOP).
- **GambetDC:** Intralot received a $215 million sole-source contract that included the
  city's only citywide sports-betting app (DCist). Revenue fell far short of projections
  (see graphic 2). The app failed on Apple devices for the whole 2022 Super Bowl, and
  Intralot paid DC $500,000 in compensation (DCist). In January 2025, Intralot and
  Veterans Services Corporation agreed to pay $6.5 million to settle the Attorney
  General's case over DC's small-business contracting laws (Washington City Paper).

**Neighboring states.** Maryland's 2026 online casino referendum bill (SB 761) was
withdrawn by its sponsor on March 13, 2026, and the House bill (HB 1343) got a hearing and
no vote (General Assembly records). Online casinos in Maryland would need a statewide
referendum (Casino.org). Virginia's House and Senate passed different bills and took no
final vote before the 2026 session ended (Covers).

**Other states.** Eight states have legalized real-money online casinos. Maine, which
legalized them in January 2026, has no launch date yet, so seven are live (Casino.org).
In Pennsylvania in FY2024/25, slots produced about $1.85B of $2,477M in online casino
revenue (74.7%), table games $597M (24.1%) and poker $29M (1.2%) (Pennsylvania Gaming
Control Board). Live-dealer games were "over 60%" of Pennsylvania's table revenue, so
live dealer was 14.5% to 24.1% of all online casino revenue. The CFO's FY2030 tax figure
implies a blended rate of 24.05%, or about 7.6% of revenue from live-dealer games (taxed at
12.5%): 1.9 to 3.2 times smaller than Pennsylvania's share. At Pennsylvania's mix, DC's
tax revenue would be about $0.6M to $1.4M a year lower than the CFO projects.

**Who pays.** Gambling losses are concentrated among heavy and problem gamblers. In France,
players flagged as likely problem gamblers (8.7% of registered players) produced 60% of
online gambling revenue in the second half of 2025 (ANJ). In a year of British Columbia's
provincial online casino data (30,920 accounts), the most engaged 20% of players produced
90% of net losses and enrolled in self-exclusion at 16%, against 6% for everyone else
(Deng, Lesch & Clark, *Addictive Behaviors*, 2021).

**New Jersey's costs.** NERA Economic Consulting, in a 2023 report for the Campaign for
Fairer Gambling, estimates that online gambling added $385 million a year in tax revenue in
New Jersey in 2022 compared with other recreation spending, and that problem gambling linked
to online gambling may cost the state about $350 million a year in healthcare, welfare,
homelessness and criminal justice. It concludes that "these fiscal costs approximately offset
the increased tax revenue." The cost figure scales UK estimates of the fiscal cost of
problem gambling to New Jersey's gambling revenue.

**Apps.** CBS News reports that sports-betting apps give extravagant perks to customers
losing large sums and limit the bets of winners.

**Gamblers Anonymous.** A Tuesday evening meeting at Second Baptist Church, 816 3rd St.
NW, is walkable from Chinatown (Gamblers Anonymous meeting listing).

## Guardrails followed

- **Sourcing:** every number in a graphic traces to a cited parameter or a checked quote.
- **No double counting:** fiscal effects, social costs and transfers are kept separate.
  Gambling losses are not counted as a social cost.
- **Cautious rounding:** derived headlines round down. For example, New Jersey's 10.3×
  ratio is shown as 10×.

## How verification works

```sh
uv sync
uv run pytest                 # model, rendering, and source checks
uv run dc-igaming all         # rebuild all graphics, CSVs and LIST_OF_CLAIMS.md
```

- **Sources:** `data/sources/manifest.yaml` lists each source with its URL, retrieval
  date and SHA-256. Copies are kept in `data/sources/` under a fair-use rationale for
  verification and will be taken down on request.
- **Claims:** `data/claims.yaml` holds every sourced number with verbatim quotes.
  `tests/test_claims.py` extracts each saved file's text and fails if a quote is missing
  or a file's hash has changed.
- **Parameters:** `model/params.yaml` marks each input `verified`, `reported` or
  `assumption`. A parameter can be marked `verified` only if it lists checked claims.
- **Claims list:** `LIST_OF_CLAIMS.md` is generated from those files and the figure code.
  `tests/test_claims_doc.py` fails if the committed copy is stale.
