document.addEventListener('DOMContentLoaded', function() {

    tinymce.init({
        selector: '#content',
        plugins: 'image code',
        toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | image | code',
        images_upload_url: '/upload-image',
        images_upload_handler: function (blobInfo, success, failure) {
            var xhr, formData;
            xhr = new XMLHttpRequest();
            xhr.withCredentials = false;
            xhr.open('POST', '/upload-image');
            xhr.onload = function() {
                var json;
                if (xhr.status != 200) {
                    failure('HTTP Error: ' + xhr.status);
                    return;
                }
                json = JSON.parse(xhr.responseText);
                if (!json || typeof json.location != 'string') {
                    failure('Invalid JSON: ' + xhr.responseText);
                    return;
                }
                success(json.location);
            };
            formData = new FormData();
            formData.append('file', blobInfo.blob(), blobInfo.filename());
            xhr.send(formData);
        }
    });

    const dropzone = document.getElementById('image-upload');
    const fileInput = document.getElementById('file-input');
    const contentTextarea = document.getElementById('content');

    dropzone.addEventListener('click', function() {
        fileInput.click();
    });

    dropzone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', function() {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        for (let file of files) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    insertImagePlaceholder(file.name, e.target.result);
                };
                reader.readAsDataURL(file);
            }
        }
    }

    function insertImagePlaceholder(filename, src) {
        const placeholder = `[Image: ${filename} - Caption goes here]\n`;
        const cursorPos = contentTextarea.selectionStart;
        const textBefore = contentTextarea.value.substring(0, cursorPos);
        const textAfter = contentTextarea.value.substring(cursorPos);
        contentTextarea.value = textBefore + placeholder + textAfter;
        contentTextarea.focus();
        contentTextarea.selectionStart = contentTextarea.selectionEnd = cursorPos + placeholder.length;
    }
});