# Transmon DRAG Simulation

This repository contains a complete quantum simulation of a 3-level transmon qubit system, built using [QuTiP](https://qutip.org/) (Quantum Toolbox in Python).

## Overview
The goal of this project is to model the effect of applying microwave pulses to a transmon qubit and to demonstrate the power of **Derivative Removal by Adiabatic Gate (DRAG)**.

Because a transmon is not a perfect 2-level system (it has a 3rd level, $|2\rangle$, very close in energy), driving the $|0\rangle \rightarrow |1\rangle$ transition too fast will inadvertently "leak" population into the $|2\rangle$ state. 

This simulation proves that by applying a secondary out-of-phase microwave drive (proportional to the derivative of the primary drive), we can destructively interfere with the transitions that cause this leakage, effectively solving the transmon speed limit.

## What the Simulation Does
1. **Pulse Shaping**: Creates and dynamically normalizes a Gaussian pi-pulse.
2. **Speed Sweep**: Demonstrates that as pulse duration $T$ decreases (gates get faster), leakage into $|2\rangle$ exponentially increases.
3. **DRAG Implementation**: Constructs the theoretical Y-quadrature correction to the microwave drive.
4. **DRAG Optimization**: Sweeps the DRAG parameter $\lambda$ to find the absolute minimum leakage for a fast 5ns gate.
5. **Comparison Benchmarking**: Compares the final leakage across various gate speeds with and without the DRAG correction, calculating the suppression factor.

## Requirements
To run this simulation, you need Python and the following packages:
- `qutip`
- `numpy`
- `scipy`
- `matplotlib`

You can install them via:
```bash
pip install -r requirements.txt
```

## Usage
Simply run the simulation script:
```bash
python drag_simulation.py
```
This will sequentially output a series of matplotlib plots detailing the physics at each stage of the experiment, culminating in a table printed to the console showing the exact suppression factors achieved by DRAG.
