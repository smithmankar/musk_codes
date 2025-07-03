import requests
import csv

# === CONFIG ===
WATI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwYWMxYjQ2NC00YTc0LTQ3MmEtYmUzZi0zZWViNzdmOWJjNzgiLCJ1bmlxdWVfbmFtZSI6Im5hbmRpbmlAbXVza3VyYWhhdC5vcmcuaW4iLCJuYW1laWQiOiJuYW5kaW5pQG11c2t1cmFoYXQub3JnLmluIiwiZW1haWwiOiJuYW5kaW5pQG11c2t1cmFoYXQub3JnLmluIiwiYXV0aF90aW1lIjoiMDYvMjcvMjAyNSAxMjo0NDozMyIsInRlbmFudF9pZCI6IjEwNDI3MCIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.4FtwXhWbeFpOhb3BBItJXIhpzeF1n1ICCxMX7jXNJXA"  # <-- Replace with your actual API key
TAG_TO_FILTER = "tl"  # <-- Replace with your desired tag
OUTPUT_CSV_FILE = "wati_contacts_with_tag.csv"

# === FETCH CONTACTS ===
def fetch_contacts():
    url = "https://live-mt-server.wati.io/104270/api/v1/getContacts"
    headers = {
        "Authorization": f"Bearer {WATI_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# === FILTER BY TAG ===
def filter_contacts_by_tag(contacts, tag):
    filtered = []
    for contact in contacts.get("contacts", []):
        contact_tags = contact.get("tags", [])
        if tag in contact_tags:
            filtered.append(contact)
    return filtered

# === EXPORT TO CSV ===
def export_to_csv(contacts, filename):
    if not contacts:
        print("No contacts found with the specified tag.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["Name", "Phone", "Tags", "Created At", "Custom Fields"])

        for contact in contacts:
            name = contact.get("fullName", "")
            phone = contact.get("phoneNumber", "")
            tags = ", ".join(contact.get("tags", []))
            created_at = contact.get("createdAt", "")
            custom_fields = contact.get("customFields", {})
            custom_fields_str = ", ".join(f"{k}:{v}" for k, v in custom_fields.items())
            writer.writerow([name, phone, tags, created_at, custom_fields_str])

    print(f"Exported {len(contacts)} contacts to {filename}")

# === MAIN ===
if __name__ == "__main__":
    try:
        all_contacts = fetch_contacts()
        print(all_contacts)
        filtered_contacts = filter_contacts_by_tag(all_contacts, TAG_TO_FILTER)
        export_to_csv(filtered_contacts, OUTPUT_CSV_FILE)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
