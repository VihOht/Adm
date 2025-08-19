// Transaction Filtering System

document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    setupFilterEventListeners();
});

let originalTransactions = {
    all: [],
    expenses: [],
    incomes: []
};

let currentFilters = {
    month: '',
    year: '',
    expenseCategory: '',
    incomeCategory: '',
    dateRange: {
        start: '',
        end: ''
    },
    amountRange: {
        min: '',
        max: ''
    }
};

function initializeFilters() {
    // Store original transaction data
    storeOriginalTransactions();
    
    // Populate filter dropdowns
    populateYearFilter();
    populateMonthFilter();
    populateCategoryFilters();
    
    // Setup date range picker
    setupDateRangePicker();
    
    // Apply URL parameters if any
    applyURLFilters();
}

function storeOriginalTransactions() {
    // Store all transactions data from the DOM
    const allTransactionCards = document.querySelectorAll('#all-tab .transaction-card');
    const expenseRows = document.querySelectorAll('#expenses-tab tbody tr');
    const incomeRows = document.querySelectorAll('#incomes-tab tbody tr');
    
    // Extract data from DOM elements
    originalTransactions.all = Array.from(allTransactionCards).map(card => extractCardData(card));
    originalTransactions.expenses = Array.from(expenseRows).map(row => extractRowData(row, 'expense'));
    originalTransactions.incomes = Array.from(incomeRows).map(row => extractRowData(row, 'income'));
}

function extractCardData(card) {
    const isIncome = card.classList.contains('income-border');
    const description = card.querySelector('h3').textContent.trim();
    const detailedDescription = card.querySelector('p').textContent.trim();
    const categorySpan = card.querySelector('.category-indicator + span');
    const category = categorySpan ? categorySpan.textContent.trim() : 'Sem categoria';
    const dateText = card.querySelector('.text-xs:last-child').textContent.trim();
    const amountText = card.querySelector('.amount-income, .amount-expense').textContent.trim();
    
    // Extract category ID from the edit button onclick attribute
    let categoryId = null;
    const editButton = card.querySelector('button[onclick*="Modal"]');
    if (editButton) {
        const onclickAttr = editButton.getAttribute('onclick');
        const match = onclickAttr.match(/,\s*(\d+|null)\s*\)/);
        if (match && match[1] !== 'null') {
            categoryId = match[1];
        }
    }
    
    return {
        element: card,
        type: isIncome ? 'income' : 'expense',
        description,
        detailedDescription,
        category,
        categoryId,
        date: parseDate(dateText),
        amount: parseAmount(amountText),
        originalElement: card.cloneNode(true)
    };
}

function extractRowData(row, type) {
    const cells = row.querySelectorAll('td');
    if (cells.length < 4) return null;
    
    const description = cells[0].querySelector('.font-semibold').textContent.trim();
    const detailedDescription = cells[0].querySelector('.text-sm')?.textContent.trim() || '';
    const categorySpan = cells[1].querySelector('.category-indicator + span');
    const category = categorySpan ? categorySpan.textContent.trim() : 'Sem categoria';
    const dateText = cells[2].textContent.trim();
    const amountText = cells[3].textContent.trim();
    
    // Extract category ID from the edit button onclick attribute
    let categoryId = null;
    const editButton = row.querySelector('button[onclick*="Modal"]');
    if (editButton) {
        const onclickAttr = editButton.getAttribute('onclick');
        const match = onclickAttr.match(/,\s*(\d+|null)\s*\)/);
        if (match && match[1] !== 'null') {
            categoryId = match[1];
        }
    }
    
    return {
        element: row,
        type,
        description,
        detailedDescription,
        category,
        categoryId,
        date: parseDate(dateText),
        amount: parseAmount(amountText),
        originalElement: row.cloneNode(true)
    };
}

function parseDate(dateText) {
    // Parse date from DD/MM/YYYY format
    const parts = dateText.split('/');
    if (parts.length === 3) {
        return new Date(parts[2], parts[1] - 1, parts[0]);
    }
    return new Date();
}

