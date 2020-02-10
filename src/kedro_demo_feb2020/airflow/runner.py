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


"""``AirflowRunner`` is an ``AbstractRunner`` implementation. It can
be used to convert the ``Pipeline`` into Airflow operators.
"""

from typing import Callable

from airflow.operators.python_operator import PythonOperator
from kedro.io import DataCatalog, MemoryDataSet
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from kedro.runner import AbstractRunner, run_node
from slugify import slugify


class AirflowRunner(AbstractRunner):
    """``AirflowRunner`` is an ``AbstractRunner`` implementation. It can
    be used to convert the ``Pipeline`` into Airflow operators.
    """

    def __init__(self, dag, process_context, operator_arguments):
        self._dag = dag
        self._process_context = process_context
        self._operator_arguments = operator_arguments

    def create_task(self, node: Node, catalog: DataCatalog) -> Callable:
        """Create a task to be executed by the runner with a simple call

        Args:
            node (Node): The node to be converted to a task
            catalog (DataCatalog): The DataCatalog to be used for loading and
                saving the data

        Returns:
            Callable: A callable, which will load the inputs, execute the
                node and save the outputs

        """

        print("create task")

        def task(**kwargs):
            task_catalog = catalog.shallow_copy()
            task_catalog = self._process_context(task_catalog, **kwargs)
            run_node(node, task_catalog)

        return task

    def create_default_data_set(
        self, ds_name: str, max_loads: int = None
    ):  # pylint: disable=arguments-differ
        """Factory method for creating the default data set for the runner.

        Args:
            ds_name: Name of the missing data set
            max_loads: Maximum number of times ``load`` method of the
                default data set is allowed to be invoked. Any number of
                calls is allowed if the argument is not set.

        Raises:
            ValueError: Always

        """
        raise ValueError(
            "Data set '{}' is not registered in the data catalog.\n"
            "AirflowRunner does not support unregistered data sets.".format(ds_name)
        )

    def _run(self, pipeline: Pipeline, catalog: DataCatalog) -> None:
        """The method implementing sequential pipeline running.

        Args:
            pipeline: The ``Pipeline`` to run.
            catalog: The ``DataCatalog`` from which to fetch data.

        Raises:
            ValueError: if the Pipeline is not compatible with Airflow
        """

        print("_run")

        data_sets = catalog._data_sets  # pylint: disable=protected-access
        memory_data_sets = []
        for name, data_set in data_sets.items():
            if name in pipeline.all_outputs() and isinstance(data_set, MemoryDataSet):
                memory_data_sets.append(name)

        if memory_data_sets:
            raise ValueError(
                "The following output data sets are memory data sets: {}\n"
                "AirflowRunner does not support output to MemoryDataSets".format(
                    ", ".join("'{}'".format(ds) for ds in memory_data_sets)
                )
            )

        node_dependencies = pipeline.node_dependencies
        operators_by_node = {}
        for node in node_dependencies:
            name = slugify(node.name)
            operators_by_node[node] = PythonOperator(
                task_id=name,
                provide_context=True,
                python_callable=self.create_task(node, catalog),
                dag=self._dag,
                **self._operator_arguments(name)
            )

        for node, dependencies in node_dependencies.items():
            for dependency in dependencies:
                operators_by_node[node].set_upstream(operators_by_node[dependency])
