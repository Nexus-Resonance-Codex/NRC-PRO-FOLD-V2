import numpy as np
from scipy.optimize import minimize
from nrc_chemistry import NRCChemistry

class NRCForcefield:
    def __init__(self, sequence):
        self.sequence = sequence
        self.N = len(sequence)
        self.phi = (1 + np.sqrt(5)) / 2
        
        # Load Chemistry Manifold
        chem = NRCChemistry()
        self.res_sigma, self.res_epsilon, self.res_charge = chem.get_params(sequence)

        # Physical constants
        self.CA_CA_BOND_LENGTH = 3.8
        self.K_BOND = 5000.0
        self.RG_TARGET = 3.0 * (self.N ** 0.33)  # Dynamic Rg scaling
        self.MODULAR_SCALE = 3.8

        self.x0 = self.spherical_fibonacci_initialization(self.N)

    def spherical_fibonacci_initialization(self, N):
        indices = np.arange(1, N + 1)
        z = 1 - (2 * indices - 1) / N
        theta = (2 * np.pi / (self.phi**2)) * indices
        x = np.sqrt(1 - z**2) * np.cos(theta)
        y = np.sqrt(1 - z**2) * np.sin(theta)
        return (np.column_stack((x, y, z)) * self.RG_TARGET).flatten()

    def energy_and_gradient(self, coords_flat):
        coords = coords_flat.reshape(-1, 3)
        n = self.N
        grad = np.zeros_like(coords)
        total_e = 0.0

        # 1. Harmonic Bonds
        diff_backbone = coords[1:] - coords[:-1]
        d_backbone = np.linalg.norm(diff_backbone, axis=1) + 1e-9
        bond_e = self.K_BOND * np.sum((d_backbone - self.CA_CA_BOND_LENGTH)**2)
        total_e += bond_e
        bond_mag = 2 * self.K_BOND * (d_backbone - self.CA_CA_BOND_LENGTH) / d_backbone
        grad[:-1] += -bond_mag[:, np.newaxis] * diff_backbone
        grad[1:] += bond_mag[:, np.newaxis] * diff_backbone

        # 2. Non-bonded Matrix
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        dists = np.sqrt(np.sum(diff**2, axis=-1) + 1e-9)
        iu = np.triu_indices(n, k=2)
        d = dists[iu]
        
        # Lorentz-Berthelot combining rules
        sigma_ij = (self.res_sigma[:, np.newaxis] + self.res_sigma[np.newaxis, :])[iu] / 1.0  # Normalized
        epsilon_ij = np.sqrt(self.res_epsilon[:, np.newaxis] * self.res_epsilon[np.newaxis, :])[iu]
        
        # 2a. Lennard-Jones
        s_r = (sigma_ij * 1.1) / d
        s_r6 = s_r**6
        s_r12 = s_r6**2
        lj_e = epsilon_ij * (s_r12 - s_r6)
        total_e += np.sum(lj_e)
        lj_grad_mag = epsilon_ij * (-12 * s_r12 / d + 6 * s_r6 / d)

        # 2b. TTT-7 Resonance
        ttt_factor = 1618.0 / (9.0 * self.MODULAR_SCALE)
        ttt_e = -np.cos(2 * np.pi * d * ttt_factor)
        total_e += np.sum(ttt_e)
        ttt_grad_mag = 2 * np.pi * ttt_factor * np.sin(2 * np.pi * d * ttt_factor)

        # 2c. Electrostatic Resonance (Coulomb + TTT-7 modulation)
        q_ij = (self.res_charge[:, np.newaxis] * self.res_charge[np.newaxis, :])[iu]
        elec_e = q_ij / (d + 1e-9) * np.exp(-d/10.0) # Screened Coulomb
        total_e += np.sum(elec_e)
        elec_grad_mag = -q_ij / (d**2 + 1e-9) * np.exp(-d/10.0) - (elec_e / 10.0)

        # 2d. QRT Damping
        qrt_e = (d / self.phi)**2 * 0.005
        total_e += np.sum(qrt_e)
        qrt_grad_mag = 2 * d / (self.phi**2) * 0.005

        # Sum non-bonded gradients
        total_mag = lj_grad_mag + ttt_grad_mag + elec_grad_mag + qrt_grad_mag
        mag_matrix = np.zeros((n, n))
        mag_matrix[iu] = total_mag / d
        mag_matrix += mag_matrix.T
        grad += np.sum(mag_matrix[:, :, np.newaxis] * diff, axis=1)

        # 3. Global Confinement
        mean_coords = np.mean(coords, axis=0)
        rel_coords = coords - mean_coords
        sum_sq_dist = np.sum(rel_coords**2)
        rg = np.sqrt(sum_sq_dist / n)
        conf_e = 5.0 * (rg - self.RG_TARGET)**2
        total_e += conf_e
        dE_drg = 10.0 * (rg - self.RG_TARGET)
        grad += (dE_drg / (rg * n + 1e-9)) * rel_coords

        return total_e, grad.flatten()

    def optimize(self, max_iter=1000):
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
    seq = "MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFKALVLIAFAQYLQQCPFEDHVKLVNEVTEFAKTCVADESAENCDKSLHTLFGDKLCTVATLRETYGEMADCCAKQEPERNECFLQHKDDNPNLPRLVRPEVDVMCTAFHDNEETFLKKYLYEIARRHPYFYAPELLFFAKRYKAAFTECCQAADKAACLLPKLDELRDEGKASSAKQRLKCASLQKFGERAFKAWAVARLSQRFPKAEFAEVSKLVTDLTKVHTECCHGDLLECADDRADLAKYICENQDSISSKLKECCEKPLLEKSHCIAEVENDEMPADLPSLAADFVESKDVCKNYAEAKDVFLGMFLYEYARRHPDYSVVLLLRLAKTYETTLEKCCAAADPHECYAKVFDEFKPLVEEPQNLIKQNCELFEQLGEYKFQNALLVRYTKKVPQVSTPTLVEVSRNLGKVGSKCCKHPEAKRMPCAEDYLSVVLNQLCVLHEKTPVSDRVTKCCTESLVNRRPCFSALEVDETYVPKEFNAETFTFHADICTLSEKERQIKKQTALVELVKHKPKATKEQLKAVMDDFAAFVEKCCKADDKETCFAEEGKKLVAASQAALGL"
    ff = NRCForcefield(seq)
    start = time.time()
    final_coords = ff.optimize(max_iter=500)
    print(f"Optimized {len(seq)} AA in {time.time() - start:.2f}s")
    rg = np.sqrt(np.mean(np.sum((final_coords - np.mean(final_coords, axis=0))**2, axis=1)))
    print(f"Final Radius of Gyration: {rg:.2f} Å")
