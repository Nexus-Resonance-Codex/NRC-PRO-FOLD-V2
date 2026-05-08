import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist

class NRCForcefield:
    def __init__(self, N):
        self.N = N
        self.phi = (1 + np.sqrt(5)) / 2
        self.x0 = self.spherical_fibonacci_initialization(N)

    def spherical_fibonacci_initialization(self, N):
        """Generates a 3D spherical distribution of points to avoid 2D collapse."""
        # Note: indices i go from 1 to N
        indices = np.arange(1, N + 1)
        z = 1 - (2 * indices - 1) / N
        # phi_angle = 2 * pi / phi^2
        phi_angle = 2 * np.pi / (self.phi**2)
        theta = phi_angle * indices
        
        x = np.sqrt(1 - z**2) * np.cos(theta)
        y = np.sqrt(1 - z**2) * np.sin(theta)
        # Scale to a reasonable starting radius for a protein (e.g., 10-20A)
        # But for optimization, 1.0 radius is fine as a starting manifold.
        return np.column_stack((x, y, z)).flatten()

    def qrt_damping_vectorized(self, d):
        """Quantum Residue Turbulence (QRT) Damping potential."""
        # V(d) = sin(phi*sqrt(2)*51.85*d) * exp(-d^2/phi) + cos(pi/phi*d)
        k = self.phi * np.sqrt(2) * 51.85
        return np.sin(k * d) * np.exp(-d**2 / self.phi) + np.cos(np.pi / self.phi * d)

    def qrt_damping_derivative(self, d):
        """Derivative of QRT Damping potential w.r.t. distance d."""
        k = self.phi * np.sqrt(2) * 51.85
        # d/dd [sin(kd) * exp(-d^2/phi)] = k*cos(kd)*exp(-d^2/phi) + sin(kd)*exp(-d^2/phi)*(-2d/phi)
        term1_deriv = (k * np.cos(k * d) - (2 * d / self.phi) * np.sin(k * d)) * np.exp(-d**2 / self.phi)
        # d/dd [cos(pi/phi * d)] = -pi/phi * sin(pi/phi * d)
        term2_deriv = -(np.pi / self.phi) * np.sin(np.pi / self.phi * d)
        return term1_deriv + term2_deriv

    def ttt_7_penalty_vectorized(self, d):
        """Trageser Tensor Theorem (TTT-7) Modular Stability potential."""
        d_int = np.floor(np.abs(d) * 1618).astype(int)
        mod_val = d_int % 9
        penalty = np.zeros_like(d, dtype=float)
        voids = (mod_val == 0) | (mod_val == 3) | (mod_val == 6) | (mod_val == 9)
        penalty[voids] = 1.0 / self.phi
        stable = (mod_val == 7)
        penalty[stable] = -1.0
        return penalty

    def ttt_7_penalty_derivative(self, d):
        """Derivative of TTT-7 penalty. Since it is step-like, we use a smooth approximation for gradients."""
        # Smooth approximation of the modular stability manifold
        return -np.sin(2 * np.pi * d * 1618 / 9.0)

    def lennard_jones_potential_vectorized(self, d_scaled):
        """Standard Steric Clash Prevention (Lennard-Jones 12-6)."""
        eps = 1e-9
        inv_d6 = (d_scaled + eps)**-6
        return 4 * (inv_d6**2 - inv_d6)

    def lennard_jones_derivative(self, d_scaled):
        """Derivative of Lennard-Jones w.r.t. d_scaled."""
        eps = 1e-9
        # d/dx [4(x^-12 - x^-6)] = 4(-12x^-13 + 6x^-7)
        return 4 * (-12 * (d_scaled + eps)**-13 + 6 * (d_scaled + eps)**-7)

    def energy_and_gradient(self, coords_flat):
        """Combined objective and gradient function for performance."""
        coords = coords_flat.reshape(-1, 3)
        n = len(coords)
        grad = np.zeros_like(coords)
        total_e = 0.0
        
        # We'll use a slightly more explicit loop or broad-casting for gradients
        # to avoid the memory overhead of a full N^2 distance matrix if N is very large,
        # but for N=200, broadcasting is fine.
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        dists = np.sqrt(np.sum(diff**2, axis=-1) + 1e-9)
        
        # Upper triangle indices to avoid double counting and self-interaction
        iu = np.triu_indices(n, k=1)
        d = dists[iu]
        
        # 1. Lennard-Jones
        d_scaled = d / 3.8
        total_e += np.sum(self.lennard_jones_potential_vectorized(d_scaled))
        lj_grad_mag = self.lennard_jones_derivative(d_scaled) / 3.8
        
        # 2. QRT
        total_e += np.sum(self.qrt_damping_vectorized(d))
        qrt_grad_mag = self.qrt_damping_derivative(d)
        
        # 3. TTT-7
        total_e += np.sum(self.ttt_7_penalty_vectorized(d))
        ttt_grad_mag = self.ttt_7_penalty_derivative(d)
        
        # Combine magnitudes
        total_grad_mag = lj_grad_mag + qrt_grad_mag + ttt_grad_mag
        
        # Project magnitudes onto vectors: grad_i += (V'(d) * (ri - rj) / d)
        # Using the diff matrix we computed earlier
        grad_matrix = np.zeros((n, n, 3))
        # unit_vectors = diff / dists[:, :, np.newaxis]
        # But we only need the upper triangle
        mag_matrix = np.zeros((n, n))
        mag_matrix[iu] = total_grad_mag / d
        
        # Apply symmetry: grad_ij = -grad_ji
        mag_matrix = mag_matrix - mag_matrix.T
        
        # Final gradient for each particle: sum over j of (mag_ij * (ri - rj))
        grad = np.sum(mag_matrix[:, :, np.newaxis] * diff, axis=1)
        
        return total_e, grad.flatten()

    def optimize(self, max_iter=500):
        """Relaxes the 3D structure using L-BFGS-B with analytical gradients."""
        res = minimize(
            self.energy_and_gradient, 
            self.x0, 
            method='L-BFGS-B', 
            jac=True,
            options={'maxiter': max_iter, 'disp': False}
        )
        self.x0 = res.x # Save state for next resonance cycle
        return res.x.reshape(-1, 3)

if __name__ == "__main__":
    import time
    n_residues = 189
    ff = NRCForcefield(n_residues)
    start = time.time()
    final_coords = ff.optimize(max_iter=100)
    print(f"Optimized 189 AA in {time.time() - start:.2f}s")
    print(f"Optimized coordinates shape: {final_coords.shape}")

