// Handle per_page changes
document.addEventListener('change', function (evt) {
  if (evt.target.name === 'per_page') {
    // Get current sort parameter from URL if it exists
    const urlParams = new URLSearchParams(window.location.search);
    const sort = urlParams.get('sort');

    // Include sort parameter in refresh if it exists
    let url = '/crud/manifest/';
    if (sort) {
      url += `?sort=${sort}`;
    }

    htmx.ajax('GET', url, {
      target: '#manifest-table',
      swap: 'innerHTML',
      include: '[name="per_page"]'
    });
  }
});

// Clear error messages when form is submitted
document.addEventListener('htmx:beforeRequest', function (evt) {
  const form = evt.detail.elt.closest('form');
  if (form) {
    // Include sort parameter if it exists
    const urlParams = new URLSearchParams(window.location.search);
    const sort = urlParams.get('sort');
    if (sort) {
      evt.detail.parameters['sort'] = sort;
    }

    // Clear any existing error messages
    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach(el => el.remove());

    // Clear field-specific error styling
    const errorFields = form.querySelectorAll('.error-field');
    errorFields.forEach(field => {
      field.classList.remove('error-field', 'border-red-500');
    });
  }
});

// Handle validation errors
document.addEventListener('htmx:beforeSwap', function (evt) {
  if (evt.detail.xhr && evt.detail.xhr.status === 400) {
    try {
      const response = JSON.parse(evt.detail.xhr.response);
      if (!response.success && response.errors) {
        evt.detail.shouldSwap = false;

        const form = evt.detail.target.closest('form');
        if (form) {
          // Remove any existing error messages
          const existingErrors = form.querySelectorAll('.error-message');
          existingErrors.forEach(el => el.remove());

          // Display field-specific errors
          Object.entries(response.errors).forEach(([field, message]) => {
            if (field === 'general') {
              // Show general error at top of form
              const errorDiv = document.createElement('div');
              errorDiv.className = 'error-message bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4';
              errorDiv.textContent = message;
              form.insertBefore(errorDiv, form.firstChild);
            } else {
              // Show field-specific error
              const input = form.querySelector(`[name="${field}"]`);
              if (input) {
                input.classList.add('error-field', 'border-red-500');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message text-red-500 text-sm mt-1';
                errorDiv.textContent = message;
                input.parentNode.appendChild(errorDiv);
              }
            }
          });
        }
      }
    } catch (e) {
      console.error('Error processing validation response:', e);
    }
  }
});

// Handle row updates after successful save
document.addEventListener('htmx:afterOnLoad', function (evt) {
  if (evt.detail.xhr && evt.detail.xhr.status === 200) {
    const triggerHeader = evt.detail.xhr.getResponseHeader('HX-Trigger-After-Swap');
    if (triggerHeader) {
      try {
        const triggers = JSON.parse(triggerHeader);
        if (triggers.updateRow) {
          const { row_id, row_html } = triggers.updateRow;

          // Always refresh the table to maintain sort order
          refreshTable().then(() => {
            // After table refresh, find and focus the updated row
            const updatedRow = document.getElementById(row_id);
            if (updatedRow) {
              // Scroll the row into view with a smooth animation
              updatedRow.scrollIntoView({ behavior: 'smooth', block: 'center' });

              // Add a subtle highlight effect
              updatedRow.classList.add('bg-yellow-50');
              setTimeout(() => {
                updatedRow.classList.remove('bg-yellow-50');
                updatedRow.classList.add('bg-white');
              }, 2000);
            }
          });
        }
      } catch (e) {
        console.error('Error processing update:', e);
        refreshTable();
      }
    }
  }
});

// Helper function to refresh the table
function refreshTable() {
  return new Promise((resolve) => {
    const urlParams = new URLSearchParams(window.location.search);
    const sort = urlParams.get('sort');

    let url = '/crud/manifest/';
    if (sort) {
      url += `?sort=${sort}`;
    }

    htmx.ajax('GET', url, {
      target: '#manifest-table',
      swap: 'innerHTML',
      include: '[name="search"], [name="per_page"]'
    }).then(() => {
      resolve();
    });
  });
}
