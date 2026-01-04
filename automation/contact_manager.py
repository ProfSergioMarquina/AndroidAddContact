#!/usr/bin/env python3
"""
Android Contact Manager - Python Automation Script

This script automates adding and completing contacts on an Android device
using ADB (Android Debug Bridge) to communicate with the AddContact app.

Requirements:
    - Python 3.7+
    - ADB installed and in PATH
    - Android device connected via USB or emulator running
    - AddContact app installed on the device

Usage:
    python contact_manager.py add --first-name "John" --last-name "Doe" --email "john@example.com" --phone "+1234567890"
    python contact_manager.py complete --id 1 --email "updated@example.com"
    python contact_manager.py batch --file contacts.json
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List


@dataclass
class Contact:
    """Represents a contact with optional fields."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    id: Optional[int] = None

    def has_any_info(self) -> bool:
        """Check if contact has at least one piece of information."""
        return any([self.first_name, self.last_name, self.email, self.phone])

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'phone': self.phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """Create Contact from dictionary."""
        return cls(
            id=data.get('id'),
            first_name=data.get('firstName') or data.get('first_name'),
            last_name=data.get('lastName') or data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone')
        )


class ADBError(Exception):
    """Exception raised for ADB errors."""
    pass


class ContactManager:
    """Manages contacts on Android device via ADB."""

    PACKAGE = "com.example.addcontact"
    ACTION_ADD = f"{PACKAGE}.ADD_CONTACT"
    ACTION_COMPLETE = f"{PACKAGE}.COMPLETE_CONTACT"

    def __init__(self, device_serial: Optional[str] = None):
        """
        Initialize ContactManager.

        Args:
            device_serial: Optional device serial number for targeting specific device
        """
        self.device_serial = device_serial
        self._verify_adb()

    def _get_adb_command(self) -> List[str]:
        """Get base ADB command with optional device targeting."""
        cmd = ["adb"]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        return cmd

    def _verify_adb(self) -> None:
        """Verify ADB is available and device is connected."""
        try:
            result = subprocess.run(
                self._get_adb_command() + ["devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ADBError("ADB command failed")

            lines = result.stdout.strip().split('\n')
            devices = [l for l in lines[1:] if l.strip() and 'device' in l]

            if not devices:
                raise ADBError("No Android device connected. Please connect a device or start an emulator.")

            print(f"Found {len(devices)} device(s) connected")

        except FileNotFoundError:
            raise ADBError("ADB not found. Please install Android SDK and add adb to PATH.")
        except subprocess.TimeoutExpired:
            raise ADBError("ADB command timed out.")

    def _run_broadcast(self, action: str, extras: dict) -> bool:
        """
        Send a broadcast to the Android app.

        Args:
            action: The broadcast action to send
            extras: Dictionary of extra parameters

        Returns:
            True if broadcast was sent successfully
        """
        cmd = self._get_adb_command() + ["shell", "am", "broadcast", "-a", action]

        for key, value in extras.items():
            if value is not None:
                if isinstance(value, int):
                    cmd.extend(["--el", key, str(value)])
                else:
                    # Escape special characters for shell
                    escaped_value = str(value).replace('"', '\\"')
                    cmd.extend(["--es", key, f'"{escaped_value}"'])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False

            if "Broadcast completed" in result.stdout:
                return True

            print(f"Unexpected response: {result.stdout}")
            return True  # Broadcast likely succeeded

        except subprocess.TimeoutExpired:
            print("Error: ADB broadcast timed out")
            return False
        except Exception as e:
            print(f"Error sending broadcast: {e}")
            return False

    def add_contact(self, contact: Contact) -> bool:
        """
        Add a new contact to the app.

        Args:
            contact: Contact object with contact information

        Returns:
            True if contact was added successfully
        """
        if not contact.has_any_info():
            print("Error: Contact must have at least one field filled")
            return False

        extras = {
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "email": contact.email,
            "phone": contact.phone
        }

        # Remove None values
        extras = {k: v for k, v in extras.items() if v is not None}

        print(f"Adding contact: {contact.first_name or ''} {contact.last_name or ''}")
        return self._run_broadcast(self.ACTION_ADD, extras)

    def complete_contact(self, contact: Contact) -> bool:
        """
        Complete/update an existing contact.

        Args:
            contact: Contact object with id and fields to update

        Returns:
            True if contact was updated successfully
        """
        if contact.id is None:
            print("Error: Contact ID is required for completion")
            return False

        extras = {
            "id": contact.id,
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "email": contact.email,
            "phone": contact.phone
        }

        # Keep id, remove other None values
        extras = {k: v for k, v in extras.items() if v is not None or k == "id"}

        print(f"Completing contact ID {contact.id}")
        return self._run_broadcast(self.ACTION_COMPLETE, extras)

    def batch_add(self, contacts: List[Contact], delay: float = 0.5) -> tuple:
        """
        Add multiple contacts in batch.

        Args:
            contacts: List of Contact objects
            delay: Delay between operations in seconds

        Returns:
            Tuple of (success_count, failure_count)
        """
        success = 0
        failed = 0

        for i, contact in enumerate(contacts, 1):
            print(f"[{i}/{len(contacts)}] ", end="")
            if self.add_contact(contact):
                success += 1
            else:
                failed += 1

            if i < len(contacts):
                time.sleep(delay)

        return success, failed

    def batch_complete(self, contacts: List[Contact], delay: float = 0.5) -> tuple:
        """
        Complete multiple contacts in batch.

        Args:
            contacts: List of Contact objects with IDs
            delay: Delay between operations in seconds

        Returns:
            Tuple of (success_count, failure_count)
        """
        success = 0
        failed = 0

        for i, contact in enumerate(contacts, 1):
            print(f"[{i}/{len(contacts)}] ", end="")
            if self.complete_contact(contact):
                success += 1
            else:
                failed += 1

            if i < len(contacts):
                time.sleep(delay)

        return success, failed


def load_contacts_from_file(file_path: str) -> List[Contact]:
    """
    Load contacts from a JSON file.

    Expected format:
    [
        {"firstName": "John", "lastName": "Doe", "email": "john@example.com", "phone": "+1234567890"},
        {"firstName": "Jane", "email": "jane@example.com"}
    ]
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return [Contact.from_dict(item) for item in data]
    else:
        return [Contact.from_dict(data)]


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Automate contact management on Android device",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Add a new contact
    python contact_manager.py add --first-name "John" --last-name "Doe" --email "john@example.com"

    # Add contact with only phone number
    python contact_manager.py add --phone "+1234567890"

    # Complete an existing contact (add missing fields)
    python contact_manager.py complete --id 1 --email "updated@example.com"

    # Batch add contacts from JSON file
    python contact_manager.py batch --file contacts.json

    # Batch complete contacts from JSON file
    python contact_manager.py batch --file updates.json --mode complete
        """
    )

    parser.add_argument(
        '--device', '-d',
        help='Target device serial number (optional)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new contact')
    add_parser.add_argument('--first-name', '-f', help='First name')
    add_parser.add_argument('--last-name', '-l', help='Last name')
    add_parser.add_argument('--email', '-e', help='Email address')
    add_parser.add_argument('--phone', '-p', help='Phone number')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Complete/update an existing contact')
    complete_parser.add_argument('--id', '-i', type=int, required=True, help='Contact ID to update')
    complete_parser.add_argument('--first-name', '-f', help='First name')
    complete_parser.add_argument('--last-name', '-l', help='Last name')
    complete_parser.add_argument('--email', '-e', help='Email address')
    complete_parser.add_argument('--phone', '-p', help='Phone number')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch add/complete contacts from file')
    batch_parser.add_argument('--file', '-f', required=True, help='JSON file with contacts')
    batch_parser.add_argument('--mode', '-m', choices=['add', 'complete'], default='add',
                              help='Operation mode (default: add)')
    batch_parser.add_argument('--delay', '-d', type=float, default=0.5,
                              help='Delay between operations in seconds (default: 0.5)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        manager = ContactManager(device_serial=args.device)

        if args.command == 'add':
            contact = Contact(
                first_name=args.first_name,
                last_name=args.last_name,
                email=args.email,
                phone=args.phone
            )

            if not contact.has_any_info():
                print("Error: At least one contact field must be provided")
                sys.exit(1)

            if manager.add_contact(contact):
                print("Contact added successfully!")
            else:
                print("Failed to add contact")
                sys.exit(1)

        elif args.command == 'complete':
            contact = Contact(
                id=args.id,
                first_name=args.first_name,
                last_name=args.last_name,
                email=args.email,
                phone=args.phone
            )

            if manager.complete_contact(contact):
                print("Contact completed successfully!")
            else:
                print("Failed to complete contact")
                sys.exit(1)

        elif args.command == 'batch':
            contacts = load_contacts_from_file(args.file)
            print(f"Loaded {len(contacts)} contact(s) from {args.file}")

            if args.mode == 'add':
                success, failed = manager.batch_add(contacts, delay=args.delay)
            else:
                success, failed = manager.batch_complete(contacts, delay=args.delay)

            print(f"\nResults: {success} succeeded, {failed} failed")

            if failed > 0:
                sys.exit(1)

    except ADBError as e:
        print(f"ADB Error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(130)


if __name__ == '__main__':
    main()
