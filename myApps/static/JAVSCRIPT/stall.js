
// Utility to toggle modal visibility
function toggleModal(modalId, displayState) {
    document.getElementById(modalId).style.display = displayState;
}

// Function to update real-time date and time
function updateDateTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    const day = now.getDate().toString().padStart(2, '0');
    const month = (now.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-based
    const year = now.getFullYear();

    const timeString = `${hours}:${minutes}:${seconds}`;
    const dateString = `${day}/${month}/${year}`;
    document.getElementById("date-time").textContent = `${dateString} | ${timeString}`;
}

// Initialize date and time
updateDateTime();
setInterval(updateDateTime, 1000);

// Toggle sidebar visibility
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Add Stall Alert
function showAddStallAlert(event, form) {
    event.preventDefault();
    Swal.fire({
        title: 'Are you sure?',
        text: "You are about to add a new stall.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, add it!',
        cancelButtonText: 'No, cancel',
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
    }).then((result) => {
        if (result.isConfirmed) {
            form.submit(); // Submit the form
        }
    });
}

// Delete Stall Alert
function showDeleteStallAlert(stallId) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel',
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-stall/${stallId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ stall_id: stallId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    document.getElementById(`stall-row-${stallId}`).remove();
                    Swal.fire('Deleted!', 'The stall has been deleted.', 'success');
                } else {
                    Swal.fire('Error!', 'Failed to delete the stall.', 'error');
                }
            })
            .catch(error => {
                console.error('Error during deletion:', error);
                Swal.fire('Error!', 'An unexpected error occurred.', 'error');
            });
        }
    });
    return false;
}

// Open Update Modal
function toggleModal(modalId, displayState) {
    document.getElementById(modalId).style.display = displayState;
}

function openUpdateModal(id, name, contactNumber, isActive, logoUrl) {
    document.getElementById('update-stall-id').value = id;
    document.getElementById('update-stall-name').value = name;
    document.getElementById('update-stall-contact-number').value = contactNumber;
    document.getElementById('update-stall-status').value = isActive;

    const logoElement = document.getElementById('current-logo');
    if (logoUrl) {
        logoElement.src = logoUrl;
        logoElement.style.display = 'block';
    } else {
        logoElement.style.display = 'none';
    }

    const form = document.getElementById('update-stall-form');
    form.action = `/update-stall/${id}/`;
    toggleModal('update-modal', 'block');
}

document.getElementById('update-stall-form').onsubmit = function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const actionUrl = this.action;

    Swal.fire({
        title: 'Are you sure?',
        text: "You are about to update the stall's information.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, update it!',
        cancelButtonText: 'No, cancel',
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Updated!', 'The stall information has been updated.', 'success');
                    toggleModal('update-modal', 'none');
                    location.reload();
                } else {
                    Swal.fire('Error!', 'Failed to update the stall.', 'error');
                }
            })
            .catch(error => {
                console.error(error);
                Swal.fire('Error!', 'An unexpected error occurred.', 'error');
            });
        }
    });
};
// Close the modal on cancel
function confirmAndAlertCancel() {
    toggleModal('update-modal', 'none');
}