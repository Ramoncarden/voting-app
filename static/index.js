document.getElementById('btn-delete-account').onclick = function confirmation() {
  if (!confirm('Confirm submit?')) {
    return false;
  }
};
