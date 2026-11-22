"""Command line entry point.

  uv run dc-igaming flow            money-flow CSVs + follow-one-dollar diagram
  uv run dc-igaming projections     GambetDC projected-vs-actual figure
  uv run dc-igaming harms           research-findings grid
  uv run dc-igaming claims-doc      regenerate LIST_OF_CLAIMS.md
  uv run dc-igaming all             everything above
  uv run dc-igaming fetch-sources   download source documents listed in the manifest
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from dc_igaming.alttext import AltText, harms_alt, one_dollar_alt, projections_alt, write_alt
from dc_igaming.claims_doc import OUTPUT_NAME, render_claims_doc
from dc_igaming.diagram import PROJECT_ROOT, default_text, dues_basis_note, render_one_dollar_svg
from dc_igaming.flow import income_tax_equivalent
from dc_igaming.harms import render_harms_svg
from dc_igaming.outputs import scenario_flows, write_flow_outputs
from dc_igaming.params import load_params
from dc_igaming.projections import render_projections_svg
from dc_igaming.share import brand_frame
from dc_igaming.sources import SOURCES_DIR, fetch, load_claims, load_manifest, sha256
from dc_igaming.svg import svg_to_png

DEFAULT_PARAMS = PROJECT_ROOT / "model" / "params.yaml"
DEFAULT_OUT = PROJECT_ROOT / "outputs"


def _save(svg: str, path: Path, png: bool, alt: AltText) -> None:
    """Write the plain figure, its branded share version (<name>_share.svg/.png) and <name>.alt.txt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"wrote {write_alt(alt, path)}")
    share_path = path.with_name(f"{path.stem}_share.svg")
    for p, content in ((path, svg), (share_path, brand_frame(svg))):
        p.write_text(content, encoding="utf-8")
        print(f"wrote {p}")
        if png:
            print(f"wrote {svg_to_png(content, p.with_suffix('.png'))}")


def cmd_flow(args: argparse.Namespace) -> int:
    params = load_params(args.params)
    out = Path(args.out)
    for p in write_flow_outputs(params, out):
        print(f"wrote {p}")
    claims = load_claims()
    for name, flows in scenario_flows(params).items():
        if not flows.feasible:
            print(f"skip {name}: infeasible (costs exceed operator revenue)")
            continue
        iit = income_tax_equivalent(flows, params)
        text = default_text(flows, iit, name, dues_basis_note(flows, claims))
        svg = render_one_dollar_svg(flows, iit, text)
        _save(svg, out / "figures" / f"follow_one_dollar_{name}.svg", not args.no_png,
              one_dollar_alt(flows, iit, text))
    return 0


def cmd_projections(args: argparse.Namespace) -> int:
    claims = load_claims()
    svg = render_projections_svg(claims, load_manifest())
    _save(svg, Path(args.out) / "figures" / "projections_vs_actuals.svg", not args.no_png,
          projections_alt(claims))
    return 0


def cmd_harms(args: argparse.Namespace) -> int:
    claims = load_claims()
    svg = render_harms_svg(claims, load_manifest())
    _save(svg, Path(args.out) / "figures" / "research_findings.svg", not args.no_png, harms_alt(claims))
    return 0


def build_claims_doc(params_path: str | Path = DEFAULT_PARAMS) -> str:
    raw = yaml.safe_load(Path(params_path).read_text(encoding="utf-8"))
    return render_claims_doc(load_params(params_path), raw, load_claims(), load_manifest())


def cmd_claims_doc(args: argparse.Namespace) -> int:
    path = PROJECT_ROOT / OUTPUT_NAME
    path.write_text(build_claims_doc(args.params), encoding="utf-8")
    print(f"wrote {path}")
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    return cmd_flow(args) or cmd_projections(args) or cmd_harms(args) or cmd_claims_doc(args)


def cmd_fetch_sources(args: argparse.Namespace) -> int:
    failures = 0
    for src in load_manifest().values():
        dest = src.path(SOURCES_DIR)
        if dest.exists() and not args.force:
            print(f"have  {src.file}")
            continue
        if src.status == "manual":
            print(f"MANUAL {src.file}: save from a browser: {src.url}")
            continue
        try:
            fetch(src)
        except Exception as exc:  # noqa: BLE001 (report and continue)
            failures += 1
            print(f"FAIL  {src.file}: {exc}")
            continue
        ok = src.sha256 is None or sha256(dest) == src.sha256
        print(f"got   {src.file}" + ("" if ok else "  (hash differs from manifest: re-verify claims)"))
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dc-igaming", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func, help_ in [
        ("flow", cmd_flow, "money-flow model: CSVs + follow-one-dollar diagram"),
        ("projections", cmd_projections, "GambetDC projected vs. actual revenue figure"),
        ("harms", cmd_harms, "research findings grid"),
        ("claims-doc", cmd_claims_doc, "regenerate LIST_OF_CLAIMS.md"),
        ("all", cmd_all, "every output, including LIST_OF_CLAIMS.md"),
    ]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("--params", default=str(DEFAULT_PARAMS))
        p.add_argument("--out", default=str(DEFAULT_OUT))
        p.add_argument("--no-png", action="store_true", help="skip PNG rendering")
        p.set_defaults(func=func)
    f = sub.add_parser("fetch-sources", help="download source documents listed in the manifest")
    f.add_argument("--force", action="store_true", help="re-download files that already exist")
    f.set_defaults(func=cmd_fetch_sources)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
