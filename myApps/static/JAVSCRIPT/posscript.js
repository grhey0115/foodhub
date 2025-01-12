function processTransaction() {
    const totalAmount = parseFloat(document.getElementById('total-amount').textContent);
    const paymentAmount = parseFloat(document.getElementById('payment-amount').value);

    if (paymentAmount < totalAmount) {
        alert('Insufficient payment.');
        return;
    }

    const transactionData = { cart, totalAmount, paymentAmount };

    // Send transaction data to the server
    fetch('{% url "process_transaction" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        body: JSON.stringify(transactionData),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Transaction completed successfully!');
                
                // Update Transaction Summary
                displayTransactionSummary(totalAmount, paymentAmount);

                // Reset the cart and payment details
                cart = [];
                updateCartTable();
                document.getElementById('payment-amount').value = '';
                document.getElementById('change-amount').textContent = '0.00';
            } else {
                alert('Error processing transaction: ' + data.error);
            }
        })
        .catch(error => console.error('Error:', error));
}

function displayTransactionSummary(totalAmount, paymentAmount) {
    const summaryTable = document.getElementById('summary-table');
    summaryTable.innerHTML = '';

    let changeAmount = paymentAmount - totalAmount;

    cart.forEach(item => {
        const subtotal = item.price * item.quantity;
        summaryTable.innerHTML += `
            <tr>
                <td>${item.name}</td>
                <td>₱${item.price.toFixed(2)}</td>
                <td>${item.quantity}</td>
                <td>₱${subtotal.toFixed(2)}</td>
            </tr>
        `;
    });

    document.getElementById('summary-total').textContent = totalAmount.toFixed(2);
    document.getElementById('summary-payment').textContent = paymentAmount.toFixed(2);
    document.getElementById('summary-change').textContent = changeAmount.toFixed(2);

    // Show the summary section
    document.getElementById('transaction-summary').style.display = 'block';

    // Hide the cart and payment sections
    document.getElementById('pos-section').style.display = 'none';
}

function clearTransaction() {
    // Reset everything for a new transaction
    document.getElementById('transaction-summary').style.display = 'none';
    document.getElementById('pos-section').style.display = 'block';

    // Reset the cart and payment details
    cart = [];
    updateCartTable();
    document.getElementById('payment-amount').value = '';
    document.getElementById('change-amount').textContent = '0.00';
}
