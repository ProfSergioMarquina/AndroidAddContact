# Contact Manager

A Python CLI application for managing contacts with name, surname, email, and phone number.

## Features

- **Add Contacts**: Create new contacts with any combination of fields
- **Complete Contacts**: Fill in missing information for existing contacts
- **Update Contacts**: Modify existing contact information
- **Search**: Find contacts by name, email, or phone
- **Import/Export**: Batch operations via JSON files
- **SQLite Storage**: Persistent local database

## Project Structure

```
ContactManager/
├── src/
│   ├── contact.py           # Contact data model
│   ├── storage.py           # SQLite database storage
│   └── contact_manager.py   # CLI application
├── sample_contacts.json     # Example contacts file
└── README.md
```

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Usage

### Add a contact

```bash
# Full contact
python src/contact_manager.py add \
    --first-name "John" \
    --last-name "Doe" \
    --email "john@example.com" \
    --phone "+1234567890"

# Partial contact - only email
python src/contact_manager.py add --email "support@company.com"

# Partial contact - only phone
python src/contact_manager.py add --phone "+1234567890"

# Partial contact - only name
python src/contact_manager.py add --first-name "John" --last-name "Doe"
```

### List all contacts

```bash
python src/contact_manager.py list
```

### Show contact details

```bash
python src/contact_manager.py show 1
```

### Complete a contact (add missing information)

```bash
# Add email to existing contact
python src/contact_manager.py complete 1 --email "john.doe@example.com"

# Add phone and email
python src/contact_manager.py complete 1 --phone "+1234567890" --email "new@example.com"
```

### Update a contact

```bash
python src/contact_manager.py update 1 --first-name "Jonathan"
```

### Search contacts

```bash
python src/contact_manager.py search "john"
python src/contact_manager.py search "@example.com"
python src/contact_manager.py search "+123"
```

### Delete a contact

```bash
# With confirmation
python src/contact_manager.py delete 1

# Skip confirmation
python src/contact_manager.py delete 1 --force
```

### Import contacts from JSON

```bash
python src/contact_manager.py import sample_contacts.json
```

### Export contacts to JSON

```bash
python src/contact_manager.py export backup.json
```

### Use a different database file

```bash
python src/contact_manager.py --db mycontacts.db list
python src/contact_manager.py --db mycontacts.db add --first-name "John"
```

## JSON Format

For import/export operations, use this JSON format:

```json
[
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    },
    {
        "first_name": "Jane",
        "email": "jane@example.com"
    },
    {
        "phone": "+1122334455"
    }
]
```

## Commands Reference

| Command    | Description                              |
|------------|------------------------------------------|
| `add`      | Add a new contact                        |
| `list`     | List all contacts                        |
| `show`     | Show details of a specific contact       |
| `complete` | Add missing info to an existing contact  |
| `update`   | Update an existing contact               |
| `delete`   | Delete a contact                         |
| `search`   | Search contacts by any field             |
| `import`   | Import contacts from a JSON file         |
| `export`   | Export contacts to a JSON file           |

## Options

| Option          | Short | Description                    |
|-----------------|-------|--------------------------------|
| `--db`          | `-d`  | Database file path             |
| `--first-name`  | `-f`  | First name                     |
| `--last-name`   | `-l`  | Last name                      |
| `--email`       | `-e`  | Email address                  |
| `--phone`       | `-p`  | Phone number                   |
| `--force`       | `-y`  | Skip confirmation (for delete) |

## License

MIT License
