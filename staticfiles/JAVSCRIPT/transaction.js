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
        const orderDate = new Date().toISOString();
        const description = buildDescriptionFromSummary();
        const size = 'Mixed'; // Adjust this as necessary
        const quantity = getTotalQuantityFromSummary();

        const transactionData = {
            ubtransact_id: ubtransactId,
            order_date: orderDate,
            description: description,
            size: size,
            quantity: quantity,
            total_price: totalPrice,
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
