
document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('dataForm');
    form.addEventListener('submit', function(e) {
        // 阻止表单的默认提交行为
        e.preventDefault();
        // 显示加载提示
        document.getElementById('loading').style.display = 'block';
        document.getElementById('other').style.display = 'none';
        // 使用FormData和fetch API提交表单
        var formData = new FormData(form);
        fetch('/'+window.location.pathname.split('/')[1] + '/load_data/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(response => {
            if (response.ok) {
                // 如果响应成功，可以在这里进行页面跳转或其他操作
                window.location.href = response.url; // 或者其他逻辑
            } else {
                // 如果响应失败，可以在这里处理错误
                console.error('Error submitting form');
            }
        }).catch(error => {
            console.error('Error:', error);
        }).finally(() => {
            // 设置10秒后隐藏加载提示
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
            }, 10000); // 10000毫秒 = 10秒
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
