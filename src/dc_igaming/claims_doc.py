"""Generate LIST_OF_CLAIMS.md: every number in every graphic, traced to its basis.

The document is built from the same inputs the graphics use (model/params.yaml,
data/claims.yaml, data/sources/manifest.yaml, and the figure definitions), and
tests/test_claims_doc.py fails if the committed file differs from a fresh render.
So the document can't drift from the graphics.
"""

from __future__ import annotations

from dataclasses import dataclass

from dc_igaming.diagram import format_cents
from dc_igaming.flow import FlowInputs, Flows, compute_flows, income_tax_equivalent  # noqa: F401
from dc_igaming.harms import TILES
from dc_igaming.harms import TITLE as HARMS_TITLE
from dc_igaming.params import ModelParams, Param
from dc_igaming.projections import _money, build_groups, default_title, hit_rate
from dc_igaming.sources import Claim, Source
from dc_igaming.svg import format_usd

OUTPUT_NAME = "LIST_OF_CLAIMS.md"


@dataclass(frozen=True)
class Row:
    shown: str
    value: str
    basis: str
    refs: str


def _md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(_md_escape(c) for c in r) + " |" for r in rows]
    return out


def _param_claims(raw_claims: dict[str, list[str]], qualified: str) -> list[str]:
    return raw_claims.get(qualified, [])


def _ref(ids: list[str]) -> str:
    return ", ".join(f"[`{i}`](#{i})" for i in ids) if ids else ""


def _num(v: float) -> str:
    """Plain numbers for humans: 3,699,357,000 not 3.69936e+09; 0.035 stays 0.035."""
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    return f"{v:g}"


def _status_badge(p: Param) -> str:
    return {"verified": "verified (primary source)", "reported": "reported (secondary source)",
            "assumption": "**assumption**"}[p.status]


# --------------------------------------------------------------------------- Sankey


