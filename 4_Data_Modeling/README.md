# 📁 Data Modeling README

This folder contains all logic and validation work related to the development of our **Nearest Neighbors model** for identifying similar Texas school districts based on demographic data.

---

## 📂 4.1 Nearest Neighbor Model

This subfolder contains the **finalized logic and code** for computing nearest neighbors.

- **Key Script**: `KNN_Model.py`  
  - Contains the `find_nearest_districts` function, which serves as the core method for generating neighbor lists.
- **Support Files**: 6 additional `.py` files assist with utility functions, preprocessing, and diagnostics.
- **Reference**: For a high-level walkthrough of the implementation, refer to the companion document:  
  📄 *1. Nearest Neighbors Implementation*

---

## 📂 4.2 Nearest Neighbor Model Validation

This subfolder provides documentation and code used to **validate and select the optimal Nearest Neighbors distance metric**. It is divided into three subdirectories:

### 🗂️ 1. Nearest Neighbors Model (Initial Version)

- Contains an **earlier version** of the model prior to finalization in `4.1`.
- Contains the scripts used to produce the quantiative and qualitative validation results

### 🗂️ 2. Qualitative Model Validation

- Includes code and outputs used to generate **diagnostic plots** of different distance metrics.
- These plots were shared with **local school district officials** for blind evaluation of neighbor similarity.
- Helped us assess which distance metric most closely aligned with expert judgment.

### 🗂️ 3. Quantitative Model Validation

- Focused on **empirical evaluation** of different distance metrics and model configurations.
- We conducted simulations across various input parameters, then computed the **average standardized variance** across neighbor groups to identify the most consistent metric.
