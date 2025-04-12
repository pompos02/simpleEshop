# app.py
import os
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
from dotenv import load_dotenv  # Added import for dotenv


import numpy as np # Included as required, though not directly used in core logic here

# --- Configuration ---
load_dotenv()  # Load environment variables from .env file

app = Flask(__name__,
            static_folder='static',  # Folder for static files (CSS, JS, Images)
            template_folder='templates')  # Folder for HTML templates

# Get the MongoDB Atlas connection string from the environment variable
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# Enable Cross-Origin Resource Sharing (CORS) for all domains on all routes
CORS(app)

# Initialize PyMongo
try:
    mongo = PyMongo(app)
    # Access the specific collection we need
    # Access the correct database and collection
    eshop_db = mongo.cx["Eshop"]  # Explicitly get the database
    eshop_collection = eshop_db["products"]  # Now get the 'products' collection

    print("MongoDB connection successful.")
    # Test connection with a simple count
    print(f"Found {eshop_collection.count_documents({})} documents in 'eshop' collection.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    mongo = None # Set mongo to None if connection fails
    eshop_collection = None

# --- Helper Function ---
def serialize_doc(doc):
    """ Converts MongoDB document (including ObjectId) to JSON-serializable format. """
    doc['_id'] = str(doc['_id']) # Convert ObjectId to string
    return doc

# --- Static Page Routes ---
@app.route('/')
def home():
    """ Renders the homepage. """
    return render_template('homepage.html')

@app.route('/products')
def products_page():
    """ Renders the products page. """
    return render_template('products.html')

# --- API Endpoints ---

@app.route('/search', methods=['GET'])
def search_products():
    """
    Searches products by name (partial or full match, case-insensitive).
    Supports sorting by name (ascending).
    Query Parameter: ?query=<search_term>
    """
    if  eshop_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    search_query = request.args.get('query', '') # Get search term from query params

    try:
        # Use regex for case-insensitive partial matching
        # If search_query is empty, match all products
        if search_query:
            pipeline = [
                {
                    "$match": {
                        "name": {
                            "$regex": f"^{search_query}",
                            "$options": "i"  # case-insensitive
                        }
                    }
                },
                {"$sort": {"price": -1}},
            ]
            products_cursor = eshop_collection.aggregate(pipeline)
        else:
            products_cursor = eshop_collection.find().sort("price", -1)

        # Convert cursor to list and serialize
        products_list = [serialize_doc(product) for product in products_cursor]

        return jsonify(products_list), 200

    except Exception as er:
        print(f"Error during search: {er}")
        return jsonify({"error": "An error occurred during search"}), 500


@app.route('/like', methods=['POST'])
def like_product():
    """
    Increments the 'likes' count for a given product ID.
    Expects JSON body: { "product_id": "<id_string>" }
    """
    if  eshop_collection is  None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        data = request.get_json()
        if not data or 'product_id' not in data:
            return jsonify({"error": "Missing 'product_id' in request body"}), 400

        product_id_str = data['product_id']

        # Validate and convert string ID to ObjectId
        try:
            product_oid = ObjectId(product_id_str)
        except Exception:
            return jsonify({"error": "Invalid product ID format"}), 400

        # Find the product and increment its likes count using $inc
        result = eshop_collection.update_one(
            {"_id": product_oid},
            {"$inc": {"likes": 1}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Product not found"}), 404

        if result.modified_count == 1:
            # Fetch the updated document to return the new like count (optional)
            updated_product = eshop_collection.find_one({"_id": product_oid})
            return jsonify({
                "message": "Like registered successfully",
                "product_id": product_id_str,
                "new_likes": updated_product.get('likes', 'N/A')
            }), 200
        else:
             # This might happen if the like value wasn't updated for some reason
             return jsonify({"message": "Like registered but count not modified (already liked?)"}), 200

    except Exception as er:
        print(f"Error liking product: {er}")
        return jsonify({"error": "An error occurred while liking the product"}), 500


@app.route('/popular-products', methods=['GET'])
def get_popular_products():
    """ Returns the top 5 products sorted by 'likes' descending. """
    if  eshop_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Find top 5 products, sorted by likes descending
        popular_products_cursor = eshop_collection.find().sort("likes", -1).limit(5)

        # Convert cursor to list and serialize
        popular_products_list = [serialize_doc(product) for product in popular_products_cursor]

        return jsonify(popular_products_list), 200

    except Exception as er:
        print(f"Error fetching popular products: {er}")
        return jsonify({"error": "An error occurred fetching popular products"}), 500


# --- Run Application ---
if __name__ == '__main__':
    # Use environment variable for port, default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Run in debug mode for development (auto-reloads changes)
    # Set debug=False for production
    app.run(debug=True, port=port)


