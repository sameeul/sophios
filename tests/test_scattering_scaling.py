import gc
import subprocess as sub
import time

# import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
import yaml


def test_scattering_scaling(minval: int = 100, maxval: int = 500, step: int = 100) -> None:
    """Tests that execution time scales linearly with input array size"""
    # First compile the workflow
    cmd = ['wic', '--yaml', 'examples/scattering_scaling.yml']
    sub.run(cmd, check=True)

    basedir = 'autogenerated'
    times = {}
    for i in range(minval, maxval + 1, step):
        # Modify the inputs file using the scaling parameter
        inputs_yml = f'{basedir}/scattering_scaling_inputs.yml'
        with open(inputs_yml, mode='r', encoding='utf-8') as f:
            d = yaml.safe_load(f.read())

        d['scattering_scaling__step__1__array_int___maxval'] = i

        with open(inputs_yml, mode='w', encoding='utf-8') as f:
            f.write(yaml.dump(d))

        # Garbage collect now, to avoid disturbing the workflow execution timings
        gc.collect()

        # Time the workflow execution
        t1 = time.time()
        cwl_workflow = f'{basedir}/scattering_scaling.cwl'
        cmd = ['cwltool', '--parallel', cwl_workflow, inputs_yml]
        # NOTE: Do NOT use toil for this test, simply because it is >10X slower
        # See https://github.com/DataBiosphere/toil/issues/4434
        # cmd = ['toil-cwl-runner', cwl_workflow, inputs_yml]
        # sub.run(cmd) # for debugging
        sub.run(cmd, check=True, stdout=sub.PIPE, stderr=sub.STDOUT)
        t2 = time.time()
        dt = t2 - t1

        times[i] = dt
        print('i, dt', i, dt)

    with open('times.csv', mode='w', encoding='utf-8') as t:
        for i_, dt_ in times.items():
            t.write(f'{i_}, {dt_}\n')

    # plt.scatter(times.keys(), times.values())
    # plt.savefig('times.png')

    # Fit the data to a quadratic model and check that the
    # leading coefficient is zero (within some tolerance).
    def quadratic(params: np.ndarray, x: float) -> float:
        return float(params[0]*x*x + params[1]*x + params[2])

    def residuals(params: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
        ys_model = np.array([quadratic(params, x) for x in xs])
        res: np.ndarray = ys - ys_model
        return res

    xs = np.array(list(times.keys()))
    ys = np.array(list(times.values()))
    init_guess_linear = [0.0, 1.0, 0.0]  # y = x
    result = least_squares(residuals, init_guess_linear, args=(xs, ys))

    print(result)
    if not result.success:
        print('Warning! least_squares optimization did not succeed!')

    tol_quad = 0.001  # adjust as necessary
    is_linear = abs(result.x[0]) < tol_quad
    if not is_linear:
        print('Warning! fit is not linear!')
    assert is_linear


if __name__ == '__main__':
    test_scattering_scaling(100, 500, 100)
