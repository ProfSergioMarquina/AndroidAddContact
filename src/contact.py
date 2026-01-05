#!/usr/bin/env python3
"""
Contact model and data classes.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class Contact:
    """Represents a contact with optional fields."""
    id: int = 0
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    def has_any_info(self) -> bool:
        """Check if contact has at least one piece of information."""
        return any([
            self.first_name and self.first_name.strip(),
            self.last_name and self.last_name.strip(),
            self.email and self.email.strip(),
            self.phone and self.phone.strip()
        ])

    def get_display_name(self) -> str:
        """Get a display name for the contact."""
        parts = []
        if self.first_name and self.first_name.strip():
            parts.append(self.first_name.strip())
        if self.last_name and self.last_name.strip():
            parts.append(self.last_name.strip())

        if parts:
            return " ".join(parts)
        elif self.email and self.email.strip():
            return self.email.strip()
        elif self.phone and self.phone.strip():
            return self.phone.strip()
        else:
            return "Unknown Contact"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """Create Contact from dictionary."""
        return cls(
            id=data.get('id', 0),
            first_name=data.get('first_name') or data.get('firstName'),
            last_name=data.get('last_name') or data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone')
        )

    def merge_with(self, other: 'Contact') -> 'Contact':
        """
        Merge this contact with another, filling in missing fields.
        Returns a new Contact with merged data.
        """
        return Contact(
            id=self.id,
            first_name=other.first_name if other.first_name and other.first_name.strip() else self.first_name,
            last_name=other.last_name if other.last_name and other.last_name.strip() else self.last_name,
            email=other.email if other.email and other.email.strip() else self.email,
            phone=other.phone if other.phone and other.phone.strip() else self.phone
        )

    def __str__(self) -> str:
        """String representation of the contact."""
        lines = [f"ID: {self.id}", f"Name: {self.get_display_name()}"]
        if self.email:
            lines.append(f"Email: {self.email}")
        if self.phone:
            lines.append(f"Phone: {self.phone}")
        return "\n".join(lines)
