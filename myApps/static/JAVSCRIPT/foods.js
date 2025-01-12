// Confirm deletion of a product
function confirmDeleteProduct(productId) {
    Swal.fire({
        title: 'Are you sure?',
        text: "This action cannot be undone!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
    }).then((result) => {
        if (result.isConfirmed) {
            deleteProduct(productId);
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const showProductsButton = document.getElementById('show-products-button');
    const showItemsButton = document.getElementById('show-items-button');
    const productsSection = document.getElementById('products-section');
    const itemsSection = document.getElementById('items-section');

    showProductsButton.addEventListener('click', () => {
        productsSection.style.display = 'block';
        itemsSection.style.display = 'none';
    });

    showItemsButton.addEventListener('click', () => {
        itemsSection.style.display = 'block';
        productsSection.style.display = 'none';
    });

    // Initially display the Items section and hide the Products section
    itemsSection.style.display = 'block';
    productsSection.style.display = 'none';
});

let products = [];
let editingIndex = -1;

function adjustQuantity(amount) {
    const quantityInput = document.getElementById('productQuantity');
    const currentValue = parseInt(quantityInput.value) || 0;
    const newValue = Math.max(currentValue + amount, 0);
    quantityInput.value = newValue;
}

function clearFormFields() {
    document.getElementById('productName').value = 'Coffee';
    document.getElementById('productCategory').value = 'Beverage';
    document.getElementById('productPrice').value = '';
    document.getElementById('productQuantity').value = '0';
    editingIndex = -1;
    document.getElementById('formTitle').textContent = 'Add Product';
}

function saveProduct() {
    const name = document.getElementById('productName').value;
    const category = document.getElementById('productCategory').value;
    const price = parseFloat(document.getElementById('productPrice').value);
    const quantity = parseInt(document.getElementById('productQuantity').value);

    if (!name || !category || isNaN(price) || isNaN(quantity) || price < 0) {
        Swal.fire({
            icon: 'error',
            title: 'Invalid Input',
            text: 'Please ensure all fields are filled out correctly. Price must be a non-negative number.'
        });
        return;
    }

    if (editingIndex === -1) {
        products.push({ name, category, price, quantity });
        Swal.fire({
            icon: 'success',
            title: 'Product Added',
            text: `${name} has been added successfully.`
        });
    } else {
        products[editingIndex] = { name, category, price, quantity };
        Swal.fire({
            icon: 'success',
            title: 'Product Updated',
            text: `${name} has been updated successfully.`
        });
        editingIndex = -1;
    }

    clearFormFields();
    renderProducts();
}

function renderProducts() {
    const tbody = document.getElementById('productTable').querySelector('tbody');
    tbody.innerHTML = '';

    products.forEach((product, index) => {
        const row = document.createElement('tr');
        const dangerClass = product.quantity < 10 ? 'danger' : '';

        row.innerHTML = `
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${product.price.toFixed(2)}</td>
            <td class="${dangerClass}">
                ${product.quantity}
                ${product.quantity < 10 ? '<span class="danger-icon">⚠️</span>' : ''}
            </td>
            <td>
                <button class="btn" onclick="editProduct(${index})">Edit</button>
                <button class="btn" onclick="deleteProduct(${index})" style="background-color: red;">Delete</button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

function editProduct(index) {
    editingIndex = index;
    const product = products[index];

    document.getElementById('formTitle').textContent = 'Edit Product';
    document.getElementById('productName').value = product.name;
    document.getElementById('productCategory').value = product.category;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productQuantity').value = product.quantity;
}

function deleteProduct(index) {
    const product = products[index];
    products.splice(index, 1);
    renderProducts();
    Swal.fire({
        icon: 'success',
        title: 'Product Deleted',
        text: `${product.name} has been deleted successfully.`
    });
}


// Simulate product deletion
function deleteProduct(productId) {
    setTimeout(() => {
        const productRow = document.getElementById(`product-row-${productId}`);
        if (productRow) {
            productRow.remove();
            Swal.fire({
                title: 'Deleted!',
                text: 'The product has been deleted successfully.',
                icon: 'success',
            });
        } else {
            console.error(`Product row with ID 'product-row-${productId}' not found.`);
        }
    }, 500);
}



// Confirm deletion of a supplier item


// Add food item logic
document.getElementById('add-item-button').addEventListener('click', function (e) {
    e.preventDefault();
    const form = document.getElementById('add-food-item-form');
    if (!form) {
        console.error('Form not found');
        return;
    }
    Swal.fire({
        title: 'Are you sure?',
        text: "Do you want to add this food item?",
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, add it!',
        cancelButtonText: 'No, cancel',
    }).then((result) => {
        if (result.isConfirmed) {
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            title: 'Success!',
                            text: 'Food item has been added successfully.',
                            icon: 'success',
                        });
                        const tableBody = document.querySelector('table tbody');
                        const newRow = document.createElement('tr');
                        newRow.innerHTML = `
                            <td>${data.item_id}</td>
                            <td>${data.item_name}</td>
                            <td>${data.category}</td>
                            <td>${data.stock_quantity}</td>
                            <td>${data.reorder_level}</td>
                            <td>${data.batch_number}</td>
                            <td>${data.expiry_date || 'N/A'}</td>
                            <td>${data.arrival_date}</td>
                            <td>${data.cost_price}</td>
                            <td>${data.selling_price}</td>
                            <td>${data.stall_location}</td>
                            <td>${data.date_created}</td>
                            <td>
                                <a href="edit_food_item/${data.item_id}">Edit</a> |
                                <a href="javascript:void(0);" onclick="confirmDeleteFoodItem(${data.item_id});">Delete</a>
                            </td>
                        `;
                        tableBody.insertBefore(newRow, tableBody.firstChild);
                    } else {
                        Swal.fire({
                            title: 'Error!',
                            text: data.error || 'An error occurred.',
                            icon: 'error',
                        });
                    }
                })
                .catch(error => {
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to add food item.',
                        icon: 'error',
                    });
                });
        }
    });
});
