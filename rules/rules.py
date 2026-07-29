def apply_rules(requirements):
    messages = []

    # SAFE ACCESS (no KeyError ever)
    floors = requirements.get("floors", "Single Storey")
    plot_size = requirements.get("plot_size", 0)
    bedrooms = requirements.get("bedrooms", 0)
    budget = requirements.get("budget", "medium")

    # Rule 1
    if floors == "Double Storey" and plot_size < 5:
        messages.append("❌ Double storey requires at least 5 marla plot.")

    # Rule 2
    if bedrooms > 6 and plot_size < 7:
        messages.append("⚠ Too many bedrooms for given plot size.")

    # Rule 3
    if budget == "low" and floors == "Double Storey":
        messages.append("⚠ Low budget may not support double storey.")

    return messages