import os
import shutil
import subprocess
import tempfile

import pandas as pd
from q2_types.genome_data import GenesDirectoryFormat
from q2_types.per_sample_sequences import MultiMAGSequencesDirFmt

from q2_amr.amrfinderplus.types import (
    AMRFinderPlusDatabaseDirFmt,
    ARMFinderPlusAnnotationsDirFmt,
)
from q2_amr.card.utils import create_count_table, read_in_txt, run_command


def annotate_mags_amrfinderplus(
    mags: MultiMAGSequencesDirFmt,
    amrfinderplus_db: AMRFinderPlusDatabaseDirFmt,
    organism: str = None,
    plus: bool = False,
    report_all_equal: bool = False,
    ident_min: float = None,
    coverage_min: float = 0.5,
    translation_table: str = "11",
    threads: int = None,
) -> (
    ARMFinderPlusAnnotationsDirFmt,
    ARMFinderPlusAnnotationsDirFmt,
    GenesDirectoryFormat,
    pd.DataFrame,
):
    manifest = mags.manifest.view(pd.DataFrame)

    annotations = ARMFinderPlusAnnotationsDirFmt()
    mutations = ARMFinderPlusAnnotationsDirFmt()
    genes = GenesDirectoryFormat()

    frequency_list = []

    with tempfile.TemporaryDirectory() as tmp:
        for samp_mag in list(manifest.index):
            input_sequence = manifest.loc[samp_mag, "filename"]
            run_amrfinderplus_n(
                tmp,
                amrfinderplus_db,
                input_sequence,
                organism,
                plus,
                report_all_equal,
                ident_min,
                coverage_min,
                translation_table,
                threads,
            )

            frequency_df = read_in_txt(
                path=os.path.join(tmp, "amr_annotations.tsv"),
                samp_bin_name=str(os.path.join(samp_mag[0], samp_mag[1])),
                data_type="mags",
                colname="Gene symbol",
            )

            for dir_format, file_name in zip(
                [annotations, mutations, genes],
                ["amr_annotations.tsv", "amr_mutations.tsv", str(samp_mag)[1]],
            ):
                if dir_format in [annotations, mutations]:
                    des_dir = os.path.join(str(dir_format), samp_mag[0], samp_mag[1])
                    os.makedirs(des_dir, exist_ok=True)
                shutil.move(os.path.join(tmp, file_name), des_dir)

            frequency_list.append(frequency_df)

        feature_table = create_count_table(df_list=frequency_list)
    return (
        annotations,
        mutations,
        genes,
        feature_table,
    )


def run_amrfinderplus_n(
    tmp,
    amrfinderplus_db,
    input_sequence,
    organism,
    plus,
    report_all_equal,
    ident_min,
    coverage_min,
    translation_table,
    threads,
):
    cmd = [
        "amrfinder",
        "-n",
        input_sequence,
        "--database",
        str(amrfinderplus_db),
        "-o",
        f"{tmp}/amr_annotations.tsv",
        "--print_node",
        "--alignment_tool",
        "--nucleotide_output",
        f"{tmp}/amr_genes.fasta",
        "--mutation_all",
        f"{tmp}/amr_mutations.fasta",
    ]
    if threads:
        cmd.extend(["--threads", str(threads)])
    if organism:
        cmd.extend(["--organism", organism])
    if plus:
        cmd.append("--plus")
    if report_all_equal:
        cmd.append("--report_all_equal")
    if ident_min:
        cmd.extend(["--ident_min", str(ident_min)])
    if coverage_min:
        cmd.extend(["--coverage_min", str(coverage_min)])
    if translation_table:
        cmd.extend(["--translation_table", str(translation_table)])
    try:
        run_command(cmd, tmp, verbose=True)
    except subprocess.CalledProcessError as e:
        raise Exception(
            "An error was encountered while running AMRFinderPlus, "
            f"(return code {e.returncode}), please inspect "
            "stdout and stderr to learn more."
        )