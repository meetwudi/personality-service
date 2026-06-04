import os


def answer_cap() -> int:
    raw_cap = os.getenv("HYDRATION_ANSWER_CAP", "100")
    try:
        cap = int(raw_cap)
    except ValueError:
        return 100
    return max(1, cap)
