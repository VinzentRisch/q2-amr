# ----------------------------------------------------------------------------
# Copyright (c) 2019-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from q2_types.feature_data import FeatureData
from q2_types.sample_data import SampleData
from qiime2.core.type import SemanticType

AMRFinderPlusDatabase = SemanticType("AMRFinderPlusDatabase")
AMRFinderPlusAnnotations = SemanticType(
    "AMRFinderPlusAnnotations",
    variant_of=[SampleData.field["type"], FeatureData.field["type"]],
)
