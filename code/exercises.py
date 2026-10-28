"""Shared exercise configuration.

Each exercise maps to a pair of CSV files used by the k-NN classifier:

    fitness_poses_csvs_out/<csv_prefix>_up.csv
    fitness_poses_csvs_out/<csv_prefix>_down.csv

``class_name`` is the pose class that increments the repetition counter.
"""

EXERCISES = {
    1: {
        'name': 'pushup',
        'label': '俯卧撑',
        'class_name': 'push_down',
        'csv_prefix': 'push',
        'output_prefix': 'pushup',
    },
    2: {
        'name': 'squat',
        'label': '深蹲',
        'class_name': 'squat_down',
        'csv_prefix': 'squat',
        'output_prefix': 'squat',
    },
    3: {
        'name': 'pullup',
        'label': '引体向上',
        'class_name': 'pull_up',
        'csv_prefix': 'pull',
        'output_prefix': 'pullup',
    },
}

# CLI aliases. Keep push_up/pull_up because they match the CSV class names.
ALIASES = {
    'pushup': 1,
    'push-up': 1,
    'push_up': 1,
    'push': 1,
    'squat': 2,
    'squat_down': 2,
    'pullup': 3,
    'pull-up': 3,
    'pull_up': 3,
    'pull': 3,
}


def get_exercise(flag):
    """Return the exercise config for a numeric flag (1/2/3)."""
    try:
        return EXERCISES[int(flag)]
    except (KeyError, TypeError, ValueError):
        valid = ', '.join(f"{key}={value['name']}" for key, value in EXERCISES.items())
        raise ValueError(f"未知运动类型: {flag!r}，可选: {valid}") from None


def flag_from_name(name):
    """Return the numeric flag for a CLI exercise name."""
    key = str(name).strip().lower()
    if key not in ALIASES:
        valid = ', '.join(sorted(ALIASES))
        raise ValueError(f"未知运动类型: {name!r}，可选: {valid}")
    return ALIASES[key]


def exercise_names():
    """Exercise names accepted by ``--exercise`` (canonical spelling first)."""
    return [EXERCISES[key]['name'] for key in sorted(EXERCISES)]
