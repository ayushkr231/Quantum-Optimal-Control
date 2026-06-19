# Derivative Removal by Adiabatic Gate (DRAG) Simulation

This directory contains a numerical simulation of single-qubit control in a superconducting transmon using the Quantum Toolbox in Python (QuTiP). It demonstrates the fundamental speed limits of weakly anharmonic qubits and their resolution via the DRAG protocol.

## 1. Introduction

Superconducting transmons are the dominant hardware architecture in modern quantum computing. Unlike ideal two-level spin systems, transmons are weakly anharmonic oscillators. The computational basis $\{|0\rangle, |1\rangle\}$ is formed by the lowest two energy eigenstates, but higher-energy states (e.g., $|2\rangle$) are easily accessible. 

Fast quantum gates are highly desirable to complete operations well within the coherence time of the qubit. However, a short pulse in the time domain corresponds to a broad spectrum in the frequency domain. When the spectral bandwidth of a fast control pulse approaches the anharmonicity of the transmon, it inadvertently drives the $|1\rangle \leftrightarrow |2\rangle$ transition. This loss of probability amplitude into the non-computational $|2\rangle$ state is known as **leakage error**.

## 2. Theoretical Formulation

### The Transmon Hamiltonian
In the rotating frame of the microwave drive frequency (assuming resonance with the $|0\rangle \leftrightarrow |1\rangle$ transition, $\omega_d = \omega_{01}$), the drift Hamiltonian for the lowest three levels simplifies to:

$$
H_0 = \alpha |2\rangle\langle 2|
$$

where $\alpha = \omega_{12} - \omega_{01}$ is the anharmonicity. In this simulation, we set $\alpha = -2\pi \times 250\mathrm{MHz}$, a standard value for modern transmons [2].

### The Microwave Drive
The control Hamiltonian driven by a microwave signal can be decomposed into an in-phase (X-quadrature) and an out-of-phase (Y-quadrature) component:

$$
H_d(t) = \Omega_X(t) H_X + \Omega_Y(t) H_Y
$$

where the coupling operators in the truncated three-level subspace are defined using the bosonic lowering operator $a = |0\rangle\langle1| + \sqrt{2}|1\rangle\langle2|$:

$$
H_X = \frac{1}{2}(a + a^\dagger) \quad \text{and} \quad H_Y = \frac{i}{2}(a^\dagger - a)
$$

For a standard operation (e.g., a $\pi$-pulse), we apply a purely real Gaussian envelope $\Omega_X(t) = \Omega_\pi s(t)$, leaving $\Omega_Y(t) = 0$. While this works for long pulses ($T \gg 1/|\alpha|$), it induces severe leakage for fast gates.

### The DRAG Correction
To suppress leakage, the DRAG protocol introduces a secondary, simultaneous pulse on the orthogonal Y-quadrature [1]. Using adiabatic perturbation theory, it can be shown that the optimal waveform to eliminate the $|1\rangle \leftrightarrow |2\rangle$ excitation is proportional to the time-derivative of the primary envelope:

$$
\Omega_Y(t) = -\lambda \frac{\dot{\Omega}_X(t)}{\alpha}
$$

where $\lambda$ is a dimensionless scaling parameter. For a simple Gaussian pulse without detuning corrections, the theoretical optimum is $\lambda = 1$ [3]. This derivative pulse creates destructive interference exactly at the $|1\rangle \leftrightarrow |2\rangle$ transition frequency, dynamically decoupling the computational subspace from the higher energy levels.

## 3. Simulation Implementation

The Python script (`drag_simulation.py`) implements this physics directly:

1. **Pulse Normalization**: We define a dimensionless Gaussian envelope $s(t)$ and use `scipy.integrate.quad` to strictly enforce the $\pi$-rotation condition: $\Omega_\pi \int_0^T s(t) dt = \pi$.
2. **Unitary Evolution**: The time-dependent Schrödinger equation is solved using QuTiP's `sesolve`. We pass the Hamiltonian as `[H0, [Hd, drive_coefficient], [HQ, drag_coeff]]`.
3. **Speed Benchmarking**: We sweep the pulse duration $T$ from $50\mathrm{ns}$ down to $2\mathrm{ns}$, recording the final population $P_2 = \langle 2 | \psi(T) \rangle \langle \psi(T) | 2 \rangle$ to observe the exponential increase in leakage for bare pulses.
4. **DRAG Optimization**: For a highly non-adiabatic $5\mathrm{ns}$ gate, we sweep the DRAG parameter $\lambda \in [0.5, 1.0]$. The numerical minimization of $P_2$ reveals an optimal parameter of $\lambda \approx 0.83$.

## 4. Results

![Simulation Results](./drag_simulation_results.png)

As demonstrated by the simulation, applying a standard $5\mathrm{ns}$ Gaussian pulse results in substantial leakage. By simply turning on the mathematically derived Y-quadrature DRAG drive, the leakage is suppressed by a factor of up to 8x, successfully pushing the fundamental speed limit of the transmon.

## 5. Usage

To run the full simulation and generate the data and plots:
```bash
pip install -r requirements.txt
python drag_simulation.py
```

## References

1. F. Motzoi, J. M. Gambetta, P. Rebentrost, and F. K. Wilhelm, *"Simple Pulses for Elimination of Leakage in Weakly Nonlinear Qubits"*, Phys. Rev. Lett. **103**, 110501 (2009). [DOI: 10.1103/PhysRevLett.103.110501](https://doi.org/10.1103/PhysRevLett.103.110501)
2. P. Krantz, M. Kjaergaard, F. Yan, T. P. Orlando, S. Gustavsson, and W. D. Oliver, *"A Quantum Engineer's Guide to Superconducting Qubits"*, Appl. Phys. Rev. **6**, 021318 (2019). [DOI: 10.1063/1.5089550](https://doi.org/10.1063/1.5089550)
3. J. M. Gambetta, F. Motzoi, S. T. Merkel, and F. K. Wilhelm, *"Analytic control methods for high-fidelity unitary operations in a weakly nonlinear oscillator"*, Phys. Rev. A **83**, 012308 (2011). [DOI: 10.1103/PhysRevA.83.012308](https://doi.org/10.1103/PhysRevA.83.012308)
