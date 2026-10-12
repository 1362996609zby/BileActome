#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${ROOT_DIR}/../.." && pwd)"
HMM_DIR="${REPO_DIR}/database file"
OUT_DIR="${ROOT_DIR}/toy_results"
PYTHON_BIN="${PYTHON_BIN:-python}"

mkdir -p "${OUT_DIR}" "${OUT_DIR}/hmm_results" "${OUT_DIR}/bowtie2_map" "${OUT_DIR}/abundance" "${OUT_DIR}/results"

bash "${ROOT_DIR}/scripts/step1_hmm_annotation.sh" \
  --protein-fasta "${ROOT_DIR}/gene_catalog/toy_unigenes.protein.fa" \
  --hmm-dir "${HMM_DIR}" \
  --out-dir "${OUT_DIR}/hmm_results" \
  --cpu 2 \
  --evalue 1e-3 \
  --dom-evalue 1e-3

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/step2_extract_matched_cds.py" \
  --hmm-result-dir "${OUT_DIR}/hmm_results" \
  --cds-fasta "${ROOT_DIR}/gene_catalog/toy_unigenes.CDS.fa" \
  --out-cds "${OUT_DIR}/target_cds.fa" \
  --out-map "${OUT_DIR}/gene_to_function.tsv" \
  --force

bash "${ROOT_DIR}/scripts/step3_bowtie2_mapping.sh" \
  --target-cds "${OUT_DIR}/target_cds.fa" \
  --reads-dir "${ROOT_DIR}/clean_reads" \
  --out-dir "${OUT_DIR}/bowtie2_map" \
  --threads 2

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/step4_abundance_calc.py" \
  --sam-dir "${OUT_DIR}/bowtie2_map" \
  --cds-fasta "${OUT_DIR}/target_cds.fa" \
  --out-dir "${OUT_DIR}/abundance" \
  --gene-length-file "${OUT_DIR}/target_cds_length.tsv" \
  --sample-strip "" \
  --force

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/step5_merge_abundance_with_function.py" \
  --abundance-dir "${OUT_DIR}/abundance" \
  --function-map "${OUT_DIR}/gene_to_function.tsv" \
  --out-xlsx "${OUT_DIR}/results/abundance_merged_with_function.xlsx" \
  --out-tsv "${OUT_DIR}/results/abundance_merged_with_function.tsv" \
  --force

"${PYTHON_BIN}" "${ROOT_DIR}/scripts/step6_function_abundance_transform.py" \
  --in-table "${OUT_DIR}/results/abundance_merged_with_function.tsv" \
  --out-func "${OUT_DIR}/results/FunctionSum_matrix.tsv" \
  --out-rel "${OUT_DIR}/results/Relative_abundance_matrix.tsv" \
  --out-clr "${OUT_DIR}/results/CLR_matrix.tsv" \
  --force

echo "Toy workflow completed. Results: ${OUT_DIR}/results"
