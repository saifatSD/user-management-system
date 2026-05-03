from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime

# MongoDB connection string – your local server
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "user_management"
COLLECTION_NAME = "users"

# Create client and get the users collection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

# Enforce unique phone numbers
users_collection.create_index("phone", unique=True)

# //////////////////////////////////////////////

def validate_date(date_text):
    """Check if date_text is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    

#//////////////////////////////////////////////
def insert_user(first_name, last_name, birth_date, birth_place, phone):
    # Check for empty fields
    if not all([first_name, last_name, birth_date, birth_place, phone]):
        return False, "All fields are required."

    # Validate date format
    if not validate_date(birth_date):
        return False, "Invalid date format. Use YYYY-MM-DD."

    # Try to insert
    try:
        users_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "birth_place": birth_place,
            "phone": phone
        })
        return True, "User added successfully."
    except DuplicateKeyError:
        return False, "Phone number already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    

    #//////////////////////////////////////////////
def get_all_users():
   #Return a list of all user documents (without MongoDB _id)
    return list(users_collection.find({}, {"_id": 0}))
    

    #//////////////////////////////////////////////
def search_users(query):
    #Search users by any field containing the query (case‑insensitive)."""
    if not query:
        return get_all_users()
    regex = {"$regex": query, "$options": "i"}
    return list(users_collection.find({
        "$or": [
            {"first_name": regex},
            {"last_name": regex},
            {"birth_date": regex},
            {"birth_place": regex},
            {"phone": regex}
        ]
    }, {"_id": 0}))


#//////////////////////////////////////////////


def update_user(phone, updated_data):
    """Update user identified by phone. 'phone' cannot be changed."""
    if not phone:
        return False, "Phone number is required to update."

    # Validate date if it's being changed
    if "birth_date" in updated_data and not validate_date(updated_data["birth_date"]):
        return False, "Invalid date format."

    # Ensure no empty fields in the update
    for key, value in updated_data.items():
        if not value:
            return False, f"{key.replace('_', ' ').title()} cannot be empty."

    result = users_collection.update_one(
        {"phone": phone},
        {"$set": updated_data}
    )

    if result.matched_count == 0:
        return False, "User not found."
    return True, "User updated successfully."


#//////////////////////////////////////////////

def delete_user(phone):
    """Delete a user by phone number."""
    result = users_collection.delete_one({"phone": phone})
    if result.deleted_count == 0:
        return False, "User not found."
    return True, "User deleted successfully."


#//////////////////////////////////////////////

def test_connection():
    """Check if MongoDB is reachable."""
    try:
        client.admin.command('ping')
        return True
    except ConnectionFailure:
        return False