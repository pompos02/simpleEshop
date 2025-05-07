import os
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

app = Flask(__name__,
            static_folder='web/static',  # Folder for static files (css, images, js)
            template_folder='web/templates')  # Folder for html templates

app.config["MONGO_URI"] = os.getenv("MONGO_URI")


CORS(app)

try:
    mongo = PyMongo(app)
    eshop_db = mongo.cx["Eshop"]  # Get the db
    eshop_collection = eshop_db["products"]  # Get the 'products' collection

    # Debugging prints
    print("MongoDB connection successful.")
    print(f"Found {eshop_collection.count_documents({})} documents in 'products' collection.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    mongo = None
    eshop_collection = None

def serialize_doc(doc):
    doc['_id'] = str(doc['_id']) # id of type Object_ID converted to str so the doc can be json-formatted
    return doc


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/products')
def products_page():
    return render_template('products.html')


@app.route('/search', methods=['GET'])
def search_products():
    if eshop_collection is None:
        return jsonify({"error": "Database connection failed"})

    search_query = request.args.get('query', '')

    try:
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
            products_cursor = eshop_collection.find().sort("price", -1) # If search_query is empty, match all products

        products_list = [serialize_doc(product) for product in products_cursor]  # Convert cursor to list and serialize

        return jsonify(products_list)

    except Exception as er:
        print(f"Error during search: {er}")
        return jsonify({"error": "An error occurred during search"})


@app.route('/like', methods=['POST'])
def like_product():
    if eshop_collection is  None:
        return jsonify({"error": "Database connection failed"})

    try:
        data = request.get_json()
        if not data or 'product_id' not in data:
            return jsonify({"error": "Missing 'product_id' in request body"})

        product_id_str = data['product_id']

        try:
            product_oid = ObjectId(product_id_str)  # convert string id to ObjectId
        except Exception:
            return jsonify({"error": "Invalid product ID format"})

        # Find the product and increment its likes count by 1
        result = eshop_collection.update_one(
            {"_id": product_oid},
            {"$inc": {"likes": 1}}
        )


        if result.modified_count == 1:
            # Fetch the updated document to return the new like count
            updated_product = eshop_collection.find_one({"_id": product_oid})
            return jsonify({
                "product_id": product_id_str,
                "new_likes": updated_product.get('likes', 'N/A')
            })


    except Exception as er:
        print(f"Error liking product: {er}")
        return jsonify({"error": "An error occurred while liking the product"})


@app.route('/popular-products', methods=['GET'])
def get_popular_products():
    if eshop_collection is None:
        return jsonify({"error": "Database connection failed"})

    try:
        # Find the top 5 products, sorted by likes descending
        popular_products_cursor = eshop_collection.find().sort("likes", -1).limit(5)

        # Convert cursor to list and serialize
        popular_products_list = [serialize_doc(product) for product in popular_products_cursor]

        return jsonify(popular_products_list)

    except Exception as er:
        print(f"Error fetching popular products: {er}")
        return jsonify({"error": "An error occurred fetching popular products"})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)