# Copyright 2018-2019 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.
"""Pipeline construction."""

from typing import Dict

from kedro.pipeline import Pipeline
from kedro_demo_feb2020.nodes.primary.demo import create_pipeline_primary_demo
from kedro_demo_feb2020.nodes.primary.pi import create_pipeline_primary_pi
from kedro_demo_feb2020.nodes.feature.pi import create_pipeline_feature_pi
from kedro_demo_feb2020.nodes.model_output.demo import create_pipeline_model_output_demo
from kedro_demo_feb2020.nodes.model_input.demo import create_pipeline_model_input_demo


def create_pipelines(**kwargs) -> Dict[str, Pipeline]:
    """Create the project's pipeline.

    Args:
        kwargs: Ignore any additional arguments added in the future.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """

    pipeline_primary = create_pipeline_primary_demo() + create_pipeline_primary_pi()
    pipeline_feature = create_pipeline_feature_pi()
    pipelilne_model_input = create_pipeline_model_input_demo()
    pipeline_model_output = create_pipeline_model_output_demo()

    return {
        "primary": pipeline_primary,
        "feature": pipeline_feature,
        "model_input": pipelilne_model_input,
        "model_output": pipeline_model_output,
        "__default__": pipeline_primary
        + pipeline_feature
        + pipelilne_model_input
        + pipeline_model_output,
    }
