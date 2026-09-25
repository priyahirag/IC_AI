def calculate_priority(severity, exposure, vulnerability, urgency):
    score = (
        0.35 * severity +
        0.30 * exposure +
        0.20 * vulnerability +
        0.15 * urgency
    )

    return round(score, 2)


def get_priority_level(score):
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


# Test
if __name__ == "__main__":
    score = calculate_priority(90, 85, 80, 95)

    print("Priority Score:", score)
    print("Priority Level:", get_priority_level(score))