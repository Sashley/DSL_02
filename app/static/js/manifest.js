document.addEventListener('manifestSaved', function () {
  // Refresh the manifest table. This custom event is fired from save_manifest
  htmx.trigger('#manifest-table', 'refreshList');
});

document.addEventListener('htmx:afterOnLoad', function (evt) {
  if (evt.detail.elt.id === 'manifest-table') {
    // Refresh the table after a manifest is saved or per_page changes
    htmx.ajax('GET', '/crud/manifest/', { target: '#manifest-table', swap: 'innerHTML' });
  }
});
