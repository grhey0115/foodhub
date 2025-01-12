const prices = {
    "Mango Banana": { "M": 89, "L": 110 },
    "Mango Cheesecake": { "M": 115, "L": 135 },
    "Mango Nutella": { "M": 110, "L": 125 },
    "Mango Avalanche": { "M": 115, "L": 135 },
    "Mango Yakult": { "M": 89, "L": 110 },
    "Mango Graham": { "M": 89, "L": 99 },
    "Knickerbocker Glory": { "M": 115, "L": 135 },
    "Banana Nutella": { "M": 89, "L": 110 }
};

function incrementQuantity() {
    const quantityInput = document.getElementById("quantity");
    quantityInput.value = parseInt(quantityInput.value) + 1;
    calculateTotalPrice();
}

function decrementQuantity() {
    const quantityInput = document.getElementById("quantity");
    if (quantityInput.value > 0) {
        quantityInput.value = parseInt(quantityInput.value) - 1;
        calculateTotalPrice();
    }
}

function calculateTotalPrice() {
    const quantity = parseInt(document.getElementById('quantity').value);
    const size = document.getElementById('size').value;
    const desc = document.getElementById('desc').value;

    const pricePerItem = prices[desc][size];
    const totalPrice = quantity * pricePerItem;

    return totalPrice;
}

function updateSummaryTotal() {
    let total = 0;
    document.querySelectorAll('#summary-list li').forEach(item => {
        total += parseFloat(item.getAttribute('data-total'));
    });
    document.getElementById("summary-totalprice").value = `₱${total.toFixed(2)}`;
}

function calculateChange() {
    const paymentInput = document.getElementById("summary-payment");
    const totalPriceInput = document.getElementById("summary-totalprice");

    const paymentAmount = parseFloat(paymentInput.value.replace(/₱/g, '').trim());
    const totalPrice = parseFloat(totalPriceInput.value.replace(/₱/g, '').trim());

    if (isNaN(paymentAmount) || isNaN(totalPrice)) {
        document.getElementById("summary-change").value = '₱0.00';
        return;
    }

    const change = paymentAmount - totalPrice;

    if (change >= 0) {
        document.getElementById("summary-change").value = `₱${change.toFixed(2)}`;
    } else {
        document.getElementById("summary-change").value = 'Insufficient payment';
    }
}

function addToSummary() {
    const desc = document.getElementById('desc').value;
    const size = document.getElementById('size').value;
    const quantity = parseInt(document.getElementById('quantity').value);


    if (quantity > 0) {
        const totalPrice = calculateTotalPrice();

        const summaryItem = document.createElement('li');
        summaryItem.innerHTML = `${quantity} x ${desc} (${size}) - ₱${totalPrice.toFixed(2)} `;
        summaryItem.setAttribute('data-total', totalPrice);
        summaryItem.classList.add('summary-item');
        
      
        // Set dataset properties
        summaryItem.dataset.quantity = quantity;
        summaryItem.dataset.description = desc;
        summaryItem.dataset.size = size;
        summaryItem.dataset.price = totalPrice;

        const deleteButton = document.createElement('DELETE');
        deleteButton.className = 'delete-item';
        deleteButton.textContent = 'X';
        summaryItem.appendChild(deleteButton);

        document.getElementById('summary-list').appendChild(summaryItem);

        updateSummaryTotal(); // Update the running total with the new item
        clearFormFields();
    } else {
        alert("Please enter a valid quantity.");
    }
}

function clearFormFields() {
    document.getElementById("quantity").value = 0;
    document.getElementById("desc").value = "Mango Banana";
    document.getElementById("size").value = "M";
    calculateTotalPrice(); // Reset the total price to ₱0.00
}

