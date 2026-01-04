# Android Add Contact

An Android application for managing contacts with Python automation support.

## Features

- **Add Contacts**: Create new contacts with name, surname, email, and/or phone number
- **Edit Contacts**: Update existing contact information
- **Complete Contacts**: Fill in missing information for partial contacts
- **Search**: Find contacts by name, email, or phone
- **Python Automation**: Add or complete contacts programmatically via ADB

## Project Structure

```
AndroidAddContact/
├── app/                          # Android application
│   ├── src/main/
│   │   ├── java/com/example/addcontact/
│   │   │   ├── data/            # Room database, entities, DAO
│   │   │   ├── ui/              # Activities and dialogs
│   │   │   ├── adapter/         # RecyclerView adapter
│   │   │   └── AddContactReceiver.kt  # Broadcast receiver for automation
│   │   └── res/                 # Resources (layouts, values, drawables)
│   └── build.gradle.kts
├── automation/                   # Python automation scripts
│   ├── contact_manager.py       # Main automation script
│   ├── sample_contacts.json     # Example contacts file
│   └── requirements.txt
├── build.gradle.kts
└── settings.gradle.kts
```

## Building the Android App

### Prerequisites

- Android Studio Arctic Fox or later
- JDK 17+
- Android SDK with API level 34

### Build Steps

1. Open the project in Android Studio
2. Sync Gradle files
3. Build and run on a device or emulator

Or build via command line:

```bash
./gradlew assembleDebug
```

## Python Automation

The Python script uses ADB to communicate with the Android app, allowing automated contact management.

### Prerequisites

- Python 3.7+
- ADB installed and in PATH
- Android device connected via USB (with USB debugging enabled) or emulator running
- AddContact app installed on the device

### Usage

#### Add a single contact

```bash
python automation/contact_manager.py add \
    --first-name "John" \
    --last-name "Doe" \
    --email "john@example.com" \
    --phone "+1234567890"
```

#### Add contact with partial information

```bash
# Only email
python automation/contact_manager.py add --email "support@company.com"

# Only phone number
python automation/contact_manager.py add --phone "+1234567890"

# Only name
python automation/contact_manager.py add --first-name "John" --last-name "Doe"
```

#### Complete/update an existing contact

```bash
python automation/contact_manager.py complete \
    --id 1 \
    --email "updated@example.com" \
    --phone "+0987654321"
```

#### Batch add contacts from JSON file

```bash
python automation/contact_manager.py batch --file automation/sample_contacts.json
```

#### Batch complete contacts

```bash
python automation/contact_manager.py batch \
    --file updates.json \
    --mode complete
```

### JSON Format

For batch operations, use this JSON format:

```json
[
    {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    },
    {
        "firstName": "Jane",
        "email": "jane@example.com"
    }
]
```

For completing contacts, include the `id` field:

```json
[
    {
        "id": 1,
        "email": "updated@example.com"
    },
    {
        "id": 2,
        "phone": "+1122334455"
    }
]
```

## Architecture

### Android App

- **Room Database**: Local SQLite database for persistent storage
- **Repository Pattern**: Single source of truth for contact data
- **Kotlin Coroutines**: Asynchronous database operations
- **Material Design**: Modern Android UI components
- **BroadcastReceiver**: Receives intents from ADB for automation

### Automation

- **ADB Integration**: Uses Android Debug Bridge for communication
- **Dataclass Models**: Type-safe contact representation
- **Batch Processing**: Efficient handling of multiple contacts
- **Error Handling**: Robust error handling with clear messages

## Permissions

The app requests the following permissions for potential future integration with the system contacts:

- `READ_CONTACTS`: Read system contacts
- `WRITE_CONTACTS`: Write to system contacts

## License

MIT License
