
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

//// 默认打开第一个选项卡
//document.addEventListener('DOMContentLoaded', (event) => {
//    var firstTab = document.getElementsByClassName('tablinks')[0];
//    openTab({ currentTarget: firstTab }, firstTab.getAttribute('onclick').split('(')[1].split(')')[0]);
//});

document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.tabcontent h3');
    sections.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.style.display === 'block') {
                content.style.display = 'none';
            } else {
                content.style.display = 'block';
            }
        });
    });
});


// 信号分析
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.signal-btn');
    sections.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.style.display === 'none') {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        });
    });
});

// 收益分析
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.return-btn');
    sections.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.style.display === 'none') {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        });
    });
});