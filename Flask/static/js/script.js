// AI-Дайджест - Скрипт для поиска и фильтрации

document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.card');
    const noResults = document.getElementById('noResults');
    const resultsCount = document.getElementById('resultsCount');

    let currentFilter = 'all';

    // Функция фильтрации карточек
    function filterCards() {
        let visibleCount = 0;

        cards.forEach(card => {
            const cardTags = card.dataset.tags.split(',');

            // Проверка фильтра
            const matchesFilter = currentFilter === 'all' ||
                cardTags.includes(currentFilter);

            if (matchesFilter) {
                card.style.display = 'block';
                card.classList.add('visible');
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.classList.remove('visible');
            }
        });

        // Обновление счетчика
        resultsCount.textContent = visibleCount;

        // Показ/скрытие "нет результатов"
        noResults.style.display = visibleCount === 0 ? 'flex' : 'none';
    }

    // Обработчик фильтров (кнопки сверху)
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Удаление active у всех кнопок
            filterBtns.forEach(b => b.classList.remove('active'));
            // Добавление active к нажатой
            this.classList.add('active');

            currentFilter = this.dataset.tag;
            filterCards();
        });
    });

    // Обработчик клика по тегам внутри карточек
    document.querySelectorAll('.card-tags .tag').forEach(tag => {
        tag.addEventListener('click', function(e) {
            e.preventDefault();
            const tagText = this.textContent;

            // Удаление active у всех кнопок
            filterBtns.forEach(b => b.classList.remove('active'));

            // Поиск кнопки с этим тегом и активация
            filterBtns.forEach(btn => {
                if (btn.dataset.tag === tagText) {
                    btn.classList.add('active');
                }
            });

            currentFilter = tagText;
            filterCards();

            // Прокрутка к фильтрам
            document.querySelector('.filters-section').scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Анимация появления карточек
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Сохранение состояния в localStorage
    function saveState() {
        localStorage.setItem('ai-digest-filter', currentFilter);
    }

    function loadState() {
        const savedFilter = localStorage.getItem('ai-digest-filter');

        if (savedFilter && savedFilter !== 'all') {
            currentFilter = savedFilter;
            filterBtns.forEach(btn => {
                if (btn.dataset.tag === savedFilter) {
                    btn.classList.add('active');
                }
            });
        }
    }

    // Сохраняем состояние при изменении
    filterBtns.forEach(btn => btn.addEventListener('click', saveState));

    // Загружаем состояние
    loadState();
    filterCards();
});