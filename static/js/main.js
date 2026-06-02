// CleverLand Admin - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие flash-сообщений
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });
});

// Показать детали ученика
function showDetails(tgId) {
    alert('Детали ученика ' + tgId + '\n\n(Функция в разработке)');
}
