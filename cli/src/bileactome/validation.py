from __future__ import annotations

import json
from pathlib import Path

from .utils import atomic_write_json, nonempty


def _read_table(path: Path):
    import pandas as pd

    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, sep="\t" if path.suffix.lower() in {".tsv", ".txt"} else ",")


def validate_project(project_dir: Path) -> dict:
    import numpy as np
    import pandas as pd

    project_dir = project_dir.expanduser().resolve()
    checks, errors, warnings = [], [], []
    manifest_path = project_dir / "run_manifest.json"
    manifest = None
    if nonempty(manifest_path):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            checks.append({"check": "run_manifest", "status": "pass"})
        except json.JSONDecodeError as exc:
            errors.append(f"invalid run_manifest.json: {exc}")
    else:
        errors.append("run_manifest.json is missing or empty")
    workflow = manifest.get("workflow") if manifest else None
    if workflow == "mag_wgs":
        matrices = sorted(project_dir.glob("hmmsearch_counts_E*.tsv"))
        if not matrices:
            errors.append("MAG/WGS count matrix is missing")
        else:
            df = pd.read_csv(matrices[0], sep="\t")
            if "Genome" not in df.columns or len(df.columns) != 28:
                errors.append("MAG/WGS matrix must contain Genome plus 27 family columns")
            checks.append({"check": "mag_count_matrix", "status": "pass" if not errors else "fail", "rows": len(df), "columns": len(df.columns)})
    elif workflow == "non_redundant_gene_catalog":
        result_dir = project_dir / "05_results"
        required = [result_dir / "abundance_merged_with_function.xlsx", result_dir / "FunctionSum_matrix.xlsx", result_dir / "Relative_abundance_matrix.xlsx", result_dir / "CLR_matrix.xlsx"]
        for path in required:
            if not nonempty(path):
                errors.append(f"missing or empty result: {path.relative_to(project_dir)}")
        if all(nonempty(path) for path in required):
            rel = _read_table(result_dir / "Relative_abundance_matrix.xlsx")
            clr = _read_table(result_dir / "CLR_matrix.xlsx")
            rel_numeric = rel.select_dtypes(include=["number"])
            clr_numeric = clr.select_dtypes(include=["number"])
            if rel_numeric.empty:
                errors.append("relative abundance matrix has no numeric sample columns")
            else:
                sums = rel_numeric.sum(axis=0)
                if not np.allclose(sums[sums > 0], 1.0, atol=1e-8):
                    errors.append("non-zero relative abundance sample columns do not sum to 1")
            if clr_numeric.empty:
                errors.append("CLR matrix has no numeric sample columns")
            elif not np.allclose(clr_numeric.mean(axis=0), 0.0, atol=1e-8):
                errors.append("CLR sample column means are not approximately zero")
            checks.append({"check": "catalog_matrices", "status": "pass" if not errors else "fail", "relative_shape": list(rel.shape), "clr_shape": list(clr.shape)})
    elif manifest:
        errors.append(f"unsupported workflow in manifest: {workflow}")
    report = {"ok": not errors, "project_dir": str(project_dir), "workflow": workflow, "checks": checks, "warnings": warnings, "errors": errors}
    atomic_write_json(project_dir / "validation_report.json", report)
    return report
