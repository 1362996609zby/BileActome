from bileactome.cli import build_parser


def test_mag_defaults():
    args = build_parser().parse_args(["mag", "run", "--genome-dir", "genomes", "--output-dir", "out"])
    assert args.evalue == 1e-3
    assert args.prodigal_mode == "meta"
    assert args.threads == 1


def test_catalog_defaults():
    args = build_parser().parse_args(["catalog", "run", "--protein-fasta", "p.fa", "--cds-fasta", "c.fa", "--reads-dir", "reads", "--output-dir", "out"])
    assert args.evalue == 1e-3
    assert args.dom_evalue == 1e-3
    assert args.epsilon == 1e-12

