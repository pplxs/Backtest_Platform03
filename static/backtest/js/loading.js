
document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('dataForm');
    form.addEventListener('submit', function(e) {
        // ��ֹ����Ĭ���ύ��Ϊ
        e.preventDefault();
        // ��ʾ������ʾ
        document.getElementById('loading').style.display = 'block';
        document.getElementById('other').style.display = 'none';
        // ʹ��FormData��fetch API�ύ��
        var formData = new FormData(form);
        fetch('/'+window.location.pathname.split('/')[1] + '/load_data/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(response => {
            if (response.ok) {
                // �����Ӧ�ɹ����������������ҳ����ת����������
                window.location.href = response.url; // ���������߼�
            } else {
                // �����Ӧʧ�ܣ����������ﴦ�����
                console.error('Error submitting form');
            }
        }).catch(error => {
            console.error('Error:', error);
        }).finally(() => {
            // ����10������ؼ�����ʾ
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
            }, 10000); // 10000���� = 10��
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
