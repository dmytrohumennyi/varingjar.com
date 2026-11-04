# Væringjar II — EXP-01 mathematical baseline

This package replaces the earlier toy continuous-time example.

## Important distinction

The plots are **outputs**, not inputs. The execution order is:

1. execute the plant transition;
2. execute the external damage event;
3. update the resource state;
4. calculate `S`, `P`, `F` and the operational regime;
5. write every time step to CSV;
6. only then read the CSV and generate plots.

`plot_results.py` contains no state-generation equations.

## Mathematical mapping

Implemented directly:

- LPV plant: `x[k+1] = A_d(rho[k]) x[k] + B_d(rho[k]) u[k] + E_d(rho[k]) xi[k]`
- reference scalar model: `A = 0.9`, `B = 1.0`
- irreversible resource equation:
  `rho[i,k+1] = rho[i,k] - lambda_i(s[k])*dt - eta_i*D[i,k]`
  with `u_rep = 0`
- `S[k] = mean(rho[k])`
- `P[k] = exp(-0.5*|e[k]|)`
- `F[k] = S[k]*P[k]`
- regime thresholds `0.8` and `0.3`
- gains `K_N=0.8`, `K_K=0.5`, `K_SK=0.2`

## Explicit EXP-01 specialization

The general theory does not uniquely prescribe how two destroyed/healthy
actuators enter `B_d(rho)`. EXP-01 therefore states this specialization explicitly:

`B_d(rho) = (B/2) [rho1, rho2]`

That means a destroyed second actuator has **zero physical control authority**:
`rho2 = 0 => B2_eff = 0`.

This assumption is visible in the manifest and source code. It is not hidden in
the plotting layer.

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

## Scientific status

The mathematical framework is implemented directly. The two-actuator LPV
specialization and the deterministic disturbance profile are EXP-01 model
assumptions. They must not be described as experimentally identified physical
parameters.

For a physical validation paper, the next step is to replace this specialization
with an identified actuator/robot model or one of the paper's fully parameterized
fault scenarios.