def sankey_rows(f: Flows, params: ModelParams, scenario: str, claims: dict[str, Claim],
                pc: dict[str, list[str]]) -> list[Row]:
    inp = f.inputs
    c = f.cents()
    sc = f"scenarios.{scenario}"

    def q(name: str) -> str:
        return f"constants.{name}" if name in params.constants else f"{sc}.{name}"

    def refs(*names: str) -> str:
        parts = []
        for n in names:
            parts.append(f"`{q(n)}`")
            if pc.get(q(n)):
                parts.append(_ref(pc[q(n)]))
        return "; ".join(parts)

    agr = "AGR (= community impact assessment \u00f7 2%)"
    lo, hi = claims["local25_dues_rate_2025"].value
    receipts = claims["local25_dues_receipts_2025"].value
    members = claims["local25_members_2025"].value
    usable = 100 * (f.public_receipts - f.regulatory) / f.net_loss
    lost = inp.lottery_loss + inp.sports_wagering_loss
    return [
        Row("Headline: \u201cthe city nets 24 cents\u201d", f"{f.net_impact_cents():.1f}\u00a2",
            f"CFO net impact on resources \u00f7 {agr}. The model rebuilds the CFO's net line from its parts "
            "and matches it exactly (`tests/test_flow.py::test_net_impact_reproduces_cfo_line`)",
            refs("community_impact", "assessment_rate") + "; " + _ref(["fis_net_impact_fy2030"])),
        Row("$1 (net of winnings)", "100\u00a2",
            "Denominator: players' combined net loss = adjusted gross revenue; promotional credits are not "
            "counted as wagers", _ref(["fis_agr_definition", "print_promo_credits"])),
        Row("Implied adjusted gross revenue", format_usd(f.net_loss) + "/yr",
            "community impact assessment \u00f7 2%, cross-checked against the regulatory assessment",
            refs("community_impact", "regulatory_assessment", "assessment_rate")),
        Row("57\u00a2 leaves DC", format_cents(c["out_of_state"]),
            "AGR \u2212 everything paid to DC \u2212 dealer pay \u2212 vendors, \u00f7 AGR. The residual, so slices sum to $1",
            refs("tax_revenue", "community_impact", "regulatory_assessment", "license_fees", "jobs",
                 "comp_per_job", "local_vendor_spend")),
        Row("DC general fund (tax)", format_cents(c["tax_general"]), "(tax \u2212 $750K set-aside) \u00f7 AGR",
            refs("tax_revenue", "treatment_setaside")),
        Row("DC community impact fund", format_cents(c["community_impact"]), "2% assessment \u00f7 AGR",
            refs("community_impact")),
        Row("DC addiction services", format_cents(c["tax_treatment"]), "$750K \u00f7 AGR", refs("treatment_setaside")),
        Row("DC license fees", format_cents(c["license_fees"]), "FY2030 license fees \u00f7 AGR", refs("license_fees")),
        Row("Regulating the market (OLG)", format_cents(c["regulatory"]),
            "2% regulatory assessment \u00f7 AGR; the CFO offsets it with equal OLG costs",
            refs("regulatory_assessment", "olg_regulatory_costs")),
        Row("Dealers' pay", format_cents(c["dealer_take_home"]), "jobs \u00d7 (pay \u2212 dues) \u00f7 AGR",
            refs("jobs", "comp_per_job", "union_dues_per_member")),
        Row("Union dues (UNITE HERE Local 25)", format_cents(c["union_dues"]), "jobs \u00d7 dues \u00f7 AGR",
            refs("jobs", "union_dues_per_member")),
        Row("DC local vendors", format_cents(c["local_vendors"]), "vendor spending \u00f7 AGR",
            refs("local_vendor_spend")),
        Row("Or: $1 of income tax \u2192 100\u00a2 to DC", "100\u00a2",
            "Definitional: income tax is collected by DC directly", ""),
        Row("Fine print: tax rates", f"{inp.tax_rate:.0%}; live dealer {inp.live_dealer_tax_rate:.1%}",
            "as stated in the committee print", refs("tax_rate", "live_dealer_tax_rate")),
        Row("Fine print: blended tax rate", f"{f.blended_tax_rate:.2%}",
            f"CFO tax \u00f7 AGR (implies {f.live_dealer_share:.1%} of AGR from live-dealer games)",
            refs("tax_revenue", "community_impact")),
        Row("Fine print: each 2% assessment", format_usd(inp.community_impact), "CFO table, FY2030",
            refs("community_impact")),
        Row("Fine print: red slices total", format_cents(usable),
            "(tax + community impact + license fees) \u00f7 AGR", refs("tax_revenue", "community_impact", "license_fees")),
        Row("Fine print: lost lottery and sports-betting revenue", f"{format_usd(lost)}/yr ({format_cents(100 * lost / f.net_loss)})",
            "CFO table, FY2030", refs("lottery_loss", "sports_wagering_loss")),
        Row("Fine print: net gain", f"{format_usd(f.net_impact)} ({f.net_impact_cents():.1f}\u00a2)",
            "red slices \u2212 lost revenue (the regulatory assessment and OLG costs cancel)",
            _ref(["fis_net_impact_fy2030"])),
        Row("Fine print: jobs, pay, vendors",
            f"{inp.jobs:.0f} jobs; {format_usd(inp.comp_per_job)}; {format_usd(inp.local_vendor_spend)}",
            "committee estimate; assumption; assumption", refs("jobs", "comp_per_job", "local_vendor_spend")),
        Row("Fine print: dues rate", f"${hi:.0f}/month (${inp.union_dues_per_member:,.0f}/yr); range ${lo:.2f}\u2013${hi:.2f}",
            "top of Local 25's reported regular dues range \u00d7 12", _ref(["local25_dues_rate_2025"])),
        Row("Fine print: dues receipts per member", f"${receipts / members:,.0f}",
            f"{format_usd(receipts)} \u00f7 {members:,.0f} members (consistency check on the rate)",
            _ref(["local25_dues_receipts_2025", "local25_members_2025"])),
        Row("Fine print: total dues", format_usd(f.dues) + "/yr", "jobs \u00d7 dues",
            refs("jobs", "union_dues_per_member")),
    ]


