import datetime
import math


def calculate_lectures_in_period(start_date, end_date, weekly_slots):
    total = 0
    current = start_date
    while current <= end_date:
        total += weekly_slots.get(current.strftime("%A"), 0)
        current += datetime.timedelta(days=1)
    return total


def find_date_for_lectures(start_date, lectures_needed, weekly_slots):
    total = 0
    current = start_date
    while total < lectures_needed:
        total += weekly_slots.get(current.strftime("%A"), 0)
        if total >= lectures_needed:
            return current
        current += datetime.timedelta(days=1)
    return current


def main_web(attended, conducted, deadline, today, weekly_slots, skip_start=None, skip_end=None, skipped_lectures=0):
    results = {
        'current_attendance': (attended / conducted) * 100 if conducted > 0 else 0.0,
        'today': today,
        'deadline': deadline
    }

    # Future lectures calculation
    results['future_lectures_total'] = calculate_lectures_in_period(
        today + datetime.timedelta(days=1),
        deadline,
        weekly_slots
    )

    # Projection calculations
    future_attended = results['future_lectures_total'] - skipped_lectures
    results['projected_total_attended'] = attended + future_attended
    results['projected_total_conducted'] = conducted + results['future_lectures_total']
    results['projected_attendance_percentage'] = (
        (results['projected_total_attended'] / results['projected_total_conducted']) * 100
        if results['projected_total_conducted'] > 0 else 0.0
    )

    # Threshold analysis
    thresholds = []
    A = results['projected_total_attended']
    C = results['projected_total_conducted']
    lectures_per_week = sum(weekly_slots.values())

    for t in [50, 60, 70, 75]:
        denominator = (1 - t / 100)
        x = ((t / 100) * C - A) / denominator

        # Calculate requirements
        extra_needed = math.ceil(x) if x > 0 else None
        additional_skip = math.floor(-x) if x < 0 else None
        last_start_date = None

        # Red zone calculations
        if extra_needed:
            required = extra_needed
            current_date = deadline
            collected = 0
            while collected < required and current_date >= today:
                day_lectures = weekly_slots.get(current_date.strftime("%A"), 0)
                if day_lectures > 0:
                    collected += day_lectures
                current_date -= datetime.timedelta(days=1)
            last_start_date = current_date + datetime.timedelta(days=1)

        # Green zone calculations
        new_skip_end_date = None
        if additional_skip and additional_skip > 0:
            baseline = skip_end + datetime.timedelta(days=1) if skip_start else deadline + datetime.timedelta(days=1)
            new_skip_end_date = find_date_for_lectures(baseline, additional_skip, weekly_slots)

        thresholds.append({
            'target': t,
            'extra_needed': extra_needed,
            'additional_skip': additional_skip,
            'last_start_date': last_start_date,
            'new_skip_end_date': new_skip_end_date,
            'weeks_equivalent': additional_skip / lectures_per_week if additional_skip else None,
            'months_equivalent': (additional_skip / lectures_per_week) / 4.345 if additional_skip else None
        })

    results['thresholds'] = thresholds
    return results
