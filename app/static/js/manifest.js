document.addEventListener('manifestSaved', function () {
  // Refresh the manifest list.  This custom event is fired from save_manifest
  htmx.trigger('#manifest-list', 'refreshList');
});

// Listen for the refreshList event on the manifest list
document.addEventListener('htmx:afterOnLoad', function (evt) {
  if (evt.detail.elt.id === 'manifest-list') {
    // Refresh the list after a manifest is saved or per_page changes
    htmx.ajax('GET', '/crud/manifest/', { target: '#manifest-list', swap: 'innerHTML' });
  }
});

// Listen for table height updates
document.addEventListener('htmx:afterSettle', function (evt) {
  const tableContainer = document.getElementById('table-container');
  if (tableContainer) {
    // Get the per_page value from the HX-Trigger header
    const trigger = evt.detail.headers['HX-Trigger'];
    if (trigger && trigger.startsWith('updateTableHeight:')) {
      const perPage = trigger.split(':')[1];
      // Update the rows container class and style
      tableContainer.className = `table-container rows-${perPage}`;
      tableContainer.style.setProperty('--rows', perPage);
    }
  }
});