function parseAmount(amountText) {
    // Extract numeric value from amount text (e.g., "R$ 150,00" -> 150.00)
    const cleaned = amountText.replace(/[^\d,.-]/g, '').replace(',', '.');
    return parseFloat(cleaned) || 0;
}

function populateYearFilter() {
    const yearSelect = document.getElementById('year-filter');
    if (!yearSelect) return;
    
    // Get all unique years from transactions
    const years = new Set();
    const allDates = [
        ...originalTransactions.all.map(t => t.date),
        ...originalTransactions.expenses.map(t => t.date),
        ...originalTransactions.incomes.map(t => t.date)
    ];
    
    allDates.forEach(date => {
        if (date) years.add(date.getFullYear());
    });
    
    // Sort years in descending order
    const sortedYears = Array.from(years).sort((a, b) => b - a);
    
    // Clear existing options except the first one
    yearSelect.innerHTML = '<option value="">Todos os anos</option>';
    
    sortedYears.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    });
}

function populateMonthFilter() {
    const monthSelect = document.getElementById('month-filter');
    if (!monthSelect) return;
    
    const months = [
        { value: '', text: 'Todos os meses' },
        { value: '1', text: 'Janeiro' },
        { value: '2', text: 'Fevereiro' },
        { value: '3', text: 'Março' },
        { value: '4', text: 'Abril' },
        { value: '5', text: 'Maio' },
        { value: '6', text: 'Junho' },
        { value: '7', text: 'Julho' },
        { value: '8', text: 'Agosto' },
        { value: '9', text: 'Setembro' },
        { value: '10', text: 'Outubro' },
        { value: '11', text: 'Novembro' },
        { value: '12', text: 'Dezembro' }
    ];
    
    monthSelect.innerHTML = '';
    months.forEach(month => {
        const option = document.createElement('option');
        option.value = month.value;
        option.textContent = month.text;
        monthSelect.appendChild(option);
    });
}

function populateCategoryFilters() {
    populateExpenseCategoryFilter();
    populateIncomeCategoryFilter();
}

function populateExpenseCategoryFilter() {
    const categorySelect = document.getElementById('expense-category-filter');
    if (!categorySelect) return;
    
    // Get unique expense categories with their IDs and names
    const categories = new Map();
    originalTransactions.expenses.forEach(transaction => {
        if (transaction.category && transaction.category !== 'Sem categoria' && transaction.categoryId) {
            categories.set(transaction.categoryId, transaction.category);
        }
    });
    
    // Keep existing options from template and add any missing ones
    const existingOptions = Array.from(categorySelect.options);
    const existingValues = new Set(existingOptions.map(opt => opt.value));
    
    // Add any categories found in transactions that aren't in the template
    categories.forEach((name, id) => {
        if (!existingValues.has(id)) {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            categorySelect.appendChild(option);
        }
    });
    
    // Add "Sem categoria" option if not present
    if (!existingValues.has('no-category')) {
        const noCategoryOption = document.createElement('option');
        noCategoryOption.value = 'no-category';
        noCategoryOption.textContent = 'Sem categoria';
        categorySelect.appendChild(noCategoryOption);
    }
}

function populateIncomeCategoryFilter() {
    const categorySelect = document.getElementById('income-category-filter');
    if (!categorySelect) return;
    
    // Get unique income categories with their IDs and names
    const categories = new Map();
    originalTransactions.incomes.forEach(transaction => {
        if (transaction.category && transaction.category !== 'Sem categoria' && transaction.categoryId) {
            categories.set(transaction.categoryId, transaction.category);
        }
    });
    
    // Keep existing options from template and add any missing ones
    const existingOptions = Array.from(categorySelect.options);
    const existingValues = new Set(existingOptions.map(opt => opt.value));
    
    // Add any categories found in transactions that aren't in the template
    categories.forEach((name, id) => {
        if (!existingValues.has(id)) {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            categorySelect.appendChild(option);
        }
    });
    
    // Add "Sem categoria" option if not present
    if (!existingValues.has('no-category')) {
        const noCategoryOption = document.createElement('option');
        noCategoryOption.value = 'no-category';
        noCategoryOption.textContent = 'Sem categoria';
        categorySelect.appendChild(noCategoryOption);
    }
}

