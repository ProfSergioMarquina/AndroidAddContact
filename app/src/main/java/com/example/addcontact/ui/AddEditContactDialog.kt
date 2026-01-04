package com.example.addcontact.ui

import android.content.Context
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.example.addcontact.R
import com.example.addcontact.data.Contact
import com.example.addcontact.databinding.DialogAddEditContactBinding

/**
 * Dialog for adding or editing a contact.
 */
class AddEditContactDialog(
    private val context: Context,
    private val contact: Contact?,
    private val onSave: (Contact) -> Unit
) {

    fun show() {
        val binding = DialogAddEditContactBinding.inflate(
            android.view.LayoutInflater.from(context)
        )

        // Pre-fill fields if editing
        contact?.let {
            binding.firstNameEditText.setText(it.firstName ?: "")
            binding.lastNameEditText.setText(it.lastName ?: "")
            binding.emailEditText.setText(it.email ?: "")
            binding.phoneEditText.setText(it.phoneNumber ?: "")
        }

        val title = if (contact == null) R.string.add_contact else R.string.edit_contact

        AlertDialog.Builder(context)
            .setTitle(title)
            .setView(binding.root)
            .setPositiveButton(R.string.save) { _, _ ->
                val firstName = binding.firstNameEditText.text?.toString()?.trim()?.ifBlank { null }
                val lastName = binding.lastNameEditText.text?.toString()?.trim()?.ifBlank { null }
                val email = binding.emailEditText.text?.toString()?.trim()?.ifBlank { null }
                val phone = binding.phoneEditText.text?.toString()?.trim()?.ifBlank { null }

                val newContact = Contact(
                    id = contact?.id ?: 0,
                    firstName = firstName,
                    lastName = lastName,
                    email = email,
                    phoneNumber = phone
                )

                if (newContact.hasAnyInfo()) {
                    onSave(newContact)
                } else {
                    Toast.makeText(context, R.string.at_least_one_field, Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }
}
