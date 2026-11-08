"""Public visibility is independent from administrative access to evidence."""


def is_visible(store, collection, document):
    if not document or document.get("banned"):
        return False
    if collection == "users" and document.get("account_type") == "sponsor":
        sponsor = store.get("sponsors", document.get("sponsor_id", ""))
        return bool(sponsor) and sponsor.get("owner_id") == document["id"] and not sponsor.get("banned")
    if collection in ("teams", "sponsors", "tournaments"):
        owner = store.get("users", document["owner_id"])
        return is_visible(store, "users", owner)
    return True
