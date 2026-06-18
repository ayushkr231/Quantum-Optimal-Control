# Quantum Optimal Control

This repository contains simulations and implementations of various Quantum Optimal Control (QOC) techniques used in quantum computing.

## Contents

### 1. [DRAG Simulation](./DRAG_Simulation)
Derivative Removal by Adiabatic Gate (DRAG) is a pulse-shaping technique used to suppress leakage to higher energy states (like $|2\rangle$) in weakly anharmonic qubits, such as transmons. 
- Demonstrates leakage caused by fast Gaussian pi-pulses.
- Implements the analytical Y-quadrature correction.
- Sweeps parameters to optimize the DRAG coefficient.

*Navigate to the `DRAG_Simulation` folder to run the experiment.*

---
*More QOC techniques (like GRAPE, CRAB, etc.) can be added to this repository in the future.*