function setupDateRangePicker() {
    const startDateInput = document.getElementById('start-date-filter');
    const endDateInput = document.getElementById('end-date-filter');
    
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', applyFilters);
        endDateInput.addEventListener('change', applyFilters);
    }
}

function setupFilterEventListeners() {
    // Month/Year filters
    const monthFilter = document.getElementById('month-filter');
    const yearFilter = document.getElementById('year-filter');
    
    if (monthFilter) monthFilter.addEventListener('change', applyFilters);
    if (yearFilter) yearFilter.addEventListener('change', applyFilters);
    
    // Category filters
    const expenseCategoryFilter = document.getElementById('expense-category-filter');
    const incomeCategoryFilter = document.getElementById('income-category-filter');
    
    if (expenseCategoryFilter) expenseCategoryFilter.addEventListener('change', applyFilters);
    if (incomeCategoryFilter) incomeCategoryFilter.addEventListener('change', applyFilters);
    
    // Amount range filters
    const minAmountFilter = document.getElementById('min-amount-filter');
    const maxAmountFilter = document.getElementById('max-amount-filter');
    
    if (minAmountFilter) minAmountFilter.addEventListener('input', debounce(applyFilters, 500));
    if (maxAmountFilter) maxAmountFilter.addEventListener('input', debounce(applyFilters, 500));
    
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', clearAllFilters);
    
    // Quick filter buttons
    setupQuickFilters();
}

function setupQuickFilters() {
    // This month
    const thisMonthBtn = document.getElementById('filter-this-month');
    if (thisMonthBtn) {
        thisMonthBtn.addEventListener('click', () => {
            const now = new Date();
            setMonthYearFilter(now.getMonth() + 1, now.getFullYear());
        });
    }
    
    // Last month
    const lastMonthBtn = document.getElementById('filter-last-month');
    if (lastMonthBtn) {
        lastMonthBtn.addEventListener('click', () => {
            const now = new Date();
            const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
            setMonthYearFilter(lastMonth.getMonth() + 1, lastMonth.getFullYear());
        });
    }
    
    // This year
    const thisYearBtn = document.getElementById('filter-this-year');
    if (thisYearBtn) {
        thisYearBtn.addEventListener('click', () => {
            const now = new Date();
            setMonthYearFilter('', now.getFullYear());
        });
    }
}

function setMonthYearFilter(month, year) {
    const monthFilter = document.getElementById('month-filter');
    const yearFilter = document.getElementById('year-filter');
    
    if (monthFilter) monthFilter.value = month;
    if (yearFilter) yearFilter.value = year;
    
    applyFilters();
}

function applyFilters() {
    // Update current filters
    updateCurrentFilters();
    
    // Filter each transaction type
    filterAllTransactions();
    filterExpenses();
    filterIncomes();
    
    // Update URL with current filters
    updateURL();
    
    // Update filter summary
    updateFilterSummary();
    
    // Update statistics
    updateFilteredStatistics();
}

