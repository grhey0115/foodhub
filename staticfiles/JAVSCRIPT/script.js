document.addEventListener('DOMContentLoaded', () => {
  let orderList = document.getElementById('order-list');
  let subTotalElem = document.getElementById('sub-total');
  let totalPriceElem = document.getElementById('total-price');
  
  let order = [];
  const TAX_RATE = 0.07;

  document.querySelectorAll('.add-item-btn').forEach(btn => {
      btn.addEventListener('click', function() {
          let itemId = this.getAttribute('data-id');
          let itemName = this.previousElementSibling.previousElementSibling.textContent;
          let itemPrice = parseFloat(this.previousElementSibling.textContent.replace('$', ''));

          order.push({ id: itemId, name: itemName, price: itemPrice, quantity: 1 });
          updateOrderSummary();
      });
  });

  function updateOrderSummary() {
      orderList.innerHTML = '';
      let subTotal = 0;

      order.forEach(item => {
          subTotal += item.price;
          orderList.innerHTML += `<li>${item.name} - $${item.price.toFixed(2)}</li>`;
      });

      let tax = subTotal * TAX_RATE;
      let totalPrice = subTotal + tax;

      subTotalElem.textContent = `$${subTotal.toFixed(2)}`;
      totalPriceElem.textContent = `$${totalPrice.toFixed(2)}`;
  }
});

const orderItems = document.getElementById('order-items');
        const subtotalElement = document.getElementById('subtotal');
        const discountElement = document.getElementById('discount');
        const taxElement = document.getElementById('tax');
        const totalElement = document.getElementById('total');
        const cashDisplay = document.getElementById('cash-display');
        const cashInput = document.getElementById('cash-input');
        const payButton = document.getElementById('pay-button');

        let order = [];
        let subtotal = 0;
        let discount = 0;
        let tax = 0;
        let total = 0;

        function updateSummary() {
            subtotalElement.innerText = subtotal.toFixed(2);
            discountElement.innerText = discount.toFixed(2);
            taxElement.innerText = tax.toFixed(2);
            totalElement.innerText = total.toFixed(2);
        }

        function handlePayment() {
            let cashAmount = parseFloat(cashInput.value);
            if (cashAmount >= total) {
                cashDisplay.innerText = cashAmount.toFixed(2);
                alert('Payment successful');
            } else {
                alert('Insufficient cash');
            }
        }

        payButton.addEventListener('click', handlePayment);
