document.addEventListener("DOMContentLoaded", (event) => {
	hljs.highlightElement(document.getElementById("view-code"));

	const copyButton = document.getElementById("copy-button");
	const destroyButton = document.getElementById("destroy-button");
	const countdownDiv = document.getElementById("countdown");

	copyButton.addEventListener("click", () => {
		const code = document.getElementById("view-code").textContent;
		navigator.clipboard.writeText(code).then(
			() => {
				alert("代码已复制到剪贴板");
			},
			(err) => {
				console.error("无法复制代码: ", err);
			}
		);
	});

	destroyButton.addEventListener("click", async () => {
		const shareCode = window.location.pathname.split("/").pop();
		try {
			const response = await fetch("/destroy", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ share_code: shareCode }),
			});

			if (response.ok) {
				alert("代码片段已销毁");
				window.location.href = "/";
			} else {
				const data = await response.json();
				alert(`销毁失败: ${data.error}`);
			}
		} catch (error) {
			console.error("Error:", error);
			alert("销毁失败，请稍后再试");
		}
	});

	// 假设后端在渲染页面时传递了过期时间
	const expirationTime = new Date("{{ expiration_time }}").getTime();

	function updateCountdown() {
		const now = new Date().getTime();
		const timeLeft = expirationTime - now;

		if (timeLeft > 0) {
			const hours = Math.floor(
				(timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
			);
			const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
			const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

			countdownDiv.textContent = `代码将在 ${hours}小时 ${minutes}分钟 ${seconds}秒 后过期`;
		} else {
			countdownDiv.textContent = "代码已过期";
			destroyButton.disabled = true;
		}
	}

	updateCountdown();
	setInterval(updateCountdown, 1000);
});
