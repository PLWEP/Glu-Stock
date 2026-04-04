# GLU-STOCK: PROJECT CHECKPOINT (v17.1)

## System Overview
Glu-Stock is now a **Kaggle-First Hybrid Cloud** quantitative trading framework. It utilizes modular Jupyter Notebooks for execution, Kaggle Datasets for free model storage, and Firebase Realtime Database as the persistent state "bridge" between independent cloud kernels.

## 🚀 Key Features (Cloud Native)
- **Modular Micro-Services**: Research, Inference, Execution, and Monitoring separated into independent notebooks to bypass 12h limits and improve resilience.
- **Automated Lifecycle**: Weekly auto-retraining pipeline (`00_model_retraining.ipynb`) that feeds the latest intelligence to the inference engine.
- **Firebase Task Queue**: Cloud-native orchestration that allows asynchronous communication between notebooks (Research -> Inference -> Trade).
- **Free Institutional Scaling**: 100% free cloud compute and model storage using Kaggle's native infrastructure.

## 📁 Repository Structure (Kaggle Ready)
- `notebooks/`: Modular core logic for Kaggle production runs.
- `utils/`: Cloud-aware handlers, including `kaggle_bridge.py` for secret management and updated `FirebaseHandler` for task queues.
- `agents/`: Core strategy and trading logic, decoupled from platform constraints.
- `data/`: Ephemeral cache in cloud, persistent state in Firebase.

## 🏗️ Technical State
1. **Cloud Environment**: Kaggle Kernels (Ubuntu/Python 3.10+).
2. **State Bridge**: Firebase Realtime DB (Task Queues enabled).
3. **Model Storage**: Kaggle Datasets / Notebook Outputs.
4. **Execution Window**: 12-hour scheduled rotations.

---
*Migration Date*: 2026-04-04
*Status*: Active Production | Kaggle Hybrid Cloud
 Riverside
 Riverside
 Riverside
 Riverside
