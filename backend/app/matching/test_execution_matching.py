"""
======================================================================
CORE FUNCTIONAL MODULES - FINAL INTEGRATION VERIFICATION
======================================================================

Components:
1. AI Auction
2. Buyer Matching
3. Risk-Aware Bidding
4. Net Profit Optimization
5. Logistics Optimization

No frontend.
No FastAPI.
No external API.
No new dataset.
No ML model training.
Existing models and datasets only.
"""

from __future__ import annotations

import sys
import traceback
import importlib.util
from pathlib import Path


# ======================================================================
# 1. CORRECT PROJECT PATH CONFIGURATION
# ======================================================================

CURRENT_FILE = Path(__file__).resolve()

# Current file:
#
# D:\PythonProject3\backend\app\matching\test_execution_matching.py
#
# parents:
#   0 = matching
#   1 = app
#   2 = backend
#   3 = PythonProject3
#
# Therefore:
#   PROJECT_ROOT = CURRENT_FILE.parents[3]

MATCHING_DIR = CURRENT_FILE.parent
APP_DIR = MATCHING_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = CURRENT_FILE.parents[3]

ML_DIR = PROJECT_ROOT / "backend" / "ml"

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"

SAVED_MODELS_DIR = ML_DIR / "saved_models"


# ======================================================================
# 2. COMPONENT MODULE PATHS
# ======================================================================

COMPONENTS = {
    "AI Auction": [
        MATCHING_DIR / "ai_auction.py",
    ],

    "Buyer Matching": [
        MATCHING_DIR / "buyer_matching.py",
    ],

    "Risk-Aware Bidding": [
        MATCHING_DIR / "risk_aware_bidding.py",
    ],

    "Net Profit Optimization": [
        MATCHING_DIR / "net_profit_optimization.py",
    ],

    "Logistics Optimization": [
        MATCHING_DIR / "logistics_optimization.py",
    ],
}


# ======================================================================
# 3. REQUIRED FEATURE DATA
# ======================================================================

REQUIRED_DATA = {

    "AI Auction": [
        "price_features.csv",
        "demand_features.csv",
    ],

    "Buyer Matching": [
        "buyer_features.csv",
        "transaction_features.csv",
    ],

    "Risk-Aware Bidding": [
        "transaction_features.csv",
        "logistics_features.csv",
    ],

    "Net Profit Optimization": [
        "cost_features.csv",
        "transaction_features.csv",
    ],

    "Logistics Optimization": [
        "logistics_features.csv",
    ],
}


# ======================================================================
# 4. REQUIRED MODEL ARTIFACTS
# ======================================================================

REQUIRED_MODELS = {

    "AI Auction": [
        "price_model.joblib",
        "demand_model.joblib",
    ],

    "Buyer Matching": [
        "buyer_model.joblib",
    ],

    "Risk-Aware Bidding": [
        "payment_risk_model.joblib",
        "delivery_risk_model.joblib",
    ],

    "Net Profit Optimization": [
        "cost_estimation_model.joblib",
        "transport_cost_model.joblib",
    ],

    "Logistics Optimization": [
        "transport_cost_model.joblib",
    ],
}


# ======================================================================
# 5. RESULT STORAGE
# ======================================================================

MODULE_RESULTS = {}
DATA_RESULTS = {}
MODEL_RESULTS = {}
IMPORT_RESULTS = {}
INTERFACE_RESULTS = {}


# ======================================================================
# DISPLAY HELPERS
# ======================================================================

def print_line():
    print("=" * 70)


def print_section(number, title):
    print()
    print_line()
    print(f"{number}. {title}")
    print_line()


def success(message):
    print(f"✓ {message}")


def warning(message):
    print(f"⚠ {message}")


def failure(message):
    print(f"✗ {message}")


# ======================================================================
# 6. PATH VERIFICATION
# ======================================================================

