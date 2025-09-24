document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const fragmentsFileInput = document.getElementById('fragmentsFile');
    const poolingFileInput = document.getElementById('poolingFile');
    const recycleBtn = document.getElementById('recycleBtn');
    const downloadFragmentsBtn = document.getElementById('downloadFragmentsBtn');
    const downloadPoolingBtn = document.getElementById('downloadPoolingBtn');
    const backToDashboardBtn = document.getElementById('backToDashboardBtn');
    const messageBox = document.getElementById('messageBox');

    let messageTimeout;
    let reducedFragmentsContent = '';
    let reducedPoolingContent = '';

    function showMessage(text, type) {
        if (messageTimeout) clearTimeout(messageTimeout);
        messageBox.textContent = text;
        messageBox.className = `message-${type}`;
        messageTimeout = setTimeout(() => {
            messageBox.className = 'hidden';
        }, 5000);
    }

    function downloadFile(content, fileName, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    recycleBtn.addEventListener('click', async () => {
        const fragmentsFile = fragmentsFileInput.files[0];
        const poolingFile = poolingFileInput.files[0];

        if (!fragmentsFile || !poolingFile) {
            showMessage('Please upload both "Oligo list" and "Pooling" CSV files.', 'error');
            return;
        }

        const fragments_csv = await fragmentsFile.text();
        const pooling_csv = await poolingFile.text();

        recycleBtn.disabled = true;
        recycleBtn.textContent = 'Processing...';
        downloadFragmentsBtn.disabled = true;
        downloadPoolingBtn.disabled = true;
        reducedFragmentsContent = '';
        reducedPoolingContent = '';

        try {
            const response = await fetch('/recycle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ fragments_csv, pooling_csv })
            });

            const result = await response.json();

            if (response.ok) {
                reducedFragmentsContent = result.reduced_fragments_ordered_csv;
                reducedPoolingContent = result.reduced_pooling_csv;
                downloadFragmentsBtn.disabled = false;
                downloadPoolingBtn.disabled = false;
                showMessage(result.message, 'success');
            } else {
                throw new Error(result.error || 'An unknown error occurred.');
            }

        } catch (error) {
            showMessage(`Error: ${error.message}`, 'error');
        } finally {
            recycleBtn.disabled = false;
            recycleBtn.textContent = 'Recycle Oligos';
        }
    });

    downloadFragmentsBtn.addEventListener('click', () => {
        if (reducedFragmentsContent) {
            downloadFile(reducedFragmentsContent, 'reduced_fragments_ordered.csv', 'text/csv');
        }
    });

    downloadPoolingBtn.addEventListener('click', () => {
        if (reducedPoolingContent) {
            downloadFile(reducedPoolingContent, 'reduced_pooling.csv', 'text/csv');
        }
    });

    backToDashboardBtn.addEventListener('click', () => {
        window.location.href = 'Dashboard.html';
    });
});
