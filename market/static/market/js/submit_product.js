document.addEventListener('DOMContentLoaded', () => {
  const imageInput = document.querySelector('#id_image');
  const preview = document.getElementById('image-preview');
  const titleInput = document.querySelector('#id_title');
  const descInput = document.querySelector('#id_description');
  const categorySelect = document.querySelector('#id_category');

  if (!imageInput || !preview) return;

  imageInput.addEventListener('change', () => {
    const file = imageInput.files[0];
    if (!file) return;

    // Preview
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Simple auto title suggestion from file name (if title empty)
    if (titleInput && !titleInput.value) {
      const base = file.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');
      titleInput.value = base.charAt(0).toUpperCase() + base.slice(1);
    }

    // Optional: call InstaBrand mock API to generate branding text
    if (titleInput && descInput && categorySelect) {
      const formData = new FormData();
      formData.append('image_url', 'local-upload');
      formData.append('category', categorySelect.value || 'other');
      formData.append('shg_id', '');

      fetch('/instabrand/', {
        method: 'POST',
        body: formData,
      })
        .then(res => res.json())
        .then(data => {
          if (data.title && !titleInput.value) {
            titleInput.value = data.title;
          }
          if (data.description && !descInput.value) {
            descInput.value = data.description;
          }
        })
        .catch(() => {
          // Silent fail – mock API is only for demo
        });
    }
  });
});
