document.addEventListener('DOMContentLoaded', () => {
    function paySummary() {
        const totalPrice = parseFloat(document.getElementById("summary-totalprice").value.replace('₱', ''));
        const payment = parseFloat(document.getElementById("summary-payment").value.replace('₱', ''));

        if (isNaN(payment) || payment < totalPrice) {
            alert("Insufficient payment. Please enter a valid amount.");
            document.getElementById("summary-change").value = "₱0.00";
        } else {
            const change = payment - totalPrice;
            document.getElementById("summary-change").value = `₱${change.toFixed(2)}`;
            alert("Payment successful! Change: ₱" + change.toFixed(2));

            const ubtransactId = document.getElementById('ubtransactid').value;
            const orderDate = getCurrentDateTime();
            const description = buildDescriptionFromSummary();
            const size = 'Mixed';
            const quantity = getTotalQuantityFromSummary();

            const transactionData = {
                ubtransact_id: ubtransactId,
                order_date: orderDate,
                description: description,
                size: size,
                quantity: quantity,
                total_price: totalPrice
            };

            sendTransactionToBackend(transactionData);
        }
    }

    function sendTransactionToBackend(transaction) {
        fetch("{% url 'process_order' %}", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify(transaction),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTransactionTable(data.transaction);
                alert("Transaction saved successfully!");
            } else {
                alert("Failed to save transaction.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    function updateTransactionTable(transaction) {
        const tableBody = document.getElementById("transaction-table-body");
        const newRow = document.createElement("tr");

        newRow.innerHTML = `
            <td>${transaction.ubtransact_id}</td>
            <td>${transaction.order_date}</td>
            <td>${transaction.description}</td>
            <td>${transaction.size}</td>
            <td>${transaction.quantity}</td>
            <td>₱${transaction.total_price.toFixed(2)}</td>
        `;

        tableBody.appendChild(newRow);
    }

    document.getElementById('add-to-summary').addEventListener('click', function(event) {
        event.preventDefault();

        const description = document.getElementById('desc').value;
        const size = document.getElementById('size').value;
        const quantity = parseInt(document.getElementById('quantity').value, 10);
        const totalPrice = calculateTotalPrice(description, size, quantity);

        if (!description || !size || isNaN(quantity) || quantity <= 0) {
            alert('Please fill out all fields with valid data.');
            return;
        }

        updateOrderSummary(description, size, quantity, totalPrice);

        const orderData = {
            ubtransact_id: generateUBTransactID(),
            description: description,
            size: size,
            quantity: quantity,
            total_price: totalPrice
        };

        saveTransaction(orderData);
    });

    const pricingLogic = {
        "Mango Banana": { "M": 89, "L": 110 },
        "Mango Cheesecake": { "M": 115, "L": 135 },
        "Mango Nutella": { "M": 110, "L": 125 },
        "Mango Avalanche": { "M": 115, "L": 135 },
        "Mango Yakult": { "M": 89, "L": 110 },
        "Mango Graham": { "M": 89, "L": 99 },
        "Knickerbocker Glory": { "M": 115, "L": 135 },
        "Banana Nutella": { "M": 89, "L": 110 }
    };

    function calculateTotalPrice(description, size, quantity) {
        const pricePerItem = pricingLogic[description] ? pricingLogic[description][size] : 0;
        return pricePerItem * quantity;
    }

    function updateOrderSummary(description, size, quantity, totalPrice) {
        const summaryList = document.getElementById('summary-list');
        const listItem = document.createElement('li');
        listItem.textContent = `${quantity}x ${description} (${size}) - ₱${totalPrice}`;
        summaryList.appendChild(listItem);

        const totalField = document.getElementById('summary-totalprice');
        const currentTotal = parseFloat(totalField.textContent.replace('₱', '')) || 0;
        const newTotal = currentTotal + totalPrice;
        totalField.textContent = `₱${newTotal.toFixed(2)}`;
    }

    function generateUBTransactID() {
        return 'UBT' + Date.now();
    }

    function saveTransaction(orderData) {
        fetch('/save_transaction/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(orderData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Transaction saved successfully.');
            } else {
                console.error('Failed to save transaction.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getCurrentDateTime() {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
            timeZone: 'Asia/Manila'
        };
    
        return now.toLocaleString('en-CA', options).replace(',', ''); 
    }
});
