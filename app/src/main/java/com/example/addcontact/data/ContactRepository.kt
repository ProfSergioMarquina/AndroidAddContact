package com.example.addcontact.data

import kotlinx.coroutines.flow.Flow

/**
 * Repository for managing contact data.
 * Acts as a single source of truth for contact operations.
 */
class ContactRepository(private val contactDao: ContactDao) {

    /**
     * Get all contacts as a Flow.
     */
    val allContacts: Flow<List<Contact>> = contactDao.getAllContacts()

    /**
     * Get a single contact by ID.
     */
    suspend fun getContactById(id: Long): Contact? {
        return contactDao.getContactById(id)
    }

    /**
     * Insert a new contact.
     * @return The ID of the newly inserted contact.
     */
    suspend fun insertContact(contact: Contact): Long {
        return contactDao.insertContact(contact)
    }

    /**
     * Update an existing contact.
     */
    suspend fun updateContact(contact: Contact) {
        contactDao.updateContact(contact)
    }

    /**
     * Delete a contact.
     */
    suspend fun deleteContact(contact: Contact) {
        contactDao.deleteContact(contact)
    }

    /**
     * Delete a contact by ID.
     */
    suspend fun deleteContactById(id: Long) {
        contactDao.deleteContactById(id)
    }

    /**
     * Search contacts by query.
     */
    fun searchContacts(query: String): Flow<List<Contact>> {
        return contactDao.searchContacts(query)
    }
}
