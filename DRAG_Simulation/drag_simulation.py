from qutip import *
import numpy as np
import matplotlib.pyplot as plt
from math import pi, sqrt
from scipy.integrate import quad

# --- 1. Pulse Parameters and Definitions ---

def s(t, args):
    """Dimensionless Gaussian envelope, peak = 1"""
    T = args['T']
    sigma = T / 4
    return np.exp(-(t - T/2)**2 / (2 * sigma**2))

def s_dot(t, args):
    """Analytical time derivative of the Gaussian envelope s(t)"""
    T = args['T']
    sigma = T / 4
    s_val = np.exp(-(t - T/2)**2 / (2 * sigma**2))
    return -((t - T/2) / sigma**2) * s_val

def drive_coefficient(t, args):
    """Time-dependent coefficient for the in-phase Hdrive"""
    Omega = args['Omega']
    return Omega * s(t, args)

def drag_coeff(t, args):
    """
    Time-dependent coefficient for the DRAG out-of-phase drive.
    Formula: -lambda_drag * d(drive)/dt / alpha
    """
    lambda_drag = args['lambda_drag']
    alpha = args['alpha']
    Omega = args['Omega']
    return -lambda_drag * Omega * s_dot(t, args) / alpha


# --- 2. System Definition ---

alpha = -2 * pi * 250e6 # Anharmonicity (250 MHz)

# Static Hamiltonian (3-level, rotating frame)
H0 = Qobj(np.array([
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, alpha]
]))

# In-phase Drive Hamiltonian (X-channel)
Hd = Qobj(np.array([
    [0,   0.5, 0],
    [0.5, 0,   1/sqrt(2)],
    [0,   1/sqrt(2), 0]
]))

# Quadrature Drive Hamiltonian (Y-channel)
HQ = Qobj(np.array([
    [0,    -0.5j,           0],
    [0.5j,  0,             -0.5j * sqrt(2)],
    [0,     0.5j * sqrt(2), 0]
]))

# Projection operators
P0 = basis(3, 0) * basis(3, 0).dag()
P1 = basis(3, 1) * basis(3, 1).dag()
P2 = basis(3, 2) * basis(3, 2).dag()

# Initial state |0>
psi0 = Qobj(basis(3, 0))


# --- 3. Single 50ns Pi-Pulse Simulation (No DRAG) ---

print("Running 50ns Pi-Pulse Simulation (No DRAG)...")
T = 50e-9
area, _ = quad(lambda t: s(t, {'T': T}), 0, T)
Omega_pi = pi / area
args = {'T': T, 'Omega': Omega_pi}

H_3lvl = [H0, [Hd, drive_coefficient]]
tlist = np.linspace(0, T, 1000)

result = sesolve(H_3lvl, psi0, tlist, e_ops=[P0, P1, P2], args=args)

plt.figure(figsize=(8, 5))
plt.plot(tlist * 1e9, result.expect[0], label='Population in |0>')
plt.plot(tlist * 1e9, result.expect[1], label='Population in |1>')
plt.plot(tlist * 1e9, result.expect[2], label='Population in |2>')
plt.xlabel('Time (ns)')
plt.ylabel('Population')
plt.title('Evolution of a 3-Level System (Pi-Pulse, T=50ns)')
plt.legend()
plt.grid(True)
plt.show()


# --- 4. Leakage vs Gate Speed (No DRAG) ---

print("Running Leakage vs Gate Speed sweep (No DRAG)...")
T_list = [50e-9, 20e-9, 10e-9, 5e-9, 2e-9]
P2_final_no_drag = []

fig, axes = plt.subplots(len(T_list), 1, figsize=(8, 4*len(T_list)))
for i, T_val in enumerate(T_list):
    area, _ = quad(lambda t: s(t, {'T': T_val}), 0, T_val)
    args_T = {'T': T_val, 'Omega': pi / area}
    
    tlist_T = np.linspace(0, T_val, 1000)
    res_T = sesolve(H_3lvl, psi0, tlist_T, e_ops=[P0, P1, P2], args=args_T)
    
    P2_final_no_drag.append(res_T.expect[2][-1])
    
    ax = axes[i]
    ax.plot(tlist_T * 1e9, res_T.expect[0], label='P₀')
    ax.plot(tlist_T * 1e9, res_T.expect[1], label='P₁')
    ax.plot(tlist_T * 1e9, res_T.expect[2], label='P₂')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Population')
    ax.set_title(f'T = {T_val*1e9:.0f} ns — P₂(final) = {res_T.expect[2][-1]:.4f}')
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.show()