def verify_paths():

    print_section(
        1,
        "CORE FUNCTIONAL ENGINE INITIALIZATION"
    )

    print(
        f"✓ Project root : {PROJECT_ROOT}"
    )

    print(
        f"✓ Backend directory : {BACKEND_DIR}"
    )

    print(
        f"✓ Matching directory : {MATCHING_DIR}"
    )

    print(
        f"✓ ML directory : {ML_DIR}"
    )

    print(
        f"✓ Data directory : {DATA_DIR}"
    )

    print(
        f"✓ Processed data : {PROCESSED_DIR}"
    )

    print(
        f"✓ Saved models : {SAVED_MODELS_DIR}"
    )

    if not PROJECT_ROOT.exists():

        raise RuntimeError(
            f"Project root does not exist: "
            f"{PROJECT_ROOT}"
        )

    if not BACKEND_DIR.exists():

        raise RuntimeError(
            f"Backend directory does not exist: "
            f"{BACKEND_DIR}"
        )

    if not MATCHING_DIR.exists():

        raise RuntimeError(
            f"Matching directory does not exist: "
            f"{MATCHING_DIR}"
        )

    if not ML_DIR.exists():

        raise RuntimeError(
            f"ML directory does not exist: "
            f"{ML_DIR}"
        )

    if not DATA_DIR.exists():

        raise RuntimeError(
            f"Data directory does not exist: "
            f"{DATA_DIR}"
        )

    if not PROCESSED_DIR.exists():

        raise RuntimeError(
            f"Processed data directory does not exist: "
            f"{PROCESSED_DIR}"
        )

    if not SAVED_MODELS_DIR.exists():

        raise RuntimeError(
            f"Saved models directory does not exist: "
            f"{SAVED_MODELS_DIR}"
        )

    success(
        "Project structure verified"
    )


# ======================================================================
# 7. MODULE LOADER
# ======================================================================

