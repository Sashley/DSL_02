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
          const rowElement = document.getElementById(row_id);

          if (rowElement) {
            // Check if sort parameter exists and if it matches edited fields
            const urlParams = new URLSearchParams(window.location.search);
            const sort = urlParams.get('sort');
            const editedFields = ['bill_of_lading', 'shipper_name', 'consignee_name', 'vessel_name', 'voyage_name'];
            const sortField = sort?.startsWith('-') ? sort.substring(1) : sort;

            if (editedFields.includes(sortField)) {
              // If sorting by an edited field, refresh the whole table
              console.log('Sort field matches edited field, refreshing table');
              refreshTable();
            } else {
              // Create a temporary container and parse the HTML
              const tempDiv = document.createElement('div');
              tempDiv.innerHTML = row_html.trim();
              // Ensure we get just the tr element
              const newRow = tempDiv.querySelector('tr');

              if (newRow) {
                // Copy over any HTMX attributes
                Array.from(rowElement.attributes).forEach(attr => {
                  if (attr.name.startsWith('hx-')) {
                    newRow.setAttribute(attr.name, attr.value);
                  }
                });

                // Replace the old row with the new one
                rowElement.replaceWith(newRow);
                console.log('Row updated successfully:', row_id);
              } else {
                console.error('Failed to parse row HTML - no tr element found');
                refreshTable();
              }
            }
          } else {
            console.log('Row not found, refreshing table');
            refreshTable();
          }
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
  });
}
