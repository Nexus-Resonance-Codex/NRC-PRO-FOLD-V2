import numpy as np
from scipy.optimize import minimize

class NRCForcefield:
    def __init__(self, N):
        self.N = N
        self.phi = (1 + np.sqrt(5)) / 2  # Golden ratio

        # Physical constants
        self.CA_CA_BOND_LENGTH = 3.8  # Target bond length in Å
        self.SIGMA = 3.38              # Minimum at 3.8A
        self.EPSILON = 5.0              # Stronger repulsion
        self.K_BOND = 5000.0            # Very rigid backbone
        self.RG_TARGET = 17.0           # Target Rg for N=189
        self.MODULAR_SCALE = 3.8        # Scale TTT-7 to Angstrom level

        self.x0 = self.spherical_fibonacci_initialization(N)

    def spherical_fibonacci_initialization(self, N):
        """Generates a 3D spherical distribution of points."""
        indices = np.arange(1, N + 1)
        z = 1 - (2 * indices - 1) / N
        phi_angle = 2 * np.pi / (self.phi**2)
        theta = phi_angle * indices

        x = np.sqrt(1 - z**2) * np.cos(theta)
        y = np.sqrt(1 - z**2) * np.sin(theta)

        # Start as a sphere of radius RG_TARGET
        coords_3d = np.column_stack((x, y, z)) * self.RG_TARGET
        return coords_3d.flatten()

    def energy_and_gradient(self, coords_flat):
        coords = coords_flat.reshape(-1, 3)
        n = self.N
        grad = np.zeros_like(coords)
        total_e = 0.0

        # 1. Harmonic Bonds (Backbone)
        diff_backbone = coords[1:] - coords[:-1]
        d_backbone = np.linalg.norm(diff_backbone, axis=1) + 1e-9

        bond_e = self.K_BOND * np.sum((d_backbone - self.CA_CA_BOND_LENGTH)**2)
        total_e += bond_e

        # Gradient of bond energy
        bond_mag = 2 * self.K_BOND * (d_backbone - self.CA_CA_BOND_LENGTH) / d_backbone

        grad[:-1] += -bond_mag[:, np.newaxis] * diff_backbone
        grad[1:] += bond_mag[:, np.newaxis] * diff_backbone

        # 2. Non-bonded Interactions (LJ + TTT-7 + QRT + Confinement)
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        dists = np.sqrt(np.sum(diff**2, axis=-1) + 1e-9)

        iu = np.triu_indices(n, k=2)  # Non-adjacent pairs
        d = dists[iu]

        # Lennard-Jones
        s_r = self.SIGMA / d
        s_r6 = s_r**6
        s_r12 = s_r6**2
        lj_e = self.EPSILON * (s_r12 - s_r6)
        total_e += np.sum(lj_e)

        lj_grad_mag = self.EPSILON * (-12 * s_r12 / d + 6 * s_r6 / d)

        # TTT-7 Resonance (scaled to Ångström level)
        ttt_factor = 1618.0 / (9.0 * self.MODULAR_SCALE)
        ttt_e = -np.cos(2 * np.pi * d * ttt_factor)
        total_e += np.sum(ttt_e)

        ttt_grad_mag = 2 * np.pi * ttt_factor * np.sin(2 * np.pi * d * ttt_factor)

        # QRT Damping (Global attractive potential to ensure globular fold)
        qrt_e = (d / self.phi)**2 * 0.01
        total_e += np.sum(qrt_e)
        qrt_grad_mag = 2 * d / (self.phi**2) * 0.01

        # Global Confinement Potential (Prevents collapse)
        # rg = sqrt(mean(squared distances from centroid))
        mean_coords = np.mean(coords, axis=0)
        rel_coords = coords - mean_coords
        sum_sq_dist = np.sum(rel_coords**2)
        rg = np.sqrt(sum_sq_dist / n)
        
        conf_e = 1.0 * (rg - self.RG_TARGET)**2
        total_e += conf_e

        # dE/dxi = dE/drg * drg/dxi
        # drg/dxi = (1/rg) * (1/n) * (xi - x_mean)
        dE_drg = 2.0 * (rg - self.RG_TARGET)
        conf_grad = (dE_drg / (rg * n + 1e-9)) * rel_coords
        grad += conf_grad

        # Combine Non-bonded Gradients
        total_mag = lj_grad_mag + ttt_grad_mag + qrt_grad_mag

        mag_matrix = np.zeros((n, n))
        mag_matrix[iu] = total_mag / d
        mag_matrix = mag_matrix + mag_matrix.T

        grad += np.sum(mag_matrix[:, :, np.newaxis] * diff, axis=1)

        return total_e, grad.flatten()

    def optimize(self, max_iter=500):
        res = minimize(
            self.energy_and_gradient,
            self.x0,
            method='L-BFGS-B',
            jac=True,
            options={'maxiter': max_iter, 'disp': False}
        )
        self.x0 = res.x
        return res.x.reshape(-1, 3)

if __name__ == "__main__":
    import time
    n_residues = 189
    ff = NRCForcefield(n_residues)
    start = time.time()
    final_coords = ff.optimize(max_iter=500)
    print(f"Optimized 189 AA in {time.time() - start:.2f}s")
    
    mean_pos = np.mean(final_coords, axis=0)
    rg = np.sqrt(np.mean(np.sum((final_coords - mean_pos)**2, axis=1)))
    print(f"Final Radius of Gyration: {rg:.2f} Å")
