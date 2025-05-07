document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the homepage with slideshow
    const slideshowEl = document.getElementById('slideshow');
    if (slideshowEl) {
        loadPopularProducts();
    }

    // Check if we're on the products page with search
    const searchButton = document.getElementById('search-button');
    const searchBar = document.getElementById('search-bar');
    if (searchButton && searchBar) {
        // Load all products initially on products page
        loadProducts('');

        // Set up search functionality
        searchButton.addEventListener('click', function() {
            const searchTerm = searchBar.value.trim();
            loadProducts(searchTerm);
        });

        // Allow search by pressing Enter
        searchBar.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                const searchTerm = searchBar.value.trim();
                loadProducts(searchTerm);
            }
        });
    }
});

// Function to load popular products for homepage slideshow
function loadPopularProducts() {
    const slideshowEl = document.getElementById('slideshow');

    // Fetch popular products from the API
    fetch('/popular-products')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(products => {
            if (products.length === 0) {
                slideshowEl.innerHTML = '<p>No popular products found.</p>';
                return;
            }


            // Create slideshow content
            let currentSlide = 0;
            const showSlide = (index) => {
                // Create slide HTML
                const product = products[index];
                slideshowEl.innerHTML = `
                    <div class="slide">
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p class="price">${product.price.toFixed(2)}€</p>
                        <p><i class="fas fa-heart" style="color: #FF8C00;"></i> ${product.likes || 0} likes</p>
                    </div>
                `;
            };

            // Show first slide
            showSlide(currentSlide);

            // Automatic slideshow
            setInterval(() => {
                currentSlide = (currentSlide + 1) % products.length;
                showSlide(currentSlide);
            }, 3000); // Change slide every 3 seconds
        })
        .catch(error => {
            console.error('Error fetching popular products:', error);
            slideshowEl.innerHTML = '<p>Error loading popular products. Please try again later.</p>';
        });
}


function loadProducts(searchTerm) {
    const productListEl = document.getElementById('product-list');

    const searchUrl = searchTerm ? `/search?query=${searchTerm}` : '/search';

    // Fetch products from the API
    fetch(searchUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(products => {
            if (products.length === 0) {
                productListEl.innerHTML = '<p>No products found. Try a different search term.</p>';
                return;
            }

            // Clear product list
            productListEl.innerHTML = '';

            // Add each product to the list
            products.forEach(product => {
                const productEl = document.createElement('div');
                productEl.className = 'product-item';
                productEl.innerHTML = `
                    <img src="${product.image}" alt="${product.name}" 
                         data-product-id="${product._id}">
                    <h3>${product.name}</h3>
                    <p>${product.description || 'No description available'}</p>
                    <p class="price">${product.price.toFixed(2)}€</p>
                    <p class="likes">
                        <i class="fas fa-heart like-icon"></i> <span class="like-count">${product.likes || 'No likes found'}</span> likes
                    </p>
                `;

                // Add click event for liking a product
                const productImg = productEl.querySelector('img');
                productImg.addEventListener('click', function() {
                    likeProduct(product._id, productEl);
                });

                productListEl.appendChild(productEl);
            });
        })
        .catch(error => {
            console.error('Error fetching products:', error);
            productListEl.innerHTML = '<p>Error loading products. Please try again later.</p>';
        });
}


function likeProduct(productId, productEl) {
    fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Update like count in the UI
        const likeCountEl = productEl.querySelector('.like-count');
        if (likeCountEl && data.new_likes) {
            likeCountEl.textContent = data.new_likes;

            // animation for feedback
            productEl.querySelector('.like-icon').style.transform = 'scale(1.5)';
            setTimeout(() => {
                productEl.querySelector('.like-icon').style.transform = 'scale(1)';
            }, 300);
        }
    })
    .catch(error => {
        console.error('Error liking product:', error);
    });
}