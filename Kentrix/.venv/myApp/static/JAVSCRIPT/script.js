
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
      }
      calculateTotalPrice();
    }
    
    function calculateTotalPrice() {
      const quantity = parseInt(document.getElementById('quantity').value);
      const size = document.getElementById('size').value;
      const desc = document.getElementById('desc').value;
  
      const pricePerItem = prices[desc][size];
      const totalPrice = quantity * pricePerItem;
  
      return totalPrice;
  }
  function updateSummaryTotal(amount) {
    const totalField = document.getElementById("summary-totalprice");
    const currentTotal = parseFloat(totalField.value.replace('₱', '').trim());
    const newTotal = currentTotal + amount;
    totalField.value = `₱${newTotal.toFixed(2)}`;
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

      const deleteButton = document.createElement('button');
      deleteButton.className = 'delete-item';
      deleteButton.textContent = 'DELETE ITEM';
      summaryItem.appendChild(deleteButton);

      document.getElementById('summary-list').appendChild(summaryItem);

      updateSummaryTotal(totalPrice); // Update the running total with the new item
      clearFormFields();
  } else {
      alert("Please enter a valid quantity.");
  }
}

  function updateSummaryTotal() {
    let total = 0;
    document.querySelectorAll('#summary-list li').forEach(item => {
      total += parseFloat(item.getAttribute('data-total'));
    });
    document.getElementById('summary-total-value').textContent = total.toFixed(2);
    document.getElementById("summary-totalprice").value = `₱${total.toFixed(2)}`;
  }
    
  function submitOrder() {
    if (confirm("Are you sure you want to submit this order?")) {
      alert("Order submitted successfully!");
      clearFormFields();
      document.getElementById("summary-list").innerHTML = '';
      document.getElementById("summary-total-value").textContent = "0.00";
      document.getElementById("summary-totalprice").value = "₱0.00";
      document.getElementById("summary-payment").value = "₱";
      document.getElementById("summary-change").value = "₱0.00";
    } else {
      alert("Order submission cancelled.");
    }
  }

  function printReceipt() {
    window.print();
  }

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
    }
  }
    
    function printReceipt() {
      const now = new Date();
      const date = now.toLocaleDateString();
      const time = now.toLocaleTimeString();
      const ubtransactid = document.getElementById("ubtransactid").value;
      const payment = document.getElementById("payment").value;
      const change = document.getElementById("change").value;
      const orderSummaryItems = document.getElementById("summary-list").children;
    
      let itemsHTML = `<tr><th>Item</th><th>Description</th><th>Size</th><th>Quantity</th><th>Price</th></tr>`;
      Array.from(orderSummaryItems).forEach(item => {
        itemsHTML += `<tr><td>${item.textContent}</td></tr>`;
      });
    
      const receiptContent = `
        <style>
          /* Your receipt style here */
        </style>
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
          <tr class="total-row"><td>Total Price</td><td>${document.getElementById("totalprice").value}</td></tr>
          <tr><td>Payment</td><td>${payment}</td></tr>
          <tr><td>Change</td><td>${change}</td></tr>
        </table>
        <div class="footer">
          <p>Thank you for shopping with us!</p>
          <p>Have a great day!</p>
        </div>
      `;
    
      const printWindow = window.open("", "", "height=500,width=300");
      printWindow.document.write(receiptContent);
      printWindow.document.close();
      printWindow.print();
    }
    
    function clearFormFields() {
      document.getElementById("quantity").value = 0;
      document.getElementById("desc").value = "Mango Banana";
      document.getElementById("size").value = "M";
      calculateTotalPrice(); // Reset the total price to ₱0.00
    }
    
    function confirmLogout() {
      if (confirm("Are you sure you want to log out?")) {
        window.location.href = "{% url 'log_in' %}";
      } else {
        return false;
      }
    }
    
    document.getElementById("logout-link").addEventListener("click", confirmLogout);