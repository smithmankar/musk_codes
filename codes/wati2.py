import requests
import csv

# === CONFIG ===
WATI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwYWMxYjQ2NC00YTc0LTQ3MmEtYmUzZi0zZWViNzdmOWJjNzgiLCJ1bmlxdWVfbmFtZSI6Im5hbmRpbmlAbXVza3VyYWhhdC5vcmcuaW4iLCJuYW1laWQiOiJuYW5kaW5pQG11c2t1cmFoYXQub3JnLmluIiwiZW1haWwiOiJuYW5kaW5pQG11c2t1cmFoYXQub3JnLmluIiwiYXV0aF90aW1lIjoiMDYvMjcvMjAyNSAxMjo0NDozMyIsInRlbmFudF9pZCI6IjEwNDI3MCIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.4FtwXhWbeFpOhb3BBItJXIhpzeF1n1ICCxMX7jXNJXA"  # <-- Replace with your actual API key
CUSTOM_FIELD_NAME = "tagName"  # <-- replace with your field name
CUSTOM_FIELD_VALUE = "tl"      # <-- replace with the value you want to filter
OUTPUT_CSV_FILE = "wati_contacts_filtered.csv"

# === FETCH CONTACTS WITH CORRECT PAGINATION ===
def fetch_all_contacts():
    contacts = []
    next_page_url = "https://live-mt-server.wati.io/104270/api/v1/getContacts?pageSize=100&pageNumber=1"

    while next_page_url:
        headers = {
            "Authorization": f"Bearer {WATI_API_KEY}"
        }
        response = requests.get(next_page_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        batch = data.get("contacts", [])
        contacts.extend(batch)

        next_page_url = data.get("link", {}).get("nextPage")

    return contacts

# === FILTER BY CUSTOM FIELD ===
def filter_contacts_by_custom_field(contacts, field_name, field_value):
    filtered = []
    for contact in contacts:
        for field in contact.get("customFields", []):
            if field.get("name") == field_name and field.get("value") == field_value:
                filtered.append(contact)
                break
    return filtered

# === EXPORT TO CSV ===
def export_to_csv(contacts, filename):
    if not contacts:
        print("No contacts found with the specified custom field and value.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Phone", "Custom Fields", "Created At"])

        for contact in contacts:
            name = contact.get("fullName", "")
            phone = contact.get("phoneNumber", "")
            created_at = contact.get("createdAt", "")
            custom_fields = contact.get("customFields", [])
            custom_fields_str = ", ".join(f"{cf.get('name')}:{cf.get('value')}" for cf in custom_fields)
            writer.writerow([name, phone, custom_fields_str, created_at])

    print(f"Exported {len(contacts)} contacts to {filename}")

# === MAIN ===
if __name__ == "__main__":
    try:
        all_contacts = fetch_all_contacts()
        filtered_contacts = filter_contacts_by_custom_field(all_contacts, CUSTOM_FIELD_NAME, CUSTOM_FIELD_VALUE)
        export_to_csv(filtered_contacts, OUTPUT_CSV_FILE)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
