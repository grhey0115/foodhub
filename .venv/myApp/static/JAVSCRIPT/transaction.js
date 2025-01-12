const transactionBody = document.getElementById('transaction-body');
const dateTimeDisplay = document.getElementById('current-date-time');
const loadingIndicator = document.getElementById('loading-indicator'); // Assuming an element with id "loading-indicator" exists

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

function populateTransactions() {
    const transactions = JSON.parse(localStorage.getItem('transactions')) || [];

    transactionBody.innerHTML = '';

    if (transactions.length === 0) {
        const noTransactionsRow = document.createElement('tr');
        noTransactionsRow.innerHTML = '<td colspan="6" class="no-transactions">No transactions found</td>';
        transactionBody.appendChild(noTransactionsRow);
    } else {
        transactions.forEach((transaction) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${transaction.ubtransactId}</td>
                <td>${new Date(transaction.orderDate).toLocaleString()}</td>
                <td>${transaction.description}</td>
                <td>${transaction.size}</td>
                <td>${transaction.quantity}</td>
                <td>₱${transaction.totalPrice.toFixed(2)}</td>
            `;
            transactionBody.appendChild(row);
        });
    }

    if (loadingIndicator) {
        loadingIndicator.style.display = 'none'; // Hide loading indicator
    }
}

function storeTransaction(transaction) {
    let transactions = JSON.parse(localStorage.getItem('transactions')) || [];
    transactions.push(transaction);
    localStorage.setItem('transactions', JSON.stringify(transactions));

    populateTransactions(); // Optionally refresh the transactions table if on the same page
}

// Generate a unique ID for the transaction
function generateUniqueID() {
    return 'UB' + Math.floor(Math.random() * 1000000).toString().padStart(6, '0');
}

// Build description from the order summary list
function buildDescriptionFromSummary() {
    const summaryItems = document.getElementById('summary-list').querySelectorAll('li');
    let descriptions = [];
    summaryItems.forEach(item => {
        descriptions.push(`${item.dataset.quantity} x ${item.dataset.description} (${item.dataset.size})`);
    });
    return descriptions.join(', ');
}

// Calculate total quantity from the order summary
function getTotalQuantityFromSummary() {
    const summaryItems = document.getElementById('summary-list').querySelectorAll('li');
    let totalQuantity = 0;
    summaryItems.forEach(item => {
        totalQuantity += parseInt(item.dataset.quantity);
    });
    return totalQuantity;
}

// Call updateDateTime on page load and every second
document.addEventListener('DOMContentLoaded', (event) => {
    populateTransactions();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

// Optional: Function to fetch transactions from the server (if applicable)
function fetchTransactions() {
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block'; // Show loading indicator
    }

    fetch('/transaction/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(transactions => {
            populateTransactions(transactions);
        })
        .catch(error => {
            console.error('Error fetching transactions:', error);
            // Handle error, e.g., display error message to user
        });
}
