"""
======================================================================
DECISION INTELLIGENCE - NET PROFIT + SELL NOW VS WAIT VERIFICATION
======================================================================

Architecture-only verification.

Checks the existing Decision Intelligence Engine for:

    1. Net Profit
    2. Sell Now vs Wait
    3. Existing recommendation
    4. Existing financial calculations

No:
    - new ML model
    - model retraining
    - new dataset
    - new architecture component
    - AI agent
======================================================================
"""

from pathlib import Path
import sys
import traceback


# ======================================================================
# PROJECT PATH
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ======================================================================
# SAFE NUMERIC CONVERSION
# ======================================================================

def safe_float(value, default=None):

    try:

        if value is None:
            return default

        result = float(value)

        if result != result:
            return default

        return result

    except Exception:

        return default


# ======================================================================
# FIND VALUE RECURSIVELY
# ======================================================================

def find_value(data, possible_keys):

    if isinstance(data, dict):

        normalized = {
            str(key).lower().strip(): value
            for key, value in data.items()
        }

        for key in possible_keys:

            key_lower = key.lower().strip()

            if key_lower in normalized:

                return normalized[key_lower]

        for value in data.values():

            found = find_value(
                value,
                possible_keys
            )

            if found is not None:

                return found

    elif isinstance(data, (list, tuple)):

        for item in data:

            found = find_value(
                item,
                possible_keys
            )

            if found is not None:

                return found

    else:

        for key in possible_keys:

            if hasattr(data, key):

                value = getattr(
                    data,
                    key
                )

                if value is not None:

                    return value

    return None


# ======================================================================
# RESULT EXTRACTION
# ======================================================================

def extract_result(engine, result):

    sources = [
        result,
        getattr(
            engine,
            "last_result",
            None
        ),
        getattr(
            engine,
            "result",
            None
        ),
        getattr(
            engine,
            "decision",
            None
        ),
    ]

    return sources


# ======================================================================
# FINANCIAL VERIFICATION
# ======================================================================

def verify_net_profit(result_sources):

    print()
    print("=" * 70)
    print("NET PROFIT VERIFICATION")
    print("=" * 70)

    revenue = None
    cost = None
    profit = None

    for source in result_sources:

        if source is None:
            continue

        if revenue is None:

            revenue = find_value(
                source,
                [
                    "expected_revenue",
                    "revenue",
                    "total_revenue",
                ]
            )

        if cost is None:

            cost = find_value(
                source,
                [
                    "estimated_cost",
                    "total_cost",
                    "cost",
                    "expected_cost",
                ]
            )

        if profit is None:

            profit = find_value(
                source,
                [
                    "net_profit",
                    "profit",
                    "expected_profit",
                    "estimated_profit",
                ]
            )

    revenue = safe_float(revenue)
    cost = safe_float(cost)
    profit = safe_float(profit)

    print(
        f"Revenue : "
        f"{revenue if revenue is not None else 'NOT FOUND'}"
    )

    print(
        f"Cost    : "
        f"{cost if cost is not None else 'NOT FOUND'}"
    )

    print(
        f"Net Profit : "
        f"{profit if profit is not None else 'NOT FOUND'}"
    )

    if (
        revenue is None
        or cost is None
    ):

        print(
            "⚠ Revenue or Cost is not exposed "
            "by the existing result."
        )

        return False

    calculated_profit = (
        revenue - cost
    )

    print(
        f"Calculated Net Profit : "
        f"{calculated_profit:.2f}"
    )

    if profit is None:

        print(
            "⚠ Existing engine does not expose "
            "a dedicated net_profit field."
        )

        print(
            "The existing financial calculation "
            "is still mathematically available."
        )

        return False

    difference = abs(
        profit - calculated_profit
    )

    print(
        f"Profit calculation difference : "
        f"{difference:.6f}"
    )

    if difference > 0.01:

        print(
            "✗ Net Profit does not match "
            "Revenue - Cost."
        )

        return False

    print(
        "✓ Net Profit verified"
    )

    print(
        "✓ Net Profit = Revenue - Cost"
    )

    return True


# ======================================================================
# SELL NOW VS WAIT VERIFICATION
# ======================================================================

def verify_sell_now_vs_wait(
    result_sources
):

    print()
    print("=" * 70)
    print("SELL NOW VS WAIT VERIFICATION")
    print("=" * 70)

    recommendation = None

    for source in result_sources:

        if source is None:
            continue

        if recommendation is None:

            recommendation = find_value(
                source,
                [
                    "sell_now_vs_wait",
                    "sell_or_wait",
                    "sell_decision",
                    "timing_decision",
                    "market_timing",
                    "recommendation",
                    "final_recommendation",
                    "decision",
                ]
            )

    if recommendation is None:

        print(
            "⚠ Existing engine recommendation "
            "was not found in returned result."
        )

        return False

    recommendation_text = str(
        recommendation
    ).strip()

    print(
        f"Existing decision : "
        f"{recommendation_text}"
    )

    text = recommendation_text.upper()

    sell_keywords = [
        "SELL NOW",
        "SELL",
        "SELL WITH CAUTION",
    ]

    wait_keywords = [
        "WAIT",
        "HOLD",
        "WAIT FOR",
    ]

    has_sell = any(
        keyword in text
        for keyword in sell_keywords
    )

    has_wait = any(
        keyword in text
        for keyword in wait_keywords
    )

    if not has_sell and not has_wait:

        print(
            "⚠ Recommendation exists, but it "
            "does not explicitly represent "
            "Sell Now / Wait."
        )

        return False

    if has_sell:

        print(
            "✓ Sell decision is represented"
        )

    if has_wait:

        print(
            "✓ Wait decision is represented"
        )

    print(
        "✓ Existing decision engine provides "
        "market-timing guidance"
    )

    return True