function updateCurrentFilters() {
    const monthFilter = document.getElementById('month-filter');
    const yearFilter = document.getElementById('year-filter');
    const expenseCategoryFilter = document.getElementById('expense-category-filter');
    const incomeCategoryFilter = document.getElementById('income-category-filter');
    const startDateFilter = document.getElementById('start-date-filter');
    const endDateFilter = document.getElementById('end-date-filter');
    const minAmountFilter = document.getElementById('min-amount-filter');
    const maxAmountFilter = document.getElementById('max-amount-filter');
    
    currentFilters.month = monthFilter ? monthFilter.value : '';
    currentFilters.year = yearFilter ? yearFilter.value : '';
    currentFilters.expenseCategory = expenseCategoryFilter ? expenseCategoryFilter.value : '';
    currentFilters.incomeCategory = incomeCategoryFilter ? incomeCategoryFilter.value : '';
    currentFilters.dateRange.start = startDateFilter ? startDateFilter.value : '';
    currentFilters.dateRange.end = endDateFilter ? endDateFilter.value : '';
    currentFilters.amountRange.min = minAmountFilter ? parseFloat(minAmountFilter.value) || '' : '';
    currentFilters.amountRange.max = maxAmountFilter ? parseFloat(maxAmountFilter.value) || '' : '';
}

function filterAllTransactions() {
    const container = document.querySelector('#all-tab .space-y-4');
    if (!container) return;
    
    // Clear current content
    container.innerHTML = '';
    
    // Filter and display transactions
    const filteredTransactions = originalTransactions.all.filter(transaction => {
        return matchesFilters(transaction);
    });
    
    if (filteredTransactions.length === 0) {
        showNoResultsMessage(container, 'all');
    } else {
        filteredTransactions.forEach(transaction => {
            container.appendChild(transaction.originalElement.cloneNode(true));
        });
    }
}

function filterExpenses() {
    const tbody = document.querySelector('#expenses-tab tbody');
    if (!tbody) return;
    
    // Clear current content
    tbody.innerHTML = '';
    
    // Filter and display expenses
    const filteredExpenses = originalTransactions.expenses.filter(transaction => {
        return matchesFilters(transaction);
    });
    
    if (filteredExpenses.length === 0) {
        showNoResultsMessage(tbody, 'expenses');
    } else {
        filteredExpenses.forEach(transaction => {
            tbody.appendChild(transaction.originalElement.cloneNode(true));
        });
    }
}

function filterIncomes() {
    const tbody = document.querySelector('#incomes-tab tbody');
    if (!tbody) return;
    
    // Clear current content
    tbody.innerHTML = '';
    
    // Filter and display incomes
    const filteredIncomes = originalTransactions.incomes.filter(transaction => {
        return matchesFilters(transaction);
    });
    
    if (filteredIncomes.length === 0) {
        showNoResultsMessage(tbody, 'incomes');
    } else {
        filteredIncomes.forEach(transaction => {
            tbody.appendChild(transaction.originalElement.cloneNode(true));
        });
    }
}

function matchesFilters(transaction) {
    // Month filter
    if (currentFilters.month && transaction.date.getMonth() + 1 !== parseInt(currentFilters.month)) {
        return false;
    }
    
    // Year filter
    if (currentFilters.year && transaction.date.getFullYear() !== parseInt(currentFilters.year)) {
        return false;
    }
    
    // Category filter - improved logic
    const categoryFilter = transaction.type === 'expense' ? currentFilters.expenseCategory : currentFilters.incomeCategory;
    if (categoryFilter) {
        if (categoryFilter === 'no-category') {
            // Show transactions without category or with "Sem categoria"
            if (transaction.categoryId || (transaction.category && transaction.category !== 'Sem categoria')) {
                return false;
            }
        } else {
            // Match by category ID
            if (transaction.categoryId !== categoryFilter) {
                return false;
            }
        }
    }
    
    // Date range filter
    if (currentFilters.dateRange.start) {
        const startDate = new Date(currentFilters.dateRange.start);
        if (transaction.date < startDate) return false;
    }
    
    if (currentFilters.dateRange.end) {
        const endDate = new Date(currentFilters.dateRange.end);
        if (transaction.date > endDate) return false;
    }
    
    // Amount range filter
    if (currentFilters.amountRange.min !== '' && transaction.amount < currentFilters.amountRange.min) {
        return false;
    }
    
    if (currentFilters.amountRange.max !== '' && transaction.amount > currentFilters.amountRange.max) {
        return false;
    }
    
    return true;
}

