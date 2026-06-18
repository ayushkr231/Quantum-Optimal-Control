import numpy as np
import matplotlib.pyplot as plt
from qutip import destroy, basis, mesolve
from scipy.integrate import quad

# System Parameters
N = 3 # 3-level transmon
alpha_over_2pi = -0.3 # GHz (Anharmonicity)
alpha = alpha_over_2pi * 2 * np.pi # rad/ns

# Operators
a = destroy(N)
adag = a.dag()

# Unperturbed Hamiltonian in rotating frame at drive frequency omega_d = omega_01
# H0 = sum_j (omega_j - j * omega_d) |j><j|
# H0 = alpha * |2><2|
H0 = alpha * basis(N, 2) * basis(N, 2).dag()

# Drive Operators
H_x = 0.5 * (a + a.dag())
H_y = 0.5 * 1j * (adag - a)

# Initial state: |0>
psi0 = basis(N, 0)

# Projection operators for populations
P0 = basis(N, 0) * basis(N, 0).dag()
P1 = basis(N, 1) * basis(N, 1).dag()
P2 = basis(N, 2) * basis(N, 2).dag()

def get_pulse_amplitude(tg, sigma):
    # unnormalized pulse
    def unnorm_pulse(t):
        return np.exp(-0.5 * ((t - tg/2) / sigma)**2) - np.exp(-0.5 * (tg/2 / sigma)**2)
    area, _ = quad(unnorm_pulse, 0, tg)
    return np.pi / area

def simulate_pulse(tg, use_drag=False):
    sigma = tg / 4.0
    A = get_pulse_amplitude(tg, sigma)
    offset = np.exp(-0.5 * (tg/2 / sigma)**2)
    
    def Omega_x(t, args):
        if t < 0 or t > tg: return 0.0
        return A * (np.exp(-0.5 * ((t - tg/2) / sigma)**2) - offset)
        
    def Omega_y(t, args):
        if not use_drag: return 0.0
        if t < 0 or t > tg: return 0.0
        deriv = -A * ((t - tg/2) / sigma**2) * np.exp(-0.5 * ((t - tg/2) / sigma)**2)
        # DRAG Q channel = - d(Omega_x)/dt / alpha
        return -deriv / alpha

    H = [H0, [H_x, Omega_x], [H_y, Omega_y]]
    
    tlist = np.linspace(0, tg, 200)
    
    # Evolve the system
    result = mesolve(H, psi0, tlist, e_ops=[P0, P1, P2])
    
    return tlist, result.expect[0], result.expect[1], result.expect[2]

def main():
    print("Running simulations...")
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Plot 1: Fast gate without DRAG
    tg_fast = 5.0 # ns
    tlist, p0, p1, p2 = simulate_pulse(tg_fast, use_drag=False)
    axs[0].plot(tlist, p0, label='|0>')
    axs[0].plot(tlist, p1, label='|1>')
    axs[0].plot(tlist, p2, label='|2>')
    axs[0].set_title(f'Gaussian Pi-pulse (tg={tg_fast}ns)')
    axs[0].set_xlabel('Time (ns)')
    axs[0].set_ylabel('Population')
    axs[0].legend()

    # Plot 2: Leakage vs gate speed
    tg_sweep = np.linspace(3, 20, 30)
    leakage_no_drag = []
    leakage_drag = []
    for tg in tg_sweep:
        _, _, _, p2_no = simulate_pulse(tg, use_drag=False)
        leakage_no_drag.append(p2_no[-1])
        _, _, _, p2_yes = simulate_pulse(tg, use_drag=True)
        leakage_drag.append(p2_yes[-1])

    # Gate speed can be defined as 1/tg
    gate_speed = 1.0 / tg_sweep
    axs[1].plot(gate_speed, leakage_no_drag, label='No DRAG')
    axs[1].plot(gate_speed, leakage_drag, label='With DRAG')
    axs[1].set_title('Leakage to |2> vs Gate Speed')
    axs[1].set_xlabel('Gate Speed 1/tg (1/ns)')
    axs[1].set_ylabel('Final Population in |2>')
    axs[1].set_yscale('log')
    axs[1].legend()

    # Plot 3: Fast gate WITH DRAG
    tlist_drag, p0_drag, p1_drag, p2_drag = simulate_pulse(tg_fast, use_drag=True)
    axs[2].plot(tlist_drag, p0_drag, label='|0>')
    axs[2].plot(tlist_drag, p1_drag, label='|1>')
    axs[2].plot(tlist_drag, p2_drag, label='|2>')
    axs[2].set_title(f'DRAG Pulse (tg={tg_fast}ns)')
    axs[2].set_xlabel('Time (ns)')
    axs[2].set_ylabel('Population')
    axs[2].legend()

    plt.tight_layout()
    plt.savefig('drag_simulation_results.png', dpi=300)
    print("Simulation complete. Results saved to drag_simulation_results.png")

if __name__ == '__main__':
    main()
