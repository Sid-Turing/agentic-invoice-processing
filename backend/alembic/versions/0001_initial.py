"""initial schema: PO reference tables + processed_invoices

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-07
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "po_vendors",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String()),
        sa.Column("tax_id", sa.String()),
        sa.Column("state", sa.String()),
        sa.Column("street_address", sa.String()),
        sa.Column("city", sa.String()),
        sa.Column("zip_code", sa.String()),
        sa.Column("bank_name", sa.String()),
        sa.Column("account_number", sa.String()),
        sa.Column("routing_number", sa.String()),
        sa.Column("swift_code", sa.String()),
        sa.Column("tax_classification", sa.String()),
        sa.Column("tax_exempt", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("backup_withholding", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tax_exemption_number", sa.String()),
        sa.Column("ifsc_code", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("po_number", sa.String(), nullable=False),
        sa.Column("vendor_id", sa.String(length=36), sa.ForeignKey("po_vendors.id")),
        sa.Column("po_date", sa.String()),
        sa.Column("due_date", sa.String()),
        sa.Column("subtotal", sa.Numeric(18, 2)),
        sa.Column("total_tax_amount", sa.Numeric(18, 2)),
        sa.Column("total_amount", sa.Numeric(18, 2)),
        sa.Column("currency", sa.String()),
        sa.Column("payment_terms", sa.String()),
        sa.Column("destination_state", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_purchase_orders_po_number", "purchase_orders", ["po_number"], unique=True)
    op.create_table(
        "purchase_order_line_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("po_id", sa.String(length=36), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("description", sa.String()),
        sa.Column("quantity", sa.Numeric(18, 4)),
        sa.Column("unit_price", sa.Numeric(18, 5)),
        sa.Column("item_tax_rate", sa.Numeric(10, 6)),
        sa.Column("total_price", sa.Numeric(18, 2)),
        sa.Column("category", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_po_line_items_po_id", "purchase_order_line_items", ["po_id"])
    op.create_table(
        "processed_invoices",
        sa.Column("record_id", sa.String(length=36), primary_key=True),
        sa.Column("conversation_id", sa.String()),
        sa.Column("invoice_number", sa.String()),
        sa.Column("verdict", sa.String(), nullable=False),
        sa.Column("reason_codes", sa.JSON()),
        sa.Column("checks", sa.JSON()),
        sa.Column("explanation", sa.Text()),
        sa.Column("extracted_invoice", sa.JSON()),
        sa.Column("matched_po_number", sa.String()),
        sa.Column("matched_po_source", sa.String()),
        sa.Column("matched_po", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_processed_invoices_conversation_id", "processed_invoices", ["conversation_id"])
    op.create_index("ix_processed_invoices_invoice_number", "processed_invoices", ["invoice_number"])


def downgrade() -> None:
    op.drop_table("processed_invoices")
    op.drop_table("purchase_order_line_items")
    op.drop_index("ix_purchase_orders_po_number", table_name="purchase_orders")
    op.drop_table("purchase_orders")
    op.drop_table("po_vendors")