function showNoResultsMessage(container, type) {
    const noResultsDiv = document.createElement('div');
    noResultsDiv.className = 'text-center py-12';
    
    let icon, title, message;
    
    switch (type) {
        case 'expenses':
            icon = 'trending-down';
            title = 'Nenhum gasto encontrado';
            message = 'Tente ajustar os filtros para encontrar gastos';
            break;
        case 'incomes':
            icon = 'trending-up';
            title = 'Nenhuma receita encontrada';
            message = 'Tente ajustar os filtros para encontrar receitas';
            break;
        default:
            icon = 'search';
            title = 'Nenhuma transação encontrada';
            message = 'Tente ajustar os filtros para encontrar transações';
    }
    
    noResultsDiv.innerHTML = `
        <i data-lucide="${icon}" class="w-16 h-16 text-base-content/30 mx-auto mb-4"></i>
        <h3 class="text-lg font-semibold text-base-content/70 mb-2">${title}</h3>
        <p class="text-base-content/50 mb-4">${message}</p>
        <button onclick="clearAllFilters()" class="btn btn-outline btn-sm">
            <i data-lucide="x" class="w-4 h-4 mr-2"></i>
            Limpar Filtros
        </button>
    `;
    
    if (container.tagName === 'TBODY') {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 5;
        td.appendChild(noResultsDiv);
        tr.appendChild(td);
        container.appendChild(tr);
    } else {
        container.appendChild(noResultsDiv);
    }
    
    // Re-initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function clearAllFilters() {
    // Reset all filter inputs
    const filterInputs = [
        'month-filter',
        'year-filter',
        'expense-category-filter',
        'income-category-filter',
        'start-date-filter',
        'end-date-filter',
        'min-amount-filter',
        'max-amount-filter'
    ];
    
    filterInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.value = '';
        }
    });
    
    // Reset current filters
    currentFilters = {
        month: '',
        year: '',
        expenseCategory: '',
        incomeCategory: '',
        dateRange: { start: '', end: '' },
        amountRange: { min: '', max: '' }
    };
    
    // Reapply filters (which will show all transactions)
    applyFilters();
}

