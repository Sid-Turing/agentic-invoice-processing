from app.config import get_settings
from app.db import repository
from app.db.seed import seed_reference_data


def test_seed_loads_reference_data_and_is_idempotent(db_session):
    data_dir = get_settings().data_dir
    counts = seed_reference_data(db_session, data_dir)
    db_session.commit()
    assert counts["vendors"] == 2
    assert counts["purchase_orders"] == 2
    assert counts["line_items"] == 15

    # Second call is a no-op (skip-if-exists).
    assert seed_reference_data(db_session, data_dir) == {}

    po = repository.get_purchase_order_by_number(db_session, "PO-54872")
    assert po is not None and po.vendor.name == "MedEquip Diagnostics LLC"
