import argparse
import sys
from pathlib import Path
from unittest.mock import patch

from . import _version
__version__ = _version.get_versions()['version']

parser = argparse.ArgumentParser(prog='main', description='Convert a high-level yaml workflow file to CWL.')
parser.add_argument('--yaml', type=str, required=('--generate_schemas' not in sys.argv),
                    help='Yaml workflow file')
parser.add_argument('--inputs_file', type=str, required=False, default='',
                    help='Additional inputs Yaml file')
parser.add_argument('--config_file', type=str, required=False, default=str(Path().home()/'wic'/'global_config.json'),
                    help='User provided (JSON) config file')
# version action exits the parser Ref : https://github.com/python/cpython/blob/1f515e8a109204f7399d85b7fd806135166422d9/Lib/argparse.py#L1167
parser.add_argument('--version', action='version', version=__version__,
                    default='==SUPPRESS==', help='Current version of the Workflow Inference Compiler')
parser.add_argument('--generate_schemas', default=False, action="store_true",
                    help='Generate schemas for the files in config.json (search_paths_wic and search_paths_cwl)')
parser.add_argument('--homedir', type=str, required=False, default=str(Path().home()),
                    help='The users home directory. This is necessary because CWL clears environment variables (e.g. HOME)')
parser.add_argument('--insert_steps_automatically', default=False, action="store_true",
                    help='''Attempt to fix inference failures by speculatively
                    inserting workflow steps from a curated whitelist.''')
parser.add_argument('--no_provenance', default=False, action="store_true",
                    help='Do not use the --provenance feature of CWL. (You should only disable provenance if absolutely necessary.)')
parser.add_argument('--copy_output_files', default=False, action="store_true",
                    help='Copies output files from the cachedir to outdir/ (automatically enabled with --run_local)')

parser.add_argument('--parallel', default=False, action="store_true",
                    help='''When running locally, execute independent steps in parallel.
                    \nThis is required for real-time analysis, but it may cause issues with
                    \nhanging (particularly when scattering). See user guide for details.''')
parser.add_argument('--quiet', default=False, action="store_true",
                    help='''Disable verbose output. This will not print out the commands used for each step,
                    and it will capture all stdout/stderr into log files for each step.''')
parser.add_argument('--cwl_runner', type=str, required=False, default='cwltool', choices=['cwltool', 'toil-cwl-runner'],
                    help='The CWL runner to use for running workflows locally.')
parser.add_argument('--allow_raw_cwl', default=False, action="store_true",
                    help='Do not check whether the input to a workflow step refers to the workflow inputs: tag')
parser.add_argument('--ignore_docker_install', default=False, action="store_true",
                    help='''Do not check whether docker is installed before running workflows.
                    \n--ignore_docker_install does NOT change whether or not any step in your workflow uses docker!''')
parser.add_argument('--ignore_docker_processes', default=False, action="store_true",
                    help='Do not check whether there are too many running docker processes before running workflows.')
parser.add_argument('--container_engine', default='docker',
                    help='Specify which command to use to run OCI containers.')

parser.add_argument('--docker_remove_entrypoints', default=False, action="store_true",
                    help='''Remove entrypoints from docker images before running workflows.
                    See https://cwl.discourse.group/t/override-docker-entrypoint-in-command-line-tool/695/2
                    If your CWL CommandLineTools rely on non-portable docker entrypoints
                    (i.e. if they do NOT explicitly have baseCommand: and/or arguments: tags)
                    then this flag will almost certainly cause your workflows to fail.
                    In other words, this flag can be used to tell you if your workflows are
                    trapped inside a walled garden of docker containers or if there is at least a chance that
                    they can be run in dev environments (conda, etc) and/or directly on the host machine.''')

parser.add_argument('--partial_failure_enable', default=False, action="store_true",
                    help='''Let workflows to continue with partial failures
                    \n(i.e. run next steps after failure step by guarding for possible no input)''')

parser.add_argument('--partial_failure_success_codes', nargs='*', type=int, default=[0, 1], required=False,
                    help='Let users add custom error codes to be treated as success')

group_run = parser.add_mutually_exclusive_group()
group_run.add_argument('--generate_run_script', default=False, action="store_true",
                       help='Just generates run.sh and exits. Does not actually invoke ./run.sh')
group_run.add_argument('--run_local', default=False, action="store_true",
                       help='After generating the cwl file(s), run it on your local machine.')

parser.add_argument('--cwl_inline_subworkflows', default=False, action="store_true",
                    help='Before generating the cwl file, inline all subworkflows.')
parser.add_argument('--inference_disable', default=False, action="store_true",
                    help='Disables use of the inference algorithm when compiling.')
parser.add_argument('--inference_use_naming_conventions', default=False, action="store_true",
                    help='Enables the use of naming conventions in the inference algorithm')
parser.add_argument('--validate_plugins', default=False, action="store_true",
                    help='Validate all CWL CommandLineTools')
parser.add_argument('--ignore_validation_errors', default=False, action="store_true",
                    help='Temporarily ignore validation errors. Do not use this permanently!')
parser.add_argument('--no_skip_dollar_schemas', default=False, action="store_true",
                    help='''Does not skip processing $schemas tags in CWL files for performance.
                    Skipping significantly improves initial validation performance, but is not always desired.
                    See https://github.com/common-workflow-language/cwltool/issues/623''')
parser.add_argument('--cachedir', type=str, required=False, default='cachedir',
                    help='The directory to save intermediate results; useful with RealtimePlots.py')

parser.add_argument('--graphviz', default=False, action="store_true",
                    help='Generate a DAG using graphviz.')
parser.add_argument('--graph_label_edges', default=False, action="store_true",
                    help='Label the graph edges with the name of the intermediate input/output.')
parser.add_argument('--graph_label_stepname', default=False, action="store_true",
                    help='Prepend the step name to each step node.')
parser.add_argument('--graph_show_inputs', default=False, action="store_true",
                    help='Add nodes to the graph representing the workflow inputs.')
parser.add_argument('--graph_show_outputs', default=False, action="store_true",
                    help='Add nodes to the graph representing the workflow outputs.')
parser.add_argument('--graph_inline_depth', type=int, required=False, default=sys.maxsize,
                    help='Controls the depth of subgraphs which are displayed.')
parser.add_argument('--graph_dark_theme', default=False, action="store_true",
                    help='Changees the color of the fonts and edges from white to black.')
parser.add_argument('--custom_net', type=str, required=False,
                    help='Passes --custom-net flag to cwltool.')


def get_args(yaml_path: str = '', suppliedargs: list[str] = []) -> argparse.Namespace:
    """This is used to get mock command line arguments, default + suppled args

    Returns:
        argparse.Namespace: The mocked command line arguments
    """
    defaultargs = ['wic', '--yaml', yaml_path]  # ignore --yaml
    testargs = defaultargs + suppliedargs
    with patch.object(sys, 'argv', testargs):
        args: argparse.Namespace = parser.parse_args()
    return args
