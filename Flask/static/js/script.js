// AI-Дайджест - Скрипт для поиска и фильтрации

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.card');
    const noResults = document.getElementById('noResults');
    const resultsCount = document.getElementById('resultsCount');

    let currentFilter = 'all';
    let searchQuery = '';

    // Функция фильтрации карточек
    function filterCards() {
        let visibleCount = 0;

        cards.forEach(card => {
            const cardTags = card.dataset.tags.split(',');
            const cardTitle = card.querySelector('.card-title').textContent.toLowerCase();
            const cardDesc = card.querySelector('.card-description').textContent.toLowerCase();

            // Проверка поиска
            const matchesSearch = searchQuery === '' ||
                cardTitle.includes(searchQuery) ||
                cardDesc.includes(searchQuery);

            // Проверка фильтра
            const matchesFilter = currentFilter === 'all' ||
                cardTags.includes(currentFilter);

            if (matchesSearch && matchesFilter) {
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

    // Обработчик поиска
    searchInput.addEventListener('input', function(e) {
        searchQuery = e.target.value.toLowerCase().trim();
        filterCards();
    });

    // Обработчик фильтров
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
        localStorage.setItem('ai-digest-search', searchQuery);
    }

    function loadState() {
        const savedFilter = localStorage.getItem('ai-digest-filter');
        const savedSearch = localStorage.getItem('ai-digest-search');

        if (savedFilter && savedFilter !== 'all') {
            currentFilter = savedFilter;
            filterBtns.forEach(btn => {
                if (btn.dataset.tag === savedFilter) {
                    btn.classList.add('active');
                }
            });
        }

        if (savedSearch) {
            searchQuery = savedSearch;
            searchInput.value = searchQuery;
        }
    }

    // Сохраняем состояние при изменении
    searchInput.addEventListener('change', saveState);
    filterBtns.forEach(btn => btn.addEventListener('click', saveState));

    // Загружаем состояние
    loadState();
    filterCards();
});