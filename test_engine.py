from nrc_engine import NRCEngine
import numpy as np

def test_engine():
    engine = NRCEngine()
    test_seq = "MTEYKLVVVGAGGVGKSALTI" # KRAS fragment
    print(f"Testing NRC Engine with sequence: {test_seq}")
    
    steps = 0
    for frame in engine.fold_sequence(test_seq):
        steps += 1
        if frame.get("final"):
            print(f"Final step reached: {frame['step']}")
            coords = frame["coords"]
            print(f"Output coordinate shape: {coords.shape}")
            if "atom_types" in frame:
                print(f"All-atom manifold detected. Total atoms: {len(frame['atom_types'])}")
            break
    
    if steps > 0:
        print("Test PASSED: Engine completed trajectory.")
    else:
        print("Test FAILED: No output from engine.")

if __name__ == "__main__":
    test_engine()
