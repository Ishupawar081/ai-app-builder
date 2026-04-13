def select_template(plan):
    text = str(plan).lower()

    # 🔥 PRIORITY ORDER (VERY IMPORTANT)

    if "dashboard" in text:
        return "dashboard_app"

    if "calculator" in text:
        return "calculator_app"

    if "note" in text or "notion" in text:
        return "form_app"

    if "todo" in text or "task" in text:
        return "list_app"

    return "list_app"