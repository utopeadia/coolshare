document.addEventListener("DOMContentLoaded", () => {
    const codeInput = document.getElementById("code-input");
    const customCodeInput = document.getElementById("custom-code");
    const timeSelect = document.getElementById("time-select");
    const customTimeInput = document.getElementById("custom-time");
    const shareButton = document.getElementById("share-button");
    const resultDiv = document.getElementById("result");
    const shareLinkSpan = document.getElementById("share-link");
    const countdownSpan = document.getElementById("countdown");
    const copyButton = document.getElementById("copy-button");
    const destroyButton = document.getElementById("destroy-button");
    const jumpForm = document.getElementById("jump-form");
    const shareCodeInput = document.getElementById("share-code-input");

    timeSelect.addEventListener("change", () => {
        customTimeInput.style.display =
            timeSelect.value === "custom" ? "inline-block" : "none";
    });

    jumpForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const shareCode = shareCodeInput.value.trim();
        if (shareCode) {
            window.location.href = `/${shareCode}`;
        }
    });

    function adjustHeight() {
        codeInput.style.height = 'auto';

        const scrollHeight = codeInput.scrollHeight;

        if (scrollHeight <= 300) {
            codeInput.style.height = '300px'; // 最小高度
        } else if (scrollHeight >= 700) {
            codeInput.style.height = '700px'; // 最大高度
        } else {
            codeInput.style.height = scrollHeight + 'px';
        }
    }
    codeInput.addEventListener('input', adjustHeight);
    // 初始调整
    adjustHeight();
    // 窗口大小改变时重新调整
    window.addEventListener('resize', adjustHeight);

    shareButton.addEventListener("click", async () => {
        const code = codeInput.value.trim();
        const customCode = customCodeInput.value.trim();
        let shareTime;

        if (code === "") {
            alert("请输入代码片段");
            return;
        }

        if (timeSelect.value === "custom") {
            shareTime = parseInt(customTimeInput.value);
            if (!Number.isInteger(shareTime) || shareTime <= 0) {
                alert("自定义时间必须为 1 到管理员最长允许时间之间的整数 (分钟)");
                return;
            }
        } else {
            shareTime = parseInt(timeSelect.value);
        }

        try {
            shareButton.disabled = true;
            const response = await fetch("/share", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ code, customCode, shareTime }),
            });

            if (response.status === 429) {
                alert("操作超限，请稍后再试");
                return; // 停止后续操作
            }

            const data = await response.json();

            if (response.ok) {
                const shareCode = data.share_code;
                const shareLink = `${window.location.origin}/${shareCode}`;
                shareLinkSpan.textContent = shareLink;

                startCountdown(shareTime * 60);

                resultDiv.classList.remove("hidden");
            } else {
                alert(`分享失败: ${data.error}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("分享失败，请稍后再试");
        } finally {
            shareButton.disabled = false;
        }
    });

    // if (ClipboardJS.isSupported()) {
    //     const clipboard = new ClipboardJS("#copy-button");
    //     clipboard.on("success", function (e) {
    //         alert("代码已复制到剪贴板");
    //     });
    //     clipboard.on("error", function (e) {
    //         alert("复制失败，请手动复制");
    //     });
    // } else {
    //     console.error("ClipboardJS not supported in this browser.");
    // }
    if (ClipboardJS.isSupported()) {
        const clipboard = new ClipboardJS("#copy-button");
        const copyMessage = document.getElementById("copy-message");

        clipboard.on("success", function (e) {
            copyMessage.textContent = "代码已复制到剪贴板";
            copyMessage.classList.add("success-message");
            copyMessage.classList.remove("error-message");
            copyMessage.style.display = "block";
            setTimeout(() => {
                copyMessage.style.display = "none";
            }, 2000);
        });

        clipboard.on("error", function (e) {
            copyMessage.textContent = "复制失败，请手动复制";
            copyMessage.classList.add("error-message");
            copyMessage.classList.remove("success-message");
            copyMessage.style.display = "block";
        });
    } else {
        console.error("ClipboardJS not supported in this browser.");
    }

    destroyButton.addEventListener("click", async () => {
        const shareCode = shareLinkSpan.textContent.split("/").pop();

        try {
            const response = await fetch("/destroy", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ share_code: shareCode }),
            });

            if (response.status === 429) {
                alert("操作超限，请稍后再试");
                return; // 停止后续操作
            }

            if (response.ok) {
                alert("代码片段已销毁");
                resultDiv.classList.add("hidden");
            } else {
                const data = await response.json();
                alert(`销毁失败: ${data.error}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("销毁失败，请稍后再试");
        }
    });

    function startCountdown(remainingTime) {
        const updateCountdown = () => {
            const minutes = Math.floor(remainingTime / 60);
            const seconds = remainingTime % 60;
            countdownSpan.textContent = `${minutes}:${seconds
                .toString()
                .padStart(2, "0")}`;

            if (remainingTime <= 0) {
                clearInterval(countdownInterval);
                countdownSpan.textContent = "已过期";
                destroyButton.disabled = true;
            }

            remainingTime--;
        };

        updateCountdown();
        const countdownInterval = setInterval(updateCountdown, 1000);
    }
});
