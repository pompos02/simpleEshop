# FurnitureShop: Project Development Summary

## 1. Introduction: The Vision

This document outlines the development process of the FurnitureShop web application. Our goal was to build a simple yet functional e-commerce platform showcasing furniture products. Users should be able to browse items, search for specific products by name, and express interest by "liking" them. We aimed to create a standard client-server application using Python/Flask for the backend, MongoDB for the database, and HTML/CSS/JavaScript for the frontend.

## 2. Phase 1: Laying the Groundwork (Backend & Database)

Every application needs a solid foundation. We started by setting up the backend structure and the database.

* **Project Structure:** We established a standard Flask project layout:
    * `app.py`: The central hub for our backend logic.
    * `static/`: To hold our CSS and JavaScript files.
    * `templates/`: To store our HTML page structures.
    * `requirements.txt`: To list necessary Python packages.
    * `.env`: To securely store our database connection string (kept out of version control).

* **Technology Choices:**
    * **Flask:** Chosen for its simplicity and flexibility as a Python web framework.
    * **MongoDB Atlas:** Selected for its ease of use as a cloud-hosted NoSQL database, suitable for flexible product data.

* **Database Setup (Atlas):**
    1.  We created a free cluster on MongoDB Atlas.
    2.  Set up a database user with read/write permissions.
    3.  Configured network access rules to allow connections from our development environment.
    4.  Obtained the vital **Connection String** (`mongodb+srv://...`).

* **Connecting Flask to MongoDB:**
    1.  Installed `Flask-PyMongo` and `python-dotenv`.
    2.  Stored the Atlas connection string in the `.env` file as `MONGO_URI`.
    3.  In `app.py`, we used `python-dotenv` to load the `MONGO_URI` and configured `Flask-PyMongo` to manage the connection:
        ```python
        from dotenv import load_dotenv
        from flask_pymongo import PyMongo

        load_dotenv() # Load MONGO_URI from .env
        app.config["MONGO_URI"] = os.getenv("MONGO_URI")
        mongo = PyMongo(app) # Initialize connection manager
        ```
    4.  We decided on a database named `Eshop` and a collection named `products` within it, explicitly selecting them in `app.py`:
        ```python
        eshop_db = mongo.cx["Eshop"]
        eshop_collection = eshop_db["products"]
        ```

* **Defining Our Data (Schema):** We established the structure for documents in the `products` collection:
    ```json
    {
      "name": "String",
      "image": "String (URL)",
      "description": "String",
      "price": Double,
      "likes": Int // Starts at 0
    }
    ```

## 3. Phase 2: Building the API (Backend Logic in `app.py`)

With the database connection established, we built the API endpoints that the frontend would use to interact with the data.

* **Flask Routing:** We used Flask's `@app.route('/path')` decorator to map URL paths to specific Python functions that handle requests.

* **API Endpoints Explained:**
    * **`GET /popular-products`:**
        * **Goal:** Fetch the top 5 most liked products for the homepage slideshow.
        * **How:** Queries the `products` collection using `find()`, sorts the results by the `likes` field in descending order (`sort("likes", -1)`), and limits the result set to 5 documents (`limit(5)`).
    * **`GET /search`:**
        - **Goal:**  
  Allow searching for products by name, supporting autocomplete and fuzzy matching.

      - **How it works:**
        - Reads the `query` parameter from the URL using `request.args.get('query')`.
        - If a query is provided:
          - Performs an **autocomplete search** on the `name` field using **MongoDB Atlas Search**.
          - The search is **case-insensitive** and supports **fuzzy matching** (to tolerate minor typos).
          - This functionality is enabled by a **MongoDB Atlas Search index** with the following definition:
            ```json
            {
              "mappings": {
                "dynamic": false,
                "fields": {
                  "name": {
                    "type": "autocomplete"
                  }
                }
              }
            }
            ```
        - If no query is provided:
          - Fetches **all products** from the collection.
        - In both cases, results are sorted by **price in descending order**.
        - Returns a JSON array of matching products.
      * **`POST /like`:**
          * **Goal:** Increment the like count for a specific product.
          * **How:** Expects a JSON body containing `{ "product_id": "..." }`. It parses this JSON (`request.get_json()`), converts the string ID to a MongoDB `ObjectId`, and then uses `update_one` with MongoDB's **`$inc` operator** (`{"$inc": {"likes": 1}}`). This atomically increases the `likes` count by 1 for the matching product, ensuring data integrity even with concurrent requests. It then fetches the updated product to return the new like count.

* **JSON Responses & ObjectIds:** Since the frontend expects JSON data, we used Flask's `jsonify` function to convert our Python dictionaries/lists into JSON responses. We also created a `serialize_doc` helper function to convert the non-JSON-serializable MongoDB `ObjectId` type into a simple string before sending it in the response.

* **CORS:** We enabled Cross-Origin Resource Sharing using `Flask-Cors` (`CORS(app)`) so that JavaScript running on the frontend (served by Flask, but technically the browser treats it as potentially different origin) could make requests to our API endpoints.

## 4. Phase 3: Crafting the User Interface (HTML & CSS)

Next, we built the visual structure and appearance of the application.

* **HTML Templates (`templates/`):**
    * `homepage.html`: Created the basic HTML structure, including a placeholder `div` with `id="slideshow"` for the dynamic content.
    * `products.html`: Set up the structure with an `input` (`id="search-bar"`), a `button` (`id="search-button"`), and a `div` (`id="product-list"`) to display search results.
    * Both templates include standard header/footer elements.