# ======================================================================
# RUN EXISTING ENGINE
# ======================================================================

def run_existing_engine():

    print()
    print("=" * 70)
    print("LOADING EXISTING DECISION INTELLIGENCE ENGINE")
    print("=" * 70)

    try:

        from backend.app.decision.decision_engine import (
            DecisionIntelligenceEngine
        )

    except Exception as exc:

        print(
            "✗ Could not import "
            "DecisionIntelligenceEngine"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return None, None

    try:

        engine = DecisionIntelligenceEngine()

        print(
            "✓ Decision Intelligence Engine initialized"
        )

    except Exception as exc:

        print(
            "✗ Engine initialization failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return None, None

    # ------------------------------------------------------------------
    # IMPORTANT
    # ------------------------------------------------------------------
    # We do NOT invent a new execution API here.
    #
    # First try the existing test/execution methods.
    # If the engine exposes a standard method, use it.
    # Otherwise inspect the existing engine state.
    # ------------------------------------------------------------------

    result = None

    candidate_methods = [
        "process_decision",
        "make_decision",
        "generate_decision",
        "get_decision",
        "run",
    ]

    for method_name in candidate_methods:

        method = getattr(
            engine,
            method_name,
            None
        )

        if not callable(method):
            continue

        try:

            # Do not call methods that require
            # unknown mandatory arguments.
            #
            # Inspect signature first.

            import inspect

            signature = inspect.signature(
                method
            )

            required_parameters = [
                parameter
                for parameter in signature.parameters.values()
                if parameter.name != "self"
                and parameter.default
                is inspect.Parameter.empty
                and parameter.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]

            if required_parameters:

                continue

            result = method()

            print(
                f"✓ Existing method executed: "
                f"{method_name}()"
            )

            break

        except TypeError:

            continue

        except Exception as exc:

            print(
                f"⚠ Existing method "
                f"{method_name}() could not execute:"
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

    return engine, result


# ======================================================================
# MAIN
# ======================================================================

def main():

    print()
    print("=" * 70)
    print("DECISION INTELLIGENCE FINANCIAL COMPLETION CHECK")
    print("=" * 70)

    print(
        "Existing architecture only."
    )

    print(
        "Existing Decision Intelligence Engine only."
    )

    print(
        "No new ML models."
    )

    print(
        "No new datasets."
    )

    print(
        "No AI Agent."
    )

    print(
        "No architecture changes."
    )

    engine, result = run_existing_engine()

    if engine is None:

        print()
        print(
            "⚠ VERIFICATION STOPPED"
        )

        return

    sources = extract_result(
        engine,
        result
    )

    # ==================================================================
    # NET PROFIT
    # ==================================================================

    net_profit_complete = (
        verify_net_profit(
            sources
        )
    )

    # ==================================================================
    # SELL NOW VS WAIT
    # ==================================================================

    sell_wait_complete = (
        verify_sell_now_vs_wait(
            sources
        )
    )

    # ==================================================================
    # FINAL STATUS
    # ==================================================================

    print()
    print("=" * 70)
    print("DECISION INTELLIGENCE FINANCIAL STATUS")
    print("=" * 70)

    print(
        "Net Profit       : "
        +
        (
            "✓ COMPLETED"
            if net_profit_complete
            else "⚠ NEEDS COMPLETION"
        )
    )

    print(
        "Sell Now vs Wait : "
        +
        (
            "✓ COMPLETED"
            if sell_wait_complete
            else "⚠ NEEDS COMPLETION"
        )
    )

    print()

    if (
        net_profit_complete
        and sell_wait_complete
    ):

        print(
            "✓ NET PROFIT COMPLETED"
        )

        print(
            "✓ SELL NOW VS WAIT COMPLETED"
        )

        print(
            "✓ Decision Intelligence financial "
            "block verified"
        )

        print()
        print(
            "Next existing architecture component: "
            "MATCHING"
        )

    else:

        print(
            "⚠ THESE DECISION INTELLIGENCE "
            "ITEMS ARE NOT FULLY VERIFIED"
        )

        print(
            "Do not add a new architecture component."
        )

        print(
            "Fix only the existing "
            "Decision Intelligence Engine."
        )

    print("=" * 70)


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print(
            "⚠ Verification interrupted."
        )

        sys.exit(1)

    except Exception as exc:

        print()
        print("=" * 70)
        print("FATAL ERROR")
        print("=" * 70)

        print(
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        sys.exit(1)