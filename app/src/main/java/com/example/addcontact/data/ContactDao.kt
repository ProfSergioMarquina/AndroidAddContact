package com.example.addcontact.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for Contact entity.
 * Provides methods for CRUD operations on contacts.
 */
@Dao
interface ContactDao {

    /**
     * Get all contacts ordered by first name, then last name.
     */
    @Query("SELECT * FROM contacts ORDER BY firstName ASC, lastName ASC")
    fun getAllContacts(): Flow<List<Contact>>

    /**
     * Get a single contact by ID.
     */
    @Query("SELECT * FROM contacts WHERE id = :id")
    suspend fun getContactById(id: Long): Contact?

    /**
     * Insert a new contact.
     * @return The ID of the newly inserted contact.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertContact(contact: Contact): Long

    /**
     * Update an existing contact.
     */
    @Update
    suspend fun updateContact(contact: Contact)

    /**
     * Delete a contact.
     */
    @Delete
    suspend fun deleteContact(contact: Contact)

    /**
     * Delete a contact by ID.
     */
    @Query("DELETE FROM contacts WHERE id = :id")
    suspend fun deleteContactById(id: Long)

    /**
     * Search contacts by name, email, or phone number.
     */
    @Query("""
        SELECT * FROM contacts
        WHERE firstName LIKE '%' || :query || '%'
           OR lastName LIKE '%' || :query || '%'
           OR email LIKE '%' || :query || '%'
           OR phoneNumber LIKE '%' || :query || '%'
        ORDER BY firstName ASC, lastName ASC
    """)
    fun searchContacts(query: String): Flow<List<Contact>>
}