function updateFilterSummary() {
    const summaryContainer = document.getElementById('filter-summary');
    if (!summaryContainer) return;
    
    const activeFilters = [];
    
    if (currentFilters.month) {
        const monthNames = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        activeFilters.push(`Mês: ${monthNames[parseInt(currentFilters.month)]}`);
    }
    
    if (currentFilters.year) {
        activeFilters.push(`Ano: ${currentFilters.year}`);
    }
    
    if (currentFilters.expenseCategory) {
        let categoryText = 'Sem categoria';
        if (currentFilters.expenseCategory !== 'no-category') {
            // Find category name by ID
            const categorySelect = document.getElementById('expense-category-filter');
            const selectedOption = categorySelect?.querySelector(`option[value="${currentFilters.expenseCategory}"]`);
            categoryText = selectedOption ? selectedOption.textContent : `ID: ${currentFilters.expenseCategory}`;
        }
        activeFilters.push(`Categoria de Gasto: ${categoryText}`);
    }
    
    if (currentFilters.incomeCategory) {
        let categoryText = 'Sem categoria';
        if (currentFilters.incomeCategory !== 'no-category') {
            // Find category name by ID
            const categorySelect = document.getElementById('income-category-filter');
            const selectedOption = categorySelect?.querySelector(`option[value="${currentFilters.incomeCategory}"]`);
            categoryText = selectedOption ? selectedOption.textContent : `ID: ${currentFilters.incomeCategory}`;
        }
        activeFilters.push(`Categoria de Receita: ${categoryText}`);
    }
    
    if (currentFilters.amountRange.min !== '' || currentFilters.amountRange.max !== '') {
        let rangeText = 'Valor: ';
        if (currentFilters.amountRange.min !== '' && currentFilters.amountRange.max !== '') {
            rangeText += `R$ ${currentFilters.amountRange.min} - R$ ${currentFilters.amountRange.max}`;
        } else if (currentFilters.amountRange.min !== '') {
            rangeText += `≥ R$ ${currentFilters.amountRange.min}`;
        } else {
            rangeText += `≤ R$ ${currentFilters.amountRange.max}`;
        }
        activeFilters.push(rangeText);
    }
    
    if (activeFilters.length === 0) {
        summaryContainer.classList.add('hidden');
    } else {
        summaryContainer.classList.remove('hidden');
        summaryContainer.innerHTML = `
            <div class="flex items-center gap-2 text-sm text-base-content/70">
                <i data-lucide="filter" class="w-4 h-4"></i>
                <span>Filtros ativos:</span>
                <div class="flex flex-wrap gap-1">
                    ${activeFilters.map(filter => `
                        <span class="badge badge-primary badge-sm">${filter}</span>
                    `).join('')}
                </div>
                <button onclick="clearAllFilters()" class="btn btn-ghost btn-xs ml-2">
                    <i data-lucide="x" class="w-3 h-3"></i>
                </button>
            </div>
        `;
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function updateFilteredStatistics() {
    // This function can be extended to update statistics based on filtered results
    // For now, we'll just update the visible counts in tabs
    
    const allTab = document.getElementById('all-button');
    const expensesTab = document.getElementById('expenses-button');
    const incomesTab = document.getElementById('incomes-button');
    
    const allCount = document.querySelectorAll('#all-tab .transaction-card').length;
    const expensesCount = document.querySelectorAll('#expenses-tab tbody tr').length;
    const incomesCount = document.querySelectorAll('#incomes-tab tbody tr').length;
    
    // Update tab texts with counts
    if (allTab) allTab.textContent = `Todas (${allCount})`;
    if (expensesTab) expensesTab.textContent = `Gastos (${expensesCount})`;
    if (incomesTab) incomesTab.textContent = `Receitas (${incomesCount})`;
}

function updateURL() {
    const params = new URLSearchParams();
    
    if (currentFilters.month) params.set('month', currentFilters.month);
    if (currentFilters.year) params.set('year', currentFilters.year);
    if (currentFilters.expenseCategory) params.set('expense_category', currentFilters.expenseCategory);
    if (currentFilters.incomeCategory) params.set('income_category', currentFilters.incomeCategory);
    if (currentFilters.dateRange.start) params.set('start_date', currentFilters.dateRange.start);
    if (currentFilters.dateRange.end) params.set('end_date', currentFilters.dateRange.end);
    if (currentFilters.amountRange.min !== '') params.set('min_amount', currentFilters.amountRange.min);
    if (currentFilters.amountRange.max !== '') params.set('max_amount', currentFilters.amountRange.max);
    
    const newURL = params.toString() ? `${window.location.pathname}?${params.toString()}` : window.location.pathname;
    window.history.replaceState({}, '', newURL);
}

function applyURLFilters() {
    const params = new URLSearchParams(window.location.search);
    
    // Set filter values from URL parameters
    const filterMappings = [
        { param: 'month', input: 'month-filter' },
        { param: 'year', input: 'year-filter' },
        { param: 'expense_category', input: 'expense-category-filter' },
        { param: 'income_category', input: 'income-category-filter' },
        { param: 'start_date', input: 'start-date-filter' },
        { param: 'end_date', input: 'end-date-filter' },
        { param: 'min_amount', input: 'min-amount-filter' },
        { param: 'max_amount', input: 'max-amount-filter' }
    ];
    
    filterMappings.forEach(mapping => {
        const value = params.get(mapping.param);
        const input = document.getElementById(mapping.input);
        if (value && input) {
            input.value = value;
        }
    });
    
    // Apply filters if any URL parameters were found
    if (params.toString()) {
        applyFilters();
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global access
window.transactionFilters = {
    applyFilters,
    clearAllFilters,
    setMonthYearFilter
};
