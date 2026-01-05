#!/usr/bin/env python3
"""
Contact storage using SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from contact import Contact


class ContactStorage:
    """SQLite-based storage for contacts."""

    def __init__(self, db_path: str = "contacts.db"):
        """
        Initialize contact storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    phone TEXT
                )
            """)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def add(self, contact: Contact) -> int:
        """
        Add a new contact.

        Args:
            contact: Contact to add

        Returns:
            ID of the newly created contact
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO contacts (first_name, last_name, email, phone)
                VALUES (?, ?, ?, ?)
                """,
                (contact.first_name, contact.last_name, contact.email, contact.phone)
            )
            conn.commit()
            return cursor.lastrowid

    def get(self, contact_id: int) -> Optional[Contact]:
        """
        Get a contact by ID.

        Args:
            contact_id: ID of the contact

        Returns:
            Contact if found, None otherwise
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM contacts WHERE id = ?",
                (contact_id,)
            ).fetchone()

            if row:
                return self._row_to_contact(row)
            return None

    def get_all(self) -> List[Contact]:
        """
        Get all contacts.

        Returns:
            List of all contacts
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM contacts ORDER BY first_name, last_name"
            ).fetchall()
            return [self._row_to_contact(row) for row in rows]

    def update(self, contact: Contact) -> bool:
        """
        Update an existing contact.

        Args:
            contact: Contact with updated data

        Returns:
            True if contact was updated, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE contacts
                SET first_name = ?, last_name = ?, email = ?, phone = ?
                WHERE id = ?
                """,
                (contact.first_name, contact.last_name, contact.email, contact.phone, contact.id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, contact_id: int) -> bool:
        """
        Delete a contact by ID.

        Args:
            contact_id: ID of the contact to delete

        Returns:
            True if contact was deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM contacts WHERE id = ?",
                (contact_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def search(self, query: str) -> List[Contact]:
        """
        Search contacts by name, email, or phone.

        Args:
            query: Search query string

        Returns:
            List of matching contacts
        """
        search_pattern = f"%{query}%"
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM contacts
                WHERE first_name LIKE ?
                   OR last_name LIKE ?
                   OR email LIKE ?
                   OR phone LIKE ?
                ORDER BY first_name, last_name
                """,
                (search_pattern, search_pattern, search_pattern, search_pattern)
            ).fetchall()
            return [self._row_to_contact(row) for row in rows]

    def complete(self, contact_id: int, updates: Contact) -> Optional[Contact]:
        """
        Complete/update a contact with additional information.

        Args:
            contact_id: ID of the contact to complete
            updates: Contact object with fields to add/update

        Returns:
            Updated contact if found, None otherwise
        """
        existing = self.get(contact_id)
        if not existing:
            return None

        merged = existing.merge_with(updates)
        self.update(merged)
        return merged

    def count(self) -> int:
        """Get total number of contacts."""
        with self._get_connection() as conn:
            result = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()
            return result[0]

    def _row_to_contact(self, row: sqlite3.Row) -> Contact:
        """Convert a database row to a Contact object."""
        return Contact(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            phone=row['phone']
        )