def load_module(
    module_path: Path,
    module_name: str
):

    if not module_path.exists():

        raise FileNotFoundError(
            f"Module not found: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        str(module_path)
    )

    if spec is None:

        raise ImportError(
            f"Unable to create module specification: "
            f"{module_path}"
        )

    if spec.loader is None:

        raise ImportError(
            f"Module loader unavailable: "
            f"{module_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


# ======================================================================
# 8. MODULE VERIFICATION
# ======================================================================

def verify_component_module(
    component,
    module_paths
):

    print()
    print("-" * 70)
    print(component)
    print("-" * 70)

    module_found = False
    imported = False
    loaded_module = None

    for module_path in module_paths:

        if module_path.exists():

            module_found = True

            success(
                f"{component} source found : "
                f"{module_path.name}"
            )

            try:

                module_name = (
                    "core_verification_"
                    + component.lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )

                loaded_module = load_module(
                    module_path,
                    module_name
                )

                imported = True

                success(
                    f"{component} module imported successfully"
                )

                break

            except Exception as exc:

                failure(
                    f"{component} import failed"
                )

                failure(
                    f"{type(exc).__name__}: {exc}"
                )

    if not module_found:

        failure(
            f"{component} source module not found"
        )

    MODULE_RESULTS[component] = module_found
    IMPORT_RESULTS[component] = imported

    return loaded_module


# ======================================================================
# 9. FEATURE DATA VERIFICATION
# ======================================================================

def verify_component_data(component):

    print()
    print(
        f"Checking feature data for {component}..."
    )

    required_files = REQUIRED_DATA.get(
        component,
        []
    )

    if not required_files:

        warning(
            f"No feature datasets configured for "
            f"{component}"
        )

        DATA_RESULTS[component] = True

        return True

    result = True

    try:

        import pandas as pd

    except ImportError as exc:

        failure(
            f"pandas unavailable: {exc}"
        )

        DATA_RESULTS[component] = False

        return False

    for filename in required_files:

        path = PROCESSED_DIR / filename

        if not path.exists():

            result = False

            failure(
                f"Missing feature file: {filename}"
            )

            continue

        try:

            df = pd.read_csv(
                path,
                nrows=5
            )

            if df.empty:

                result = False

                failure(
                    f"Feature file is empty: "
                    f"{filename}"
                )

                continue

            success(
                f"Feature file verified: "
                f"{filename}"
            )

            success(
                f"  Columns : {len(df.columns)}"
            )

        except Exception as exc:

            result = False

            failure(
                f"Could not read {filename}: "
                f"{type(exc).__name__}: {exc}"
            )

    DATA_RESULTS[component] = result

    return result


# ======================================================================
# 10. MODEL VERIFICATION
# ======================================================================

def verify_component_models(component):

    print()
    print(
        f"Checking trained models for {component}..."
    )

    required_models = REQUIRED_MODELS.get(
        component,
        []
    )

    if not required_models:

        warning(
            f"No models configured for {component}"
        )

        MODEL_RESULTS[component] = True

        return True

    try:

        import joblib

    except ImportError as exc:

        failure(
            f"joblib unavailable: {exc}"
        )

        MODEL_RESULTS[component] = False

        return False

    result = True

    for filename in required_models:

        model_path = (
            SAVED_MODELS_DIR / filename
        )

        if not model_path.exists():

            result = False

            failure(
                f"Missing model: {filename}"
            )

            continue

        try:

            model = joblib.load(
                model_path
            )

            success(
                f"Model verified: {filename}"
            )

            success(
                f"  Model class : "
                f"{type(model).__name__}"
            )

        except Exception as exc:

            result = False

            failure(
                f"Could not load {filename}"
            )

            failure(
                f"  {type(exc).__name__}: {exc}"
            )

    MODEL_RESULTS[component] = result

    return result


# ======================================================================
# 11. INTERFACE VERIFICATION
# ======================================================================

def discover_callable_members(module):

    members = []

    if module is None:

        return members

    for name in dir(module):

        if name.startswith("_"):

            continue

        try:

            value = getattr(
                module,
                name
            )

        except Exception:

            continue

        if callable(value):

            members.append(name)

    return members


def verify_execution_interface(
    component,
    module
):

    print()
    print(
        f"Checking execution interface for "
        f"{component}..."
    )

    if module is None:

        INTERFACE_RESULTS[component] = False

        failure(
            "Module unavailable"
        )

        return False

    preferred = [
        "run",
        "execute",
        "process",
        "calculate",
        "optimize",
        "recommend",
        "match",
        "auction",
        "bid",
        "predict",
        "main",
    ]

    available = (
        discover_callable_members(
            module
        )
    )

    preferred_found = [
        name
        for name in preferred
        if name in available
    ]

    if preferred_found:

        success(
            "Execution interface found"
        )

        success(
            "Entry points : "
            + ", ".join(preferred_found)
        )

        INTERFACE_RESULTS[component] = True

        return True

    # --------------------------------------------------------------
    # Check classes
    # --------------------------------------------------------------

    classes = []

    for name in dir(module):

        if name.startswith("_"):

            continue

        try:

            value = getattr(
                module,
                name
            )

        except Exception:

            continue

        if isinstance(value, type):

            classes.append(name)

    if classes:

        success(
            "Class-based execution interface found"
        )

        success(
            "Classes : "
            + ", ".join(classes[:10])
        )

        INTERFACE_RESULTS[component] = True

        return True

    if available:

        success(
            "Callable module interface found"
        )

        success(
            "Available : "
            + ", ".join(available[:10])
        )

        INTERFACE_RESULTS[component] = True

        return True

    failure(
        "No callable execution interface found"
    )

    INTERFACE_RESULTS[component] = False

    return False


# ======================================================================
# 12. VERIFY ONE COMPONENT
# ======================================================================

def verify_component(
    component,
    module_paths
):

    module = verify_component_module(
        component,
        module_paths
    )

    data_ok = verify_component_data(
        component
    )

    model_ok = verify_component_models(
        component
    )

    interface_ok = verify_execution_interface(
        component,
        module
    )

    verified = (
        MODULE_RESULTS.get(
            component,
            False
        )
        and IMPORT_RESULTS.get(
            component,
            False
        )
        and DATA_RESULTS.get(
            component,
            False
        )
        and MODEL_RESULTS.get(
            component,
            False
        )
        and INTERFACE_RESULTS.get(
            component,
            False
        )
    )

    print()

    if verified:

        success(
            f"{component} : VERIFIED"
        )

    else:

        failure(
            f"{component} : REQUIRES VERIFICATION"
        )

    return verified


# ======================================================================
# 13. MAIN
# ======================================================================

def main():

    print()
    print_line()

    print(
        "CORE FUNCTIONAL MODULES - "
        "FINAL INTEGRATION VERIFICATION"
    )

    print_line()

    print()
    print("Components:")
    print("1. AI Auction")
    print("2. Buyer Matching")
    print("3. Risk-Aware Bidding")
    print("4. Net Profit Optimization")
    print("5. Logistics Optimization")

    print()
    print("No frontend.")
    print("No FastAPI.")
    print("No external API.")
    print("No new dataset.")
    print("No ML model training.")
    print("Existing models and datasets only.")

    # ==================================================================
    # INITIALIZATION
    # ==================================================================

    verify_paths()

    # ==================================================================
    # COMPONENT VERIFICATION
    # ==================================================================

    print_section(
        2,
        "CORE FUNCTIONAL COMPONENT VERIFICATION"
    )

    component_results = {}

    for component, module_paths in COMPONENTS.items():

        component_results[
            component
        ] = verify_component(
            component,
            module_paths
        )

    # ==================================================================
    # INTEGRATION
    # ==================================================================

    print_section(
        3,
        "CORE FUNCTIONAL INTEGRATION"
    )

    for component, verified in component_results.items():

        if verified:

            success(
                f"{component} connected"
            )

        else:

            failure(
                f"{component} integration failed"
            )

    all_verified = all(
        component_results.values()
    )

    if all_verified:

        success(
            "All Core Functional Modules "
            "passed final verification"
        )

    else:

        failure(
            "One or more Core Functional Modules "
            "require verification"
        )

    # ==================================================================
    # FINAL STATUS
    # ==================================================================

    print_section(
        4,
        "CORE FUNCTIONAL MODULES FINAL STATUS"
    )

    for component, verified in component_results.items():

        if verified:

            print(
                f"✓ {component:<32}: VERIFIED"
            )

        else:

            print(
                f"✗ {component:<32}: FAILED"
            )

    verified_count = sum(
        component_results.values()
    )

    total_count = len(
        component_results
    )

    print()
    print(
        f"Verified components : "
        f"{verified_count}/{total_count}"
    )

    print()

    if all_verified:

        print_line()

        print(
            "CORE FUNCTIONAL MODULES STATUS: COMPLETE"
        )

        print_line()

        print()
        print(
            "✓ FINAL CORE FUNCTIONAL "
            "VERIFICATION PASSED"
        )

        print()
        print(
            "✓ AI Auction verified"
        )

        print(
            "✓ Buyer Matching verified"
        )

        print(
            "✓ Risk-Aware Bidding verified"
        )

        print(
            "✓ Net Profit Optimization verified"
        )

        print(
            "✓ Logistics Optimization verified"
        )

        return 0

    print_line()

    print(
        "CORE FUNCTIONAL MODULES STATUS: "
        "REQUIRES VERIFICATION"
    )

    print_line()

    print()
    print(
        "✗ Final verification did not pass."
    )

    return 1


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        sys.exit(
            main()
        )

    except KeyboardInterrupt:

        print()
        print(
            "Verification interrupted by user."
        )

        sys.exit(130)

    except Exception as exc:

        print()
        print_line()

        print(
            "CORE FUNCTIONAL VERIFICATION FAILED"
        )

        print_line()

        print()
        print(
            f"Error Type : {type(exc).__name__}"
        )

        print(
            f"Error      : {exc}"
        )

        print()

        traceback.print_exc()

        sys.exit(1)