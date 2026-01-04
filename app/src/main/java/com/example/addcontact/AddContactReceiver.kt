package com.example.addcontact

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.example.addcontact.data.Contact
import com.example.addcontact.data.ContactDatabase
import com.example.addcontact.data.ContactRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * BroadcastReceiver for handling automated contact operations via ADB.
 *
 * Usage from Python/ADB:
 *
 * Add new contact:
 * adb shell am broadcast -a com.example.addcontact.ADD_CONTACT \
 *     --es firstName "John" \
 *     --es lastName "Doe" \
 *     --es email "john@example.com" \
 *     --es phone "+1234567890"
 *
 * Complete/Update existing contact by ID:
 * adb shell am broadcast -a com.example.addcontact.COMPLETE_CONTACT \
 *     --el id 1 \
 *     --es firstName "John" \
 *     --es lastName "Doe" \
 *     --es email "john@example.com" \
 *     --es phone "+1234567890"
 */
class AddContactReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "AddContactReceiver"
        const val ACTION_ADD = "com.example.addcontact.ADD_CONTACT"
        const val ACTION_COMPLETE = "com.example.addcontact.COMPLETE_CONTACT"

        const val EXTRA_ID = "id"
        const val EXTRA_FIRST_NAME = "firstName"
        const val EXTRA_LAST_NAME = "lastName"
        const val EXTRA_EMAIL = "email"
        const val EXTRA_PHONE = "phone"
    }

    override fun onReceive(context: Context, intent: Intent) {
        Log.d(TAG, "Received broadcast: ${intent.action}")

        val database = ContactDatabase.getDatabase(context)
        val repository = ContactRepository(database.contactDao())

        when (intent.action) {
            ACTION_ADD -> handleAddContact(intent, repository)
            ACTION_COMPLETE -> handleCompleteContact(intent, repository)
            else -> Log.w(TAG, "Unknown action: ${intent.action}")
        }
    }

    private fun handleAddContact(intent: Intent, repository: ContactRepository) {
        val firstName = intent.getStringExtra(EXTRA_FIRST_NAME)
        val lastName = intent.getStringExtra(EXTRA_LAST_NAME)
        val email = intent.getStringExtra(EXTRA_EMAIL)
        val phone = intent.getStringExtra(EXTRA_PHONE)

        val contact = Contact(
            firstName = firstName?.ifBlank { null },
            lastName = lastName?.ifBlank { null },
            email = email?.ifBlank { null },
            phoneNumber = phone?.ifBlank { null }
        )

        if (contact.hasAnyInfo()) {
            CoroutineScope(Dispatchers.IO).launch {
                val id = repository.insertContact(contact)
                Log.d(TAG, "Contact added with ID: $id")
            }
        } else {
            Log.w(TAG, "No contact info provided, skipping")
        }
    }

    private fun handleCompleteContact(intent: Intent, repository: ContactRepository) {
        val id = intent.getLongExtra(EXTRA_ID, -1)

        if (id == -1L) {
            Log.w(TAG, "No contact ID provided for completion")
            return
        }

        val firstName = intent.getStringExtra(EXTRA_FIRST_NAME)
        val lastName = intent.getStringExtra(EXTRA_LAST_NAME)
        val email = intent.getStringExtra(EXTRA_EMAIL)
        val phone = intent.getStringExtra(EXTRA_PHONE)

        CoroutineScope(Dispatchers.IO).launch {
            val existingContact = repository.getContactById(id)

            if (existingContact != null) {
                // Merge: use new values if provided, otherwise keep existing
                val updatedContact = existingContact.copy(
                    firstName = firstName?.ifBlank { null } ?: existingContact.firstName,
                    lastName = lastName?.ifBlank { null } ?: existingContact.lastName,
                    email = email?.ifBlank { null } ?: existingContact.email,
                    phoneNumber = phone?.ifBlank { null } ?: existingContact.phoneNumber
                )
                repository.updateContact(updatedContact)
                Log.d(TAG, "Contact $id updated/completed")
            } else {
                // If contact doesn't exist, create a new one with the provided ID
                val newContact = Contact(
                    id = id,
                    firstName = firstName?.ifBlank { null },
                    lastName = lastName?.ifBlank { null },
                    email = email?.ifBlank { null },
                    phoneNumber = phone?.ifBlank { null }
                )
                if (newContact.hasAnyInfo()) {
                    repository.insertContact(newContact)
                    Log.d(TAG, "New contact created with ID: $id")
                }
            }
        }
    }
}
