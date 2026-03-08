# This is a test feature with over 100 lines of code


def calculate_stats(data):
    """Calculate various statistics from data."""
    results = {}

    # Calculate sum
    total = 0
    for item in data:
        total += item
    results["sum"] = total

    # Calculate average
    results["average"] = total / len(data) if data else 0

    # Calculate min
    results["min"] = min(data) if data else None

    # Calculate max
    results["max"] = max(data) if data else None

    # Calculate median
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        results["median"] = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        results["median"] = sorted_data[n // 2]

    # Calculate standard deviation
    mean = results["average"]
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    results["std_dev"] = variance**0.5

    return results


def process_user_data(users):
    """Process user data and return formatted results."""
    processed = []

    for user in users:
        user_record = {
            "id": user.get("id"),
            "name": user.get("name", "Unknown"),
            "email": user.get("email", ""),
            "active": user.get("active", False),
            "created_at": user.get("created_at", ""),
            "last_login": user.get("last_login", ""),
        }

        # Add derived fields
        if user.get("email"):
            user_record["domain"] = user["email"].split("@")[1] if "@" in user["email"] else ""

        processed.append(user_record)

    return processed


def generate_report(data, title="Report"):
    """Generate a formatted report from data."""
    report = []
    report.append("=" * 50)
    report.append(f" {title}")
    report.append("=" * 50)
    report.append("")

    # Add summary section
    report.append("SUMMARY")
    report.append("-" * 50)
    stats = calculate_stats(data)
    for key, value in stats.items():
        report.append(f"  {key}: {value}")

    report.append("")
    report.append("=" * 50)

    return "\n".join(report)
