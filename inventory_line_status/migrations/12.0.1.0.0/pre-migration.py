def migrate(cr, version):
    """Create required tables for optimistic updates."""
    cr.execute("""
        CREATE TABLE IF NOT EXISTS stock_move_status_updates (
            move_id integer PRIMARY KEY,
            new_status varchar,
            create_date timestamp without time zone,
            processed boolean DEFAULT false
        );
        CREATE INDEX IF NOT EXISTS stock_move_status_updates_date_idx 
        ON stock_move_status_updates (create_date);

        CREATE TABLE IF NOT EXISTS stock_move_line_status_updates (
            move_line_id integer PRIMARY KEY,
            new_status varchar,
            create_date timestamp without time zone,
            processed boolean DEFAULT false
        );
        CREATE INDEX IF NOT EXISTS stock_move_line_status_updates_date_idx 
        ON stock_move_line_status_updates (create_date);
    """)
