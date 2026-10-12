"""ASCII identity for terminal use; machine-readable stdout stays unchanged."""

from . import __version__

LOGO = r""" ____  _ _        _        _
| __ )(_) | ___  / \   ___| |_ ___  _ __ ___   ___
|  _ \| | |/ _ \/ _ \ / __| __/ _ \| '_ ` _ \ / _ \
| |_) | | |  __/ ___ \ (__| || (_) | | | | | |  __/
|____/|_|_|\___/_/   \_\___|\__\___/|_| |_| |_|\___|"""


def render_banner() -> str:
    return (
        f"{LOGO}\n"
        f"BileActome CLI v{__version__} | 27 bile acid gene HMM profiles\n"
        "China Agricultural University | Research / Commercial License\n"
        "Paper resources: CC BY 4.0 | DOI: 10.1093/ismeco/ycag205\n"
    )


def license_summary() -> str:
    return (
        "BileActome Microbial Bile Acid Metabolism Gene Annotation\n"
        "and Abundance Analysis Software V1.0\n"
        "Copyright (c) 2026 China Agricultural University\n"
        "CLI: LicenseRef-BileActome-Research-Commercial.\n"
        "Non-commercial research and education: free under LICENSE.\n"
        "Commercial use: prior written authorization required.\n"
        "Public package redistribution is permitted under LICENSE.\n"
        "27 HMMs, legacy scripts and toy data: CC-BY-4.0; commercial reuse permitted.\n"
        "Full terms: installed distribution licenses / source LICENSE and NOTICE.\n"
        "Commercial licensing inquiries:\n"
        "  Bing Wang: wangb@cau.edu.cn\n"
        "  Boyan Zhang: 1362996609zby@gmail.com\n"
    )
