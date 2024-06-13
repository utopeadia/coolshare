const codeInput = document.getElementById('code-input');
const customCodeInput = document.getElementById('custom-code');
const timeSelect = document.getElementById('time-select');
const customTimeInput = document.getElementById('custom-time');
const shareButton = document.getElementById('share-button');
const resultDiv = document.getElementById('result');
const shareLinkSpan = document.getElementById('share-link');
const countdownSpan = document.getElementById('countdown');
const copyButton = document.getElementById('copy-button');
const destroyButton = document.getElementById('destroy-button');

timeSelect.addEventListener('change', () => {
    customTimeInput.style.display = timeSelect.value === 'custom' ? 'inline-block' : 'none';
});

shareButton.addEventListener('click', async () => {
    const code = codeInput.value;
    const customCode = customCodeInput.value;
    let shareTime;

    if (timeSelect.value === 'custom') {
        shareTime = parseInt(customTimeInput.value);
        if (isNaN(shareTime) || shareTime <= 0 || shareTime > 28800) {
            alert('自定义时间必须为 1 到 28800 之间的数字 (分钟)');
            return;
        }
    } else {
        shareTime = parseInt(timeSelect.value);
    }

    try {
        const response = await fetch('/share', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code, customCode, customTime: shareTime }),
        });

        const data = await response.json();

        if (response.ok) {
            const shareCode = data.share_code;
            const shareLink = `${window.location.origin}/view/${shareCode}`;
            shareLinkSpan.textContent = shareLink;

            let remainingTime = shareTime * 60;

            const updateCountdown = () => {
                const minutes = Math.floor(remainingTime / 60);
                const seconds = remainingTime % 60;
                countdownSpan.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

                if (remainingTime <= 0) {
                    clearInterval(countdownInterval);
                    countdownSpan.textContent = '已过期';
                    destroyButton.disabled = true;
                }

                remainingTime--;
            };

            updateCountdown();
            const countdownInterval = setInterval(updateCountdown, 1000);

            resultDiv.classList.remove('hidden');
        } else {
            alert(`分享失败: ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('分享失败，请稍后再试');
    }
});

copyButton.addEventListener('click', () => {
    navigator.clipboard.writeText(shareLinkSpan.textContent)
        .then(() => {
            alert('分享链接已复制到剪贴板');
        })
        .catch(err => {
            console.error('Failed to copy: ', err);
        });
});

destroyButton.addEventListener('click', async () => {
    const shareCode = shareLinkSpan.textContent.split('/').pop();

    try {
        const response = await fetch('/destroy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ share_code: shareCode }),
        });

        if (response.ok) {
            alert('代码片段已销毁');
            resultDiv.classList.add('hidden');
        } else {
            const data = await response.json();
            alert(`销毁失败: ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('销毁失败，请稍后再试');
    }
});
