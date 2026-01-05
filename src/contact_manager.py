#!/usr/bin/env python3
"""
Contact Manager - CLI tool for managing contacts.

Usage:
    python contact_manager.py add --first-name "John" --last-name "Doe" --email "john@example.com"
    python contact_manager.py list
    python contact_manager.py show 1
    python contact_manager.py complete 1 --email "new@example.com"
    python contact_manager.py search "john"
    python contact_manager.py delete 1
    python contact_manager.py import contacts.json
    python contact_manager.py export contacts.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from contact import Contact
from storage import ContactStorage


DEFAULT_DB = "contacts.db"


def cmd_add(storage: ContactStorage, args) -> int:
    """Add a new contact."""
    contact = Contact(
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        phone=args.phone
    )

    if not contact.has_any_info():
        print("Error: At least one field must be provided")
        return 1

    contact_id = storage.add(contact)
    print(f"Contact added with ID: {contact_id}")
    return 0


def cmd_list(storage: ContactStorage, args) -> int:
    """List all contacts."""
    contacts = storage.get_all()

    if not contacts:
        print("No contacts found")
        return 0

    print(f"{'ID':<6} {'Name':<30} {'Email':<30} {'Phone':<20}")
    print("-" * 86)

    for contact in contacts:
        name = contact.get_display_name()[:28]
        email = (contact.email or "")[:28]
        phone = (contact.phone or "")[:18]
        print(f"{contact.id:<6} {name:<30} {email:<30} {phone:<20}")

    print(f"\nTotal: {len(contacts)} contact(s)")
    return 0


def cmd_show(storage: ContactStorage, args) -> int:
    """Show details of a specific contact."""
    contact = storage.get(args.id)

    if not contact:
        print(f"Error: Contact with ID {args.id} not found")
        return 1

    print(f"ID:         {contact.id}")
    print(f"First Name: {contact.first_name or '-'}")
    print(f"Last Name:  {contact.last_name or '-'}")
    print(f"Email:      {contact.email or '-'}")
    print(f"Phone:      {contact.phone or '-'}")
    return 0


def cmd_complete(storage: ContactStorage, args) -> int:
    """Complete/update an existing contact with additional information."""
    updates = Contact(
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        phone=args.phone
    )

    result = storage.complete(args.id, updates)

    if not result:
        print(f"Error: Contact with ID {args.id} not found")
        return 1

    print(f"Contact {args.id} updated successfully")
    print(f"\nUpdated contact:")
    print(f"  Name:  {result.get_display_name()}")
    print(f"  Email: {result.email or '-'}")
    print(f"  Phone: {result.phone or '-'}")
    return 0


def cmd_update(storage: ContactStorage, args) -> int:
    """Update an existing contact (replaces all fields)."""
    existing = storage.get(args.id)

    if not existing:
        print(f"Error: Contact with ID {args.id} not found")
        return 1

    updated = Contact(
        id=args.id,
        first_name=args.first_name if args.first_name is not None else existing.first_name,
        last_name=args.last_name if args.last_name is not None else existing.last_name,
        email=args.email if args.email is not None else existing.email,
        phone=args.phone if args.phone is not None else existing.phone
    )

    storage.update(updated)
    print(f"Contact {args.id} updated successfully")
    return 0


def cmd_delete(storage: ContactStorage, args) -> int:
    """Delete a contact."""
    if not args.force:
        contact = storage.get(args.id)
        if contact:
            print(f"Delete contact: {contact.get_display_name()}?")
            response = input("Type 'yes' to confirm: ")
            if response.lower() != 'yes':
                print("Cancelled")
                return 0

    if storage.delete(args.id):
        print(f"Contact {args.id} deleted")
        return 0
    else:
        print(f"Error: Contact with ID {args.id} not found")
        return 1


def cmd_search(storage: ContactStorage, args) -> int:
    """Search contacts."""
    contacts = storage.search(args.query)

    if not contacts:
        print(f"No contacts found matching '{args.query}'")
        return 0

    print(f"{'ID':<6} {'Name':<30} {'Email':<30} {'Phone':<20}")
    print("-" * 86)

    for contact in contacts:
        name = contact.get_display_name()[:28]
        email = (contact.email or "")[:28]
        phone = (contact.phone or "")[:18]
        print(f"{contact.id:<6} {name:<30} {email:<30} {phone:<20}")

    print(f"\nFound: {len(contacts)} contact(s)")
    return 0


def cmd_import(storage: ContactStorage, args) -> int:
    """Import contacts from a JSON file."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        return 1

    if isinstance(data, dict):
        data = [data]

    added = 0
    skipped = 0

    for item in data:
        contact = Contact.from_dict(item)
        if contact.has_any_info():
            storage.add(contact)
            added += 1
        else:
            skipped += 1

    print(f"Imported {added} contact(s)")
    if skipped:
        print(f"Skipped {skipped} empty contact(s)")
    return 0