function updateDateTime() {
    const now = new Date();
    const formattedDate = now.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
    const formattedTime = now.toLocaleTimeString("en-US",   
   {
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    });
    document.getElementById("date-time").value = `${formattedDate} ${formattedTime}`;
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    document.getElementById('ubtransactid').value = generateUniqueID();
    document.getElementById('increment').addEventListener('click', incrementQuantity);
    document.getElementById('decrement').addEventListener('click', decrementQuantity);
    document.getElementById('add-to-summary').addEventListener('click', addToSummary);
    document.getElementById('pay-summary').addEventListener('click', paySummary);
    document.getElementById('summary-payment').addEventListener('input', calculateChange);
    document.getElementById('print-summary').addEventListener('click', printReceipt);
    document.getElementById("logout-link").addEventListener("click", confirmLogout);

    document.getElementById('summary-list').addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-item')) {
            event.target.parentNode.remove();
            updateSummaryTotal();
        }
    });
});

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

        const transaction = {
            ubtransactId: document.getElementById('ubtransactid').value,
            orderDate: new Date().toISOString(),
            description: buildDescriptionFromSummary(),
            size: 'Mixed',
            quantity: getTotalQuantityFromSummary(),
            totalPrice: totalPrice
        };

        sendTransactionToBackend(transaction);
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
            alert("Transaction saved successfully!");
        } else {
            alert("Failed to save transaction.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
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

function buildDescriptionFromSummary() {
    const summaryItems = document.querySelectorAll('#summary-list li');
    return Array.from(summaryItems).map(item => `${item.dataset.quantity}x ${item.dataset.description} (${item.dataset.size})`).join(', ');
}

function getTotalQuantityFromSummary() {
    const summaryItems = document.querySelectorAll('#summary-list li');
    return Array.from(summaryItems).reduce((total, item) => total + parseInt(item.dataset.quantity), 0);
}

function printReceipt() {
    const now = new Date();
    const date = now.toLocaleDateString();
    const time = now.toLocaleTimeString();
    const ubtransactid = document.getElementById("ubtransactid")?.value || "";
    const payment = document.getElementById("summary-payment")?.value || "";
    const change = document.getElementById("summary-change")?.value || "";
    const totalPrice = document.getElementById("summary-totalprice")?.value || "";
    
    const orderSummaryItems = document.getElementById("summary-list").children;
    let itemsHTML = `<tr><th>Item</th><th>Size</th><th>Quantity</th><th>Price</th></tr>`;
    
    Array.from(orderSummaryItems).forEach(item => {
      const quantity = item.dataset.quantity;
      const description = item.dataset.description;
      const size = item.dataset.size;
      const price = item.dataset.price;
    
      itemsHTML += `<tr>
        <td>${description}</td>
        <td>${size}</td>
        <td>${quantity}</td>
        <td>₱${price}</td>
      </tr>`;
    });
    
    const receiptContent = `
      <style>
        /* Add these styles to your main stylesheet */

.receipt {
  font-family: monospace; /* Similar to 7/11 receipt font */
  width: 300px; /* Adjust width as needed */
  margin: 0 auto; /* Center the receipt */
}

.header {
  text-align: center;
  margin-bottom: 10px;
}

.itemized-table,
.order-summary table {
  border-collapse: collapse;
  width: 100%;
}

.itemized-table,
.order-summary table,
th,
td {
  border: 1px solid #ddd;
  padding: 5px;
  text-align: left;
}

.total-row {
  font-weight: bold;
  margin top: 10px;
}

.footer {
  text-align: center;
  margin-top: 10px;
}

      </style>
      <div class="receipt">
      <div class="header">
        <h2>I/O Food Hub</h2>
        <p>Seawall Area, Poblacion, Dalaguete</p>
        <p>City, Philippines</p>
        <p>Tel: (123) 456-7890</p>
      </div>
      <table class="itemized-table">
        <tr><th>Date</th><td>${date}</td></tr>
        <tr><th>Time</th><td>${time}</td></tr>
        <tr><th>UBTransactID</th><td>${ubtransactid}</td></tr>
      </table>
      <div class="order-summary">
        <h3>Order Summary</h3>
        <table>${itemsHTML}</table>
      </div>
      <table>
        <tr class="total-row"><td>Total Price</td><td>${totalPrice}</td></tr>
        <tr><td>Payment</td><td>${payment}</td></tr>
        <tr><td>Change</td><td>${change}</td></tr>
      </table>
      <div class="footer">
        <p>Thank you for shopping with us!</p>
        <p>Have a great day!</p>
      </div>
      </div>
    `;
    
    const printWindow = window.open("", "", "height=500,width=300");
    printWindow.document.write(receiptContent);
    printWindow.document.close();
    printWindow.print();    
}
  


function confirmLogout() {
    if (confirm("Are you sure you want to log out?")) {
        window.location.href = "{% url 'log_in' %}";
    } else {
        return false;
    }
}


