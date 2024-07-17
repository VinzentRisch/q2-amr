import os
from unittest.mock import MagicMock, patch

from q2_types.genome_data import LociDirectoryFormat
from qiime2.plugin.testing import TestPluginBase

from q2_amr.amrfinderplus.sequences import annotate_sequences_amrfinderplus
from q2_amr.amrfinderplus.tests.test_sample_data import mock_run_amrfinderplus_n


class TestAnnotateSequencesAMRFinderPlus(TestPluginBase):
    package = "q2_amr.amrfinderplus.tests"

    def test_annotate_sequences_amrfinderplus_dna(self):
        dna_sequences = MagicMock()
        self._helper(
            dna_sequences=dna_sequences, protein_sequences=None, gff=None, organism=None
        )

    def test_annotate_sequences_amrfinderplus_prot_gff(self):
        protein_sequences = MagicMock()
        gff = LociDirectoryFormat()
        gff_content = "##gff-version 3\nchr1\t.\tgene\t1\t1000\t.\t+\t.\tID=gene1"
        with open(os.path.join(str(gff), "loci.gff"), "w") as file:
            file.write(gff_content)
        self._helper(
            dna_sequences=None,
            protein_sequences=protein_sequences,
            gff=gff,
            organism="Escherichia",
        )

    def test_annotate_sequences_amrfinderplus_dna_gff(self):
        dna_sequences = MagicMock()
        gff = MagicMock()
        amrfinderplus_db = MagicMock()
        with self.assertRaisesRegex(
            ValueError,
            "GFF input can only be given in combination with protein-sequence input.",
        ):
            annotate_sequences_amrfinderplus(
                dna_sequences=dna_sequences,
                gff=gff,
                amrfinderplus_db=amrfinderplus_db,
            )

    def test_annotate_sequences_amrfinderplus_dna_prot(self):
        dna_sequences = MagicMock()
        protein_sequences = MagicMock()
        amrfinderplus_db = MagicMock()
        with self.assertRaisesRegex(
            ValueError,
            "DNA-sequence and protein-sequence inputs together can only be given in "
            "combination with GFF input.",
        ):
            annotate_sequences_amrfinderplus(
                dna_sequences=dna_sequences,
                protein_sequences=protein_sequences,
                amrfinderplus_db=amrfinderplus_db,
            )

    def _helper(self, dna_sequences, protein_sequences, gff, organism):
        amrfinderplus_db = MagicMock()
        with patch(
            "q2_amr.amrfinderplus.sequences.run_amrfinderplus_n",
            side_effect=mock_run_amrfinderplus_n,
        ):
            result = annotate_sequences_amrfinderplus(
                dna_sequences=dna_sequences,
                protein_sequences=protein_sequences,
                gff=gff,
                amrfinderplus_db=amrfinderplus_db,
                organism=organism,
            )

            self.assertTrue(
                os.path.exists(os.path.join(str(result[0]), "amr_annotations.tsv"))
            )
            if organism:
                self.assertTrue(
                    os.path.exists(os.path.join(str(result[1]), "amr_mutations.tsv"))
                )
            self.assertTrue(
                os.path.exists(os.path.join(str(result[2]), "amr_genes.fasta"))
            )
            self.assertTrue(
                os.path.exists(os.path.join(str(result[3]), "amr_proteins.fasta"))
            )