# --------------------------------------------------------------------------- document


def render_claims_doc(params: ModelParams, raw_params: dict, claims: dict[str, Claim],
                      sources: dict[str, Source]) -> str:
    # qualified param name -> list of claim ids (from the raw YAML `claims:` field)
    pc: dict[str, list[str]] = {}
    for k, v in raw_params["constants"].items():
        if v.get("claims"):
            pc[f"constants.{k}"] = list(v["claims"])
    for sname, sc in raw_params["scenarios"].items():
        for k, v in sc.items():
            if isinstance(v, dict) and v.get("claims"):
                pc[f"scenarios.{sname}.{k}"] = list(v["claims"])

    used_in: dict[str, list[str]] = {cid: [] for cid in claims}
    for q, ids in pc.items():
        for cid in ids:
            used_in[cid].append(f"Sankey input `{q}`")
    for cid in ("local25_dues_rate_2025", "local25_dues_receipts_2025", "local25_members_2025"):
        used_in[cid].append("Sankey fine print (dues basis)")
    for cid in ("local25_2024", "local25_2023"):
        used_in[cid].append("Cross-check only (dues per member in prior years); not displayed")
    groups = build_groups(claims)
    for g in groups:
        for b in g.bars:
            if b.key in claims:
                used_in[b.key].append("Projections chart bar")
    for cid in ("gambetdc_fy2021_loss", "igaming_other_estimate", "igaming_committee_estimate"):
        used_in[cid].append("Projections chart note/fine print")
    for cid in ("fis_scope", "fis_agr_definition", "print_promo_credits", "fis_promo_cap", "fis_net_impact_fy2030"):
        used_in[cid].append("Sankey headline/fine print (tax base and net gain)")
    for cid, cl in claims.items():
        if cl.article:
            used_in[cid].append(f"Article text: {cl.article}")
    for t in TILES:
        used_in[t.claim].append(f"Research findings tile `{t.claim}` (headline)")
        for e in t.extra_claims:
            used_in[e].append(f"Research findings tile `{t.claim}` (text/label)")

    L: list[str] = []
    a = L.append
    a("# List of claims")
    a("")
    a("<!-- GENERATED FILE: do not edit by hand. Regenerate with `uv run dc-igaming claims-doc`. -->")
    a("<!-- tests/test_claims_doc.py fails if this file is out of date. -->")
    a("")
    a("Every number and factual statement in the three graphics, with how it was derived and where it "
      "comes from. A reader should be able to check each item without trusting the authors.")
    a("")
    a("## How to verify")
    a("")
    a("```sh")
    a("uv sync")
    a("uv run pytest                  # all checks below, including quote-in-source tests")
    a("uv run dc-igaming all          # re-render every graphic and CSV from the inputs")
    a("uv run dc-igaming claims-doc   # regenerate this file")
    a("shasum -a 256 data/sources/*   # compare with the sha256 column in the source register")
    a("```")
    a("")
    a("Every item below is one of three kinds:")
    a("")
    a("- **Checked quote**: a claim in [`data/claims.yaml`](data/claims.yaml) with verbatim quotes. "
      "`tests/test_claims.py` extracts the text of the saved source file and fails unless every quote "
      "appears in it (after whitespace, quote-mark and ligature normalization), and fails if the file's "
      "sha256 differs from the manifest. To check by hand, open the file in `data/sources/` and search "
      "for the quote.")
    a("- **Model output**: computed from parameters in [`model/params.yaml`](model/params.yaml) by "
      "[`src/dc_igaming/flow.py`](src/dc_igaming/flow.py). The formula is given; golden-value tests are in "
      "`tests/test_flow.py`. Each parameter is marked `verified` (checked against a primary source), "
      "`reported` (checked against secondary reporting only) or `assumption` (no source).")
    a("- **Definitional**: true by construction (for example, the income-tax panel's 100\u00a2).")
    a("")

    # ---- Sankey
    central = compute_flows(FlowInputs.from_scenario(params, "central"))
    a("## 1. Follow one dollar (Sankey)")
    a("")
    a("Files: `outputs/figures/follow_one_dollar_central.{svg,png}` and `_share` versions. "
      "Code: `src/dc_igaming/diagram.py`.")
    a("")
    a("**The \u201c$1\u201d is DC players' combined net loss**: everything wagered minus everything paid "
      "back as winnings, including winnings to players who finish ahead. That equals operators' gross gaming "
      "revenue (GGR). Shares are cents per $1 of GGR. The out-of-state share is the residual, so the "
      "slices sum to exactly $1 (`tests/test_flow.py::test_every_dollar_of_net_loss_is_accounted_for`). "
      "There is no \u201cwinners\u201d slice: taken together, players lose.")
    a("")
    a("### Numbers shown (central scenario)")
    a("")
    rows = sankey_rows(central, params, "central", claims, pc)
    L += _table(["Shown on graphic", "Value", "Derivation", "Inputs and supporting claims"],
                [[r.shown, r.value, r.basis, r.refs] for r in rows])
    a("")
    a("### Inputs")
    a("")
    prow = []
    for q, prm in params.all_params():
        if q in ("constants.dc_population",):
            continue  # used only in CSV outputs, not in any graphic
        prow.append([f"`{q}`", _num(prm.value), prm.unit, _status_badge(prm), prm.source,
                     _ref(pc.get(q, []))])
    L += _table(["Parameter", "Value", "Unit", "Status", "Source", "Claims"], prow)
    a("")
    a("The steady-state year is fiscal 2030, the last year of the CFO's financial plan. Fiscal 2028 "
      "includes $12.3M of one-time operator license fees, and fiscal 2027 has no revenue.")
    a("")

    # ---- Projections
    a("## 2. Projections vs. actuals")
    a("")
    a("Files: `outputs/figures/projections_vs_actuals.{svg,png}` and `_share` versions. "
      "Code: `src/dc_igaming/projections.py`.")
    a("")
    prj = []
    prj.append([f"Title: \u201c{default_title(claims)}\u201d", f"{hit_rate(claims):.1%}",
                "FY2022 actual \u00f7 FY2022 projection",
                _ref(["gambetdc_fy2022_actual", "gambetdc_fy2022_projection"])])
    for g in groups:
        for b in g.bars:
            label = f"{g.title}, {g.subtitle}: {' '.join(b.label)}"
            if b.kind == "unknown":
                prj.append([label, "?", "Not yet known: the program hasn't launched", ""])
            else:
                prj.append([label, _money(b.value), claims[b.key].unit, _ref([b.key])])
            if b.note:
                note_ref = ["gambetdc_fy2021_loss"] if "lost" in b.note else \
                    ["gambetdc_fy2022_actual", "gambetdc_fy2022_projection"]
                prj.append([f"Note above bar: \u201c{b.note}\u201d", b.note, "", _ref(note_ref)])
    prj.append(["Fine print: other estimate", _money(claims["igaming_other_estimate"].value) + " a year",
                "Annual gaming tax estimate from an economic analysis cited at markup, as reported by Covers",
                _ref(["igaming_other_estimate"])])
    prj.append(["Fine print: lawmakers' $73M over four years", "$73M",
                "Four-year gaming tax estimate attributed to lawmakers by Axios DC",
                _ref(["igaming_committee_estimate"])])
    L += _table(["Shown on graphic", "Value", "Basis", "Supporting claims"], prj)
    a("")
    a("GambetDC actuals are net transfers to the District reported by the Office of Lottery and Gaming. "
      "GambetDC projections are as reported at the time. The online casino bar shows the DC Chief Financial "
      "Officer's projected net impact on District resources in FY2030 from the fiscal impact statement "
      "on the committee print.")
    a("")

    # ---- Harms
    a(f"## 3. Research findings (\u201c{HARMS_TITLE}\u201d)")
    a("")
    a("Files: `outputs/figures/research_findings.{svg,png}` and `_share` versions. "
      "Code: `src/dc_igaming/harms.py`.")
    a("")
    hr = []
    for t in TILES:
        hr.append([t.headline(claims), t.finding, t.covers,
                   "; ".join(sources[s].short_citation() for s in t.sources(claims)),
                   _ref([t.claim, *t.extra_claims])])
    L += _table(["Headline", "Finding as worded", "Evidence type label", "Citation shown", "Supporting claims"], hr)
    a("")
    a("Each headline is a number plus the harm it measures, set under the number in bold serif. "
      "Derived headlines: `10\u00d7` is 11.3% \u00f7 1.1% (New Jersey, Table 28), rounded *down* from 10.3 so "
      "it never overstates. "
      "`+87%` is (583 \u2212 311) \u00f7 311, also rounded down. `+25\u201330%` is the high end the October "
      "2024 draft reports (\u201cas much as\u201d), and the tile says so. `5\u00d7` is the Gambling Commission's ratio of 5.9 for online slots, rounded down. "
      "`+8%` (\u201croughly\u201d in the "
      "source, \u201capproximate\u201d on the tile), `\u2212$0.99`, `15\u00d7`, `60%` and `50%+` restate the "
      "quoted figures directly.")
    a("")
    a("Fine-print caveats on the graphic: none of these are DC estimates; the financial findings "
      "cover sports betting, and few studies isolate online casino games; Connecticut launched online casino "
      "games and sports betting together; helpline figures measure service contacts; the British, New Jersey "
      "and Swedish results compare groups of people and do not show that gambling caused the differences.")
    a("")

    # ---- Claim register
    a("## 4. Claim register")
    a("")
    a("Every claim in `data/claims.yaml`. The quotes are checked against the saved source by "
      "`tests/test_claims.py`.")
    a("")
    for cid, cl in claims.items():
        src = sources[cl.source]
        a(f"### {cid}")
        a("")
        if isinstance(cl.value, list):
            val = ", ".join(_num(x) for x in cl.value)
        elif isinstance(cl.value, (int, float)):
            val = _num(cl.value)
        else:
            val = "n/a (qualitative)"
        a(f"- **Value:** {val} ({cl.unit})")
        a(f"- **Source:** {src.citation()} \u2014 [{src.url}]({src.url})")
        a(f"- **Local copy:** [`data/sources/{src.file}`](data/sources/{src.file.replace(' ', '%20')})")
        a("- **Verbatim quotes:**")
        for q in cl.quotes:
            a(f"  - \u201c{q}\u201d")
        a(f"- **Used in:** {'; '.join(used_in[cid]) or 'not displayed'}")
        a("")

    # ---- Source register
    a("## 5. Source register")
    a("")
    srows = [[f"`{s.id}`", s.citation(), f"[link]({s.url})", f"`{s.file}`",
              f"`{s.sha256[:12]}\u2026`" if s.sha256 else "", s.status] for s in sources.values()]
    L += _table(["ID", "Citation", "URL", "File", "sha256 (prefix)", "How obtained"], srows)
    a("")
    a("Full hashes are in `data/sources/manifest.yaml`. `manual` means the publisher blocks automated "
      "downloads and the copy was saved from a browser. Copies are kept under a fair-use rationale for "
      "verification and will be taken down on request.")
    a("")

    return "\n".join(L) + "\n"
