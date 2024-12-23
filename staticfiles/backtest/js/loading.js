
document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('dataForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        document.getElementById('loading').style.display = 'block';
        document.getElementById('other').style.display = 'none';

        var formData = new FormData(form);
        fetch('/'+window.location.pathname.split('/')[1] + '/load_data/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(response => {
            if (response.ok) {
                window.location.href = response.url;
            } else {
                console.error('Error submitting form');
            }
        }).catch(error => {
            console.error('Error:', error);
        }).finally(() => {
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
            }, 10000);
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