def cmd_export(storage: ContactStorage, args) -> int:
    """Export contacts to a JSON file."""
    contacts = storage.get_all()

    if not contacts:
        print("No contacts to export")
        return 0

    data = [contact.to_dict() for contact in contacts]

    with open(args.file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(contacts)} contact(s) to {args.file}")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Contact Manager - CLI tool for managing contacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s add --first-name "John" --last-name "Doe" --email "john@example.com"
    %(prog)s add --phone "+1234567890"
    %(prog)s list
    %(prog)s show 1
    %(prog)s complete 1 --email "john.doe@example.com"
    %(prog)s search "john"
    %(prog)s delete 1
    %(prog)s import contacts.json
    %(prog)s export backup.json
        """
    )

    parser.add_argument(
        '--db', '-d',
        default=DEFAULT_DB,
        help=f'Database file path (default: {DEFAULT_DB})'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new contact')
    add_parser.add_argument('--first-name', '-f', help='First name')
    add_parser.add_argument('--last-name', '-l', help='Last name')
    add_parser.add_argument('--email', '-e', help='Email address')
    add_parser.add_argument('--phone', '-p', help='Phone number')

    # List command
    subparsers.add_parser('list', help='List all contacts')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show contact details')
    show_parser.add_argument('id', type=int, help='Contact ID')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Complete/add info to existing contact')
    complete_parser.add_argument('id', type=int, help='Contact ID')
    complete_parser.add_argument('--first-name', '-f', help='First name')
    complete_parser.add_argument('--last-name', '-l', help='Last name')
    complete_parser.add_argument('--email', '-e', help='Email address')
    complete_parser.add_argument('--phone', '-p', help='Phone number')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update an existing contact')
    update_parser.add_argument('id', type=int, help='Contact ID')
    update_parser.add_argument('--first-name', '-f', help='First name')
    update_parser.add_argument('--last-name', '-l', help='Last name')
    update_parser.add_argument('--email', '-e', help='Email address')
    update_parser.add_argument('--phone', '-p', help='Phone number')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a contact')
    delete_parser.add_argument('id', type=int, help='Contact ID')
    delete_parser.add_argument('--force', '-y', action='store_true', help='Skip confirmation')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search contacts')
    search_parser.add_argument('query', help='Search query')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import contacts from JSON file')
    import_parser.add_argument('file', help='JSON file to import')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export contacts to JSON file')
    export_parser.add_argument('file', help='JSON file to export to')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    storage = ContactStorage(args.db)

    commands = {
        'add': cmd_add,
        'list': cmd_list,
        'show': cmd_show,
        'complete': cmd_complete,
        'update': cmd_update,
        'delete': cmd_delete,
        'search': cmd_search,
        'import': cmd_import,
        'export': cmd_export,
    }

    return commands[args.command](storage, args)


if __name__ == '__main__':
    sys.exit(main())