* **Styling (`static/css/style.css`):**
    * We wrote CSS rules to define the layout (using techniques like Flexbox or Grid), typography, colors, and overall look and feel of the application, ensuring a consistent presentation across both pages.

## 5. Phase 4: Bringing it to Life (Frontend JavaScript - `products.js`)

Static pages aren't interactive. We used JavaScript to connect the frontend UI to the backend API and create a dynamic experience.

* **Single JS File Approach:** We used one file (`products.js`) linked in both HTML pages. Inside the script, we check for the presence of specific element IDs (like `#slideshow` or `#search-bar`) using `document.getElementById`. This tells the script which page it's currently running on, allowing it to execute only the relevant logic. The entire script runs after the HTML is loaded, thanks to the `DOMContentLoaded` event listener.

* **Homepage Slideshow Logic:**
    1.  **Fetch:** On page load (if `#slideshow` exists), an `async` function `fetchPopularProducts` calls `fetch(API_BASE_URL + '/popular-products')`.
    2.  **Display:** Upon receiving the product data, `displaySlideshow` is called. It uses `setInterval` to repeatedly call `showSlide`.
    3.  **Update DOM:** `showSlide` updates the `innerHTML` of the `#slideshow` div with the current product's image, name, price, and likes, cycling through the fetched products.

* **Products Page Logic:**
    1.  **Search Trigger:** Event listeners on the search button (`click`) and input field (`keypress` for Enter) trigger the `searchProducts` function.
    2.  **Search Fetch:** `searchProducts` gets the search term, constructs the URL (e.g., `/search?query=...`), and uses `fetch` to call the `GET /search` API endpoint.
    3.  **Display Results (`displayProducts`):**
        * Clears any previous results from `#product-list`.
        * Loops through the product array received from the API.
        * For each product, it dynamically creates HTML elements (`div`, `img`, `h3`, `p`) and sets their content.
        * **Key:** It stores the product's unique `_id` in a `data-product-id` attribute on the product's image element.
        * Appends the newly created HTML to the `#product-list` div, rendering the results on the page.
    4.  **"Like" Functionality:**
        * **Event Delegation:** A single click listener is attached to the parent `#product-list`.
        * **Target Check:** When a click occurs, it checks if the clicked element (`event.target`) is specifically a product image (`.product-image`).
        * **ID Retrieval:** If it's an image, it reads the `product_id` from the `data-product-id` attribute.
        * **POST Request:** It calls `likeProduct`, which uses `fetch` to send a `POST` request to `/like`, including the `product_id` in the JSON body.
        * **UI Update:** When the backend confirms the like (sending back the `new_likes`), the JavaScript finds the corresponding `.like-count` span on the page and updates its text content, providing instant feedback.

## 6. Docker Setup

The application is containerized using Docker, making it easy to deploy and run in any environment. The Docker setup consists of two main services:

### Docker Architecture

The application uses Docker Compose to orchestrate two services:

1. **Backend Service**: A Flask application that serves both the API and the web interface
2. **MongoDB Service**: A MongoDB database that stores the product data

### Service Details

#### Backend Service
- **Base Image**: Python 3.10 slim
- **Exposed Port**: 5000
- **Dependencies**: Requires the MongoDB service to be running
- **Volumes**:
  - `./backend:/app`: Mounts the backend directory to the container for development
  - `./web:/app/web`: Mounts the web directory to the container for serving static files and templates
- **Environment Variables**:
  - `MONGO_URI`: Connection string for MongoDB

#### MongoDB Service
- **Base Image**: Latest MongoDB image
- **Exposed Port**: 27017
- **Volumes**:
  - `mongo_data:/data/db`: Persistent volume for database data
- **Environment Variables**:
  - `MONGO_INITDB_ROOT_USERNAME`: Root username for MongoDB
  - `MONGO_INITDB_ROOT_PASSWORD`: Root password for MongoDB
- **Initialization**: Uses the `init.js` script to create the database, collections, and insert sample data

### Running the Application with Docker

1. **Prerequisites**:
   - Docker and Docker Compose installed on your system
   - `.env` file with the required environment variables:
     ```
     MONGO_URI=mongodb://admin:adminpassword@mongodb:27017/Eshop?authSource=admin
     MONGO_ROOT_USER=admin
     MONGO_ROOT_PASSWORD=adminpassword
     ```

2. **Build and Start the Containers**:
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**:
   - Web Interface: http://localhost:5000
   - API Endpoints:
     - GET http://localhost:5000/popular-products
     - GET http://localhost:5000/search?query=your_search_term
     - POST http://localhost:5000/like (with JSON body: `{"product_id": "..."}`)

4. **Stop the Containers**:
   ```bash
   docker-compose down
   ```

### Development with Docker

For development purposes, the Docker setup includes volume mounts that allow you to make changes to the code without rebuilding the containers. When you modify files in the `backend` or `web` directories, the changes will be reflected in the running application.

## 7. Conclusion

Through these phases, we successfully built the FurnitureShop application. This involved setting up a Flask backend, connecting to a MongoDB database, creating a RESTful API, structuring the HTML frontend, styling with CSS, and implementing dynamic user interactions with JavaScript's `fetch` API and DOM manipulation. The project serves as a practical demonstration of integrating these common web technologies and containerizing the application with Docker.

---
