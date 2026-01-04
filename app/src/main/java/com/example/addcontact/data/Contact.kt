package com.example.addcontact.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity representing a contact in the database.
 * All fields except id are optional to allow partial contact information.
 */
@Entity(tableName = "contacts")
data class Contact(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val firstName: String? = null,
    val lastName: String? = null,
    val email: String? = null,
    val phoneNumber: String? = null
) {
    /**
     * Returns a display name for the contact.
     * Uses first name + last name if available, otherwise falls back to email or phone.
     */
    fun getDisplayName(): String {
        val fullName = listOfNotNull(firstName, lastName)
            .filter { it.isNotBlank() }
            .joinToString(" ")

        return when {
            fullName.isNotBlank() -> fullName
            !email.isNullOrBlank() -> email
            !phoneNumber.isNullOrBlank() -> phoneNumber
            else -> "Unknown Contact"
        }
    }

    /**
     * Checks if the contact has at least one piece of information.
     */
    fun hasAnyInfo(): Boolean {
        return !firstName.isNullOrBlank() ||
                !lastName.isNullOrBlank() ||
                !email.isNullOrBlank() ||
                !phoneNumber.isNullOrBlank()
    }
}
