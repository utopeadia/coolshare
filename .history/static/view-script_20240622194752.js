document.addEventListener('DOMContentLoaded', (event) => {
    hljs.highlightElement(document.getElementById('view-code'));

    const copyButton = document.getElementById('copy-button');
    const destroyButton = document.getElementById('destroy-button');
    const countdownDiv = document.getElementById('countdown');

    copyButton.addEventListener('click', () => {
        const code = document.getElementById('view-code').textContent;
        navigator.clipboard.writeText(code).then(() => {
            alert('代码已复制到剪贴板');
        }, (err) => {
            console.error('无法复制代码: ', err);
        });
    });

    destroyButton.addEventListener('click', async () => {
        const shareCode = window.location.pathname.split('/').pop();
        console.log('Attempting to destroy share code:', shareCode);
        try {
            const response = await fetch('/destroy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ share_code: shareCode }),
            });

            console.log('Destroy response status:', response.status);
            const responseData = await response.json();
            console.log('Destroy response data:', responseData);

            if (response.ok) {
                alert('代码片段已销毁');
                window.location.href = '/';
            } else {
                alert(`销毁失败: ${responseData.error || '未知错误'}`);
            }
        } catch (error) {
            console.error('Error during destroy operation:', error);
            alert('销毁失败，请稍后再试');
        }
    });

    // 使用ISO格式的时间字符串
    const expirationTimeStr = '{{ expiration_time }}';
    console.log('Expiration time from server:', expirationTimeStr);
    const expirationTime = new Date(expirationTimeStr).getTime();
    console.log('Parsed expiration time:', new Date(expirationTime));

    function updateCountdown() {
        const now = new Date().getTime();
        const timeLeft = expirationTime - now;

        if (timeLeft > 0) {
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            countdownDiv.textContent = `代码将在 ${hours}小时 ${minutes}分钟 ${seconds}秒 后过期`;
        } else {
            countdownDiv.textContent = '代码已过期';
            destroyButton.disabled = true;
        }
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
});