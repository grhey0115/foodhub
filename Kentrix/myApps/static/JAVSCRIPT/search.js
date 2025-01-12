    const searchInput = document.getElementById('item-search');
    const searchBtn = document.getElementById('search-btn');
    const itemInfoFormGroup = document.querySelectorAll('.item-info .form-group');
    const supplierInfoFormGroup = document.querySelectorAll('.supplier-info .form-group');

    searchBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const searchTerm = searchInput.value.trim();
        if (searchTerm) {
            // Make an AJAX request to your Django view to search for the item
            fetch('/search_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ search_term: searchTerm })
            })
            .then(response => response.json())
            .then(data => {
                if (data.item_found) {
                    // Update the form groups with the search result
                    itemInfoFormGroup.forEach((formGroup) => {
                        const label = formGroup.querySelector('label');
                        const input = formGroup.querySelector('input');
                        if (label.textContent === 'Item Name') {
                            input.value = data.item_name;
                        }
                    });
                    supplierInfoFormGroup.forEach((formGroup) => {
                        const label = formGroup.querySelector('label');
                        const input = formGroup.querySelector('input');
                        if (label.textContent === 'Supplier Name') {
                            input.value = data.supplier_name;
                        }
                    });
                } else {
                    // Show an error message if the item is not found
                    alert('Item not found');
                }
            })
            .catch(error => console.error(error));
        }
    });
