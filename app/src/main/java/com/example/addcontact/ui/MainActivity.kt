package com.example.addcontact.ui

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.addcontact.R
import com.example.addcontact.adapter.ContactAdapter
import com.example.addcontact.data.Contact
import com.example.addcontact.data.ContactDatabase
import com.example.addcontact.data.ContactRepository
import com.example.addcontact.databinding.ActivityMainBinding
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var repository: ContactRepository
    private lateinit var adapter: ContactAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupDatabase()
        setupToolbar()
        setupRecyclerView()
        setupSearch()
        setupFab()
        observeContacts()
    }

    private fun setupDatabase() {
        val database = ContactDatabase.getDatabase(applicationContext)
        repository = ContactRepository(database.contactDao())
    }

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
    }

    private fun setupRecyclerView() {
        adapter = ContactAdapter(
            onContactClick = { contact ->
                showAddEditDialog(contact)
            },
            onDeleteClick = { contact ->
                showDeleteConfirmation(contact)
            }
        )
        binding.contactsRecyclerView.layoutManager = LinearLayoutManager(this)
        binding.contactsRecyclerView.adapter = adapter
    }

    private fun setupSearch() {
        binding.searchEditText.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val query = s?.toString() ?: ""
                searchContacts(query)
            }
        })
    }

    private fun setupFab() {
        binding.fabAddContact.setOnClickListener {
            showAddEditDialog(null)
        }
    }

    private fun observeContacts() {
        lifecycleScope.launch {
            repository.allContacts.collectLatest { contacts ->
                updateUI(contacts)
            }
        }
    }

    private fun searchContacts(query: String) {
        lifecycleScope.launch {
            if (query.isBlank()) {
                repository.allContacts.collectLatest { contacts ->
                    updateUI(contacts)
                }
            } else {
                repository.searchContacts(query).collectLatest { contacts ->
                    updateUI(contacts)
                }
            }
        }
    }

    private fun updateUI(contacts: List<Contact>) {
        adapter.submitList(contacts)
        binding.emptyView.visibility = if (contacts.isEmpty()) View.VISIBLE else View.GONE
        binding.contactsRecyclerView.visibility = if (contacts.isEmpty()) View.GONE else View.VISIBLE
    }

    private fun showAddEditDialog(contact: Contact?) {
        AddEditContactDialog(
            context = this,
            contact = contact,
            onSave = { savedContact ->
                lifecycleScope.launch {
                    if (contact == null) {
                        repository.insertContact(savedContact)
                        Toast.makeText(this@MainActivity, R.string.contact_added, Toast.LENGTH_SHORT).show()
                    } else {
                        repository.updateContact(savedContact)
                        Toast.makeText(this@MainActivity, R.string.contact_updated, Toast.LENGTH_SHORT).show()
                    }
                }
            }
        ).show()
    }

    private fun showDeleteConfirmation(contact: Contact) {
        AlertDialog.Builder(this)
            .setTitle(R.string.delete_contact)
            .setMessage(R.string.confirm_delete)
            .setPositiveButton(R.string.delete) { _, _ ->
                lifecycleScope.launch {
                    repository.deleteContact(contact)
                    Toast.makeText(this@MainActivity, R.string.contact_deleted, Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }
}
