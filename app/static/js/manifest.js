document.addEventListener('htmx:afterOnLoad', function (evt) {
  if (evt.detail.elt.id === 'manifest-table') {
    // Refresh the table after per_page changes
    htmx.ajax('GET', '/crud/manifest/', { target: '#manifest-table', swap: 'innerHTML' });
  }
});

// Handle manifest save response
document.addEventListener('htmx:beforeSwap', function (evt) {
  // Check if this is a save response
  if (evt.detail.xhr && evt.detail.xhr.getResponseHeader('Content-Type') === 'application/json') {
    try {
      const response = JSON.parse(evt.detail.xhr.response);

      if (response.row_id) {
        // Close the modal
        const modalContainer = document.getElementById('modal-container');
        if (modalContainer) {
          modalContainer.innerHTML = '';
        }

        // Refresh the table
        htmx.ajax('GET', '/crud/manifest/', { target: '#manifest-table', swap: 'innerHTML' });

        // Prevent default swap
        evt.detail.shouldSwap = false;
      }
    } catch (e) {
      console.error('Error processing response:', e);
    }
  }
});
