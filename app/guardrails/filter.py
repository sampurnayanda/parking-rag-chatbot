def guardrail_check(query: str):

    query_lower = query.lower()

    # ── Sensitive data access ─────────────────────────
    sensitive = [
        "password", "private", "user data", "database",
        "all bookings", "all reservations", "all users",
        "other user", "other people", "someone else",
        "share user", "share name", "share details",
        "give me user", "show me user", "list users",
        "list all", "dump", "export data", "personal data",
        "confidential", "secret", "credentials",
        "api key", "token", "access key",
    ]

    # ── Prompt injection / jailbreak ──────────────────
    injection = [
        "ignore previous", "ignore instructions",
        "forget instructions", "disregard",
        "you are now", "act as", "pretend to be",
        "jailbreak", "bypass", "override",
        "system prompt", "new instruction",
        "do anything now", "dan mode",
        "ignore all rules", "ignore your rules",
        "ignore constraints", "ignore guidelines",
    ]

    # ── Unsafe / harmful ─────────────────────────────
    harmful = [
        "hack", "exploit", "attack", "inject",
        "sql injection", "xss", "malware", "virus",
        "illegal", "steal", "fraud", "scam",
        "bomb", "weapon", "kill", "harm",
    ]

    # ── Irrelevant / off-topic ────────────────────────
    off_topic = [
        "write code", "write a program", "write an essay",
        "tell me a joke", "play a game",
        "what is the weather", "stock price",
        "who is the president", "recipe",
        "translate", "write poem",
    ]

    for word in sensitive:
        if word in query_lower:
            return (
                "🔒 Access to sensitive or personal data is restricted. "
                "Please use your Reservation ID in the Reservation Status tab "
                "to view your own booking details."
            )

    for word in injection:
        if word in query_lower:
            return (
                "⚠️ That request cannot be processed. "
                "I can only help with parking questions and reservations."
            )

    for word in harmful:
        if word in query_lower:
            return (
                "🚫 That request is not allowed. "
                "I can only assist with parking-related queries."
            )

    for word in off_topic:
        if word in query_lower:
            return (
                "ℹ️ I'm a parking assistant and can only help with "
                "parking questions, bookings, and reservations."
            )

    return None