# --- 5. Implementation of DRAG for T=5ns ---

print("Running 5ns Pi-Pulse Simulation (With DRAG)...")
H_3lvl_drag = [H0, [Hd, drive_coefficient], [HQ, drag_coeff]]

T_fast = 5e-9
lambda_drag = 1.0
area_fast, _ = quad(lambda t: s(t, {'T': T_fast}), 0, T_fast)

solver_args = {
    'T': T_fast,
    'Omega': pi / area_fast,
    'lambda_drag': lambda_drag,
    'alpha': alpha
}

tlist_fast = np.linspace(0, T_fast, 1000)
res_drag = sesolve(H_3lvl_drag, psi0, tlist_fast, e_ops=[P0, P1, P2], args=solver_args)

plt.figure(figsize=(8, 5))
plt.plot(tlist_fast * 1e9, res_drag.expect[0], label='Population in |0>')
plt.plot(tlist_fast * 1e9, res_drag.expect[1], label='Population in |1>')
plt.plot(tlist_fast * 1e9, res_drag.expect[2], label='Population in |2>')
plt.xlabel('Time (ns)')
plt.ylabel('Population')
plt.title(f'3-Level System with DRAG (T={T_fast*1e9:.0f}ns)\nFinal P2 (Leakage) = {res_drag.expect[2][-1]:.6f}')
plt.legend()
plt.grid(True)
plt.show()


# --- 6. Optimization of DRAG parameter (lambda) ---

print("Optimizing DRAG parameter (lambda)...")
lambda_list = np.linspace(0.5, 1, 40)
P2_lambda = []

for lam in lambda_list:
    solver_args['lambda_drag'] = lam
    res_lam = sesolve(H_3lvl_drag, psi0, tlist_fast, e_ops=[P0, P1, P2], args=solver_args)
    P2_lambda.append(res_lam.expect[2][-1])

plt.figure(figsize=(8, 5))
plt.plot(lambda_list, P2_lambda, 'o-')
plt.xlabel('λ (DRAG parameter)')
plt.ylabel('Leakage P₂ at end of pulse')
plt.title(f'P₂ vs λ at T = {T_fast*1e9:.0f} ns')
plt.axvline(x=1, color='r', linestyle='--', label='λ = 1 (theory)')
plt.legend()
plt.grid(True)
plt.show()

print(f"Minimum P₂ = {min(P2_lambda):.6f} at λ = {lambda_list[np.argmin(P2_lambda)]:.2f}")


# --- 7. Final Comparison: DRAG vs No DRAG ---

print("Running final DRAG vs No DRAG comparison...")
P2_no_drag = []
P2_with_drag = []

for T_val in T_list:
    area, _ = quad(lambda t: s(t, {'T': T_val}), 0, T_val)
    Omega_pi = pi / area
    tlist_T = np.linspace(0, T_val, 1000)

    # Without DRAG
    args_bare = {'T': T_val, 'Omega': Omega_pi}
    res_bare = sesolve(H_3lvl, psi0, tlist_T, e_ops=[P0, P1, P2], args=args_bare)
    P2_no_drag.append(res_bare.expect[2][-1])

    # With DRAG (lambda=1)
    args_drag = {'T': T_val, 'Omega': Omega_pi, 'lambda_drag': 1.0, 'alpha': alpha}
    res_drag = sesolve(H_3lvl_drag, psi0, tlist_T, e_ops=[P0, P1, P2], args=args_drag)
    P2_with_drag.append(res_drag.expect[2][-1])

T_ns = [T_val * 1e9 for T_val in T_list]

plt.figure(figsize=(8, 5))
plt.semilogy(T_ns, P2_no_drag, 'o-', label='No DRAG')
plt.semilogy(T_ns, P2_with_drag, 's--', label='DRAG (λ=1)')
plt.xlabel('Pulse duration T (ns)')
plt.ylabel('Leakage P₂ (log scale)')
plt.title('Leakage vs Pulse Speed: DRAG vs No DRAG')
plt.legend()
plt.grid(True, which='both')
plt.show()

print("\n--- Final Results ---")
print("T (ns) | P2 no DRAG | P2 with DRAG | Suppression factor")
print("-" * 55)
for i, T_val in enumerate(T_ns):
    suppression = P2_no_drag[i]/P2_with_drag[i] if P2_with_drag[i] > 0 else float('inf')
    print(f"{T_val:6.0f} | {P2_no_drag[i]:.6f}   | {P2_with_drag[i]:.6f}     | {suppression:.1f}x")
print("-------------------------------------------------------")
