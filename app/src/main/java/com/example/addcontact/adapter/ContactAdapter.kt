package com.example.addcontact.adapter

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.addcontact.data.Contact
import com.example.addcontact.databinding.ItemContactBinding

/**
 * Adapter for displaying contacts in a RecyclerView.
 */
class ContactAdapter(
    private val onContactClick: (Contact) -> Unit,
    private val onDeleteClick: (Contact) -> Unit
) : ListAdapter<Contact, ContactAdapter.ContactViewHolder>(ContactDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ContactViewHolder {
        val binding = ItemContactBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ContactViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ContactViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ContactViewHolder(
        private val binding: ItemContactBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(contact: Contact) {
            // Set avatar with initials
            val initials = getInitials(contact)
            binding.avatarTextView.text = initials
            binding.avatarTextView.setBackgroundColor(getColorForContact(contact))

            // Set name
            binding.nameTextView.text = contact.getDisplayName()

            // Set details (phone and/or email)
            val details = buildDetails(contact)
            binding.detailsTextView.text = details

            // Click listeners
            binding.root.setOnClickListener {
                onContactClick(contact)
            }
            binding.deleteButton.setOnClickListener {
                onDeleteClick(contact)
            }
        }

        private fun getInitials(contact: Contact): String {
            val firstName = contact.firstName?.firstOrNull()?.uppercaseChar() ?: ""
            val lastName = contact.lastName?.firstOrNull()?.uppercaseChar() ?: ""

            return when {
                firstName != "" && lastName != "" -> "$firstName$lastName"
                firstName != "" -> firstName.toString()
                lastName != "" -> lastName.toString()
                !contact.email.isNullOrBlank() -> contact.email.first().uppercaseChar().toString()
                !contact.phoneNumber.isNullOrBlank() -> "#"
                else -> "?"
            }
        }

        private fun buildDetails(contact: Contact): String {
            val parts = mutableListOf<String>()
            if (!contact.phoneNumber.isNullOrBlank()) {
                parts.add(contact.phoneNumber)
            }
            if (!contact.email.isNullOrBlank()) {
                parts.add(contact.email)
            }
            return parts.joinToString("\n")
        }

        private fun getColorForContact(contact: Contact): Int {
            val colors = listOf(
                Color.parseColor("#1976D2"),
                Color.parseColor("#388E3C"),
                Color.parseColor("#D32F2F"),
                Color.parseColor("#7B1FA2"),
                Color.parseColor("#C2185B"),
                Color.parseColor("#00796B"),
                Color.parseColor("#F57C00"),
                Color.parseColor("#5D4037")
            )
            val hash = contact.getDisplayName().hashCode()
            return colors[Math.abs(hash) % colors.size]
        }
    }

    class ContactDiffCallback : DiffUtil.ItemCallback<Contact>() {
        override fun areItemsTheSame(oldItem: Contact, newItem: Contact): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Contact, newItem: Contact): Boolean {
            return oldItem == newItem
        }
    }
}
