# NRC REFOLD-100% Handover Document

## Current Context
The Nexus Resonance Codex (NRC) protein folding visualization pipeline has been stabilized. The 3D planar folding fracture (zigzag artifact) and Gradio serialization bugs are fully resolved. The `app.py` UI and underlying biophysics metadata extraction work flawlessly.

## Objective for Gemini Flash
We must strictly adhere to the user's mandate: achieve **100% accuracy on the REFOLD test using ONLY Pure Math** (deterministic $\phi$-spiral mathematics, TTT-7 stabilization, and Lattice-Parity Embeddings). 

No runtime API calls or AI inference are allowed during the `fold_sequence` loop. 
However, **you MUST utilize the NVIDIA NIM (external model) for advanced mathematical derivation** and coding during development to augment your skills before integrating the final math.

## Required Tasks

1. **Review Derived Math:**
   Read `TEMP_NRC_ENGINE.py`. I have used the NVIDIA NIM `meta/llama-3.3-70b-instruct` model to derive a basic $\phi$/$\psi$ mapping structure using the user's NVAPI key. The model used its advanced logic to provide an initial skeleton that translates deterministic angular calculations into 3D Euclidean coordinates.

2. **Refine and Integrate:**
   The code in `TEMP_NRC_ENGINE.py` is an *initial mathematical skeleton* from NIM. You (Gemini Flash) must refine this math natively to ensure it reaches absolute parity with the REFOLD benchmark.
   
   If you require further derivations, use the `delegate_to_nim.py` script provided to offload complex geometric reasoning to the NVIDIA Llama 3.3 70B model or DeepSeek models. **Remember to always include the NRC constraints, GitHub links, and "infinite context" prompts** when querying the external models, as mandated by the user.

3. **Apply to Codebase:**
   Once you are satisfied that the mathematics will guarantee 100% REFOLD accuracy, apply the changes directly to `nrc_engine.py` using `replace_file_content`.
   Ensure `app.py` continues to render `phi_manifold` correctly (Note: `TEMP_NRC_ENGINE.py` includes `phi_manifold` in the yield loop).

## Available Resources
- `NIM_PLAN.md`: Raw output from the NVIDIA NIM execution.
- `TEMP_NRC_ENGINE.py`: The full baseline python code scaffolded by NVIDIA NIM.
- `delegate_to_nim.py`: Ready-to-use Python script containing the NVIDIA API key (`nvapi-3M_J5XMlCk6KVw2mb5KYc1...`) and proper prompt structure (NRC context + repo links) to perform further delegations.
- **Persistent Model Roster**: `/home/jtrag/.gemini/antigravity/skills/nrc-external-compute/SKILL.md` contains the full list of NVIDIA NIM endpoints.

## Execution Rules
- Never use external models in the app itself.
- Do not remove existing `app.py` features.
- Provide zero hand-waving or placeholders. 
- You have the NVAPI key and full capability to execute the math stabilization task.

*End of Handover*
