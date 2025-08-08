// Finance Manager Dashboard JavaScript
// Handles expense and category modals and form submissions

// Modal management functions
function openExpenseModal() {
  document.getElementById('expenseModal').classList.add('modal-open');
  // Set today's date as default
  document.getElementById('spent_at').value = new Date().toISOString().split('T')[0];
}

function closeExpenseModal() {
  document.getElementById('expenseModal').classList.remove('modal-open');
  setTimeout(function() {
    document.getElementById('expenseForm').reset();
  }, 200)
}

function openCategoryModal() {
  const categoryModal = document.getElementById('categoryModal');
  categoryModal.classList.add('modal-open');
  
  // Check if we're already in an edit modal and set higher z-index
  const editExpenseModal = document.getElementById('editExpenseModal');
  if (editExpenseModal && editExpenseModal.classList.contains('modal-open')) {
    categoryModal.style.zIndex = '1001';
  }
}

function closeCategoryModal() {
  const categoryModal = document.getElementById('categoryModal');
  categoryModal.classList.remove('modal-open');
  categoryModal.style.zIndex = ''; // Reset z-index

  setTimeout(function() { 
  document.getElementById('categoryForm').reset();
  
  // Reset modal to original state
    const modalTitle = document.querySelector('#categoryModal h3');
    modalTitle.innerHTML = '<i data-lucide="tag" class="w-5 h-5 inline-block mr-2"></i>Nova Categoria';
    
    const submitButton = document.querySelector('#categoryModal .btn-primary');
    submitButton.innerHTML = '<i data-lucide="save" class="w-4 h-4 mr-2"></i>Criar Categoria';  

    lucide.createIcons()

  // Remove editing ID
  document.getElementById('categoryForm').removeAttribute('data-editing-id');
  
  // Show the "add new category" button again (if it was hidden)
  const addCategoryButton = document.querySelector('#categoryModal .btn-outline');
  if (addCategoryButton) {
    addCategoryButton.style.display = '';
  }
  
  // Hide the delete button when not editing
  const deleteCategoryBtn = document.getElementById('deleteCategoryBtn');
  if (deleteCategoryBtn) {
    deleteCategoryBtn.style.display = 'none';
  }
  }, 200) 
}

function openEditExpenseModal(id, description, detailedDescription, spentAt, amount, categoryId) {
  document.getElementById('editExpenseModal').classList.add('modal-open');
  
  // Populate form fields
  document.getElementById('edit_expense_id').value = id;
  document.getElementById('edit_description').value = description;
  document.getElementById('edit_detailed_description').value = detailedDescription || '';
  document.getElementById('edit_spent_at').value = spentAt;
  document.getElementById('edit_amount').value = (amount / 100).toFixed(2); // Convert cents to reais
  document.getElementById('edit_category').value = categoryId || '';
}

function closeEditExpenseModal() {
  document.getElementById('editExpenseModal').classList.remove('modal-open');
  setTimeout(function() {
    document.getElementById('editExpenseForm').reset();
  }, 200)
}

// Income Modal Functions
function openIncomeModal() {
  document.getElementById('incomeModal').classList.add('modal-open');
  // Set today's date as default
  document.getElementById('income_received_at').value = new Date().toISOString().split('T')[0];
}

function closeIncomeModal() {
  document.getElementById('incomeModal').classList.remove('modal-open');
  setTimeout(function() {
    document.getElementById('incomeForm').reset();
  }, 200)
}

function openIncomeCategoryModal() {
  const incomeCategoryModal = document.getElementById('incomeCategoryModal');
  incomeCategoryModal.classList.add('modal-open');
  
  // Check if we're already in an edit modal and set higher z-index
  const editIncomeModal = document.getElementById('editIncomeModal');
  if (editIncomeModal && editIncomeModal.classList.contains('modal-open')) {
    incomeCategoryModal.style.zIndex = '1001';
  }
}

function closeIncomeCategoryModal() {
  const incomeCategoryModal = document.getElementById('incomeCategoryModal');
  incomeCategoryModal.classList.remove('modal-open');
  incomeCategoryModal.style.zIndex = ''; // Reset z-index

  setTimeout(function(){
    document.getElementById('incomeCategoryForm').reset();
    
    // Reset modal to original state
    const modalTitle = document.querySelector('#incomeCategoryModal h3');
    modalTitle.innerHTML = '<i data-lucide="dollar-sign" class="w-5 h-5 inline-block mr-2"></i>Nova Categoria de Renda';
    
    const submitButton = document.querySelector('#incomeCategoryModal .btn-secondary');
    submitButton.innerHTML = '<i data-lucide="save" class="w-4 h-4 mr-2"></i>Criar Categoria';

    lucide.createIcons()
  
  // Remove editing ID
  document.getElementById('incomeCategoryForm').removeAttribute('data-editing-id');
  
  // Show the "add new category" button again (if it was hidden)
  const addCategoryButton = document.querySelector('#incomeCategoryModal .btn-outline');
  if (addCategoryButton) {
    addCategoryButton.style.display = '';
  } 
  
  // Hide the delete button when not editing
  const deleteIncomeCategoryBtn = document.getElementById('deleteIncomeCategoryBtn');
  if (deleteIncomeCategoryBtn) {
    deleteIncomeCategoryBtn.style.display = 'none';
  }
  }, 200)
}

function openEditIncomeModal(id, description, detailedDescription, receivedAt, amount, categoryId) {
  document.getElementById('editIncomeModal').classList.add('modal-open');
  
  // Populate form fields
  document.getElementById('edit_income_id').value = id;
  document.getElementById('edit_income_description').value = description;
  document.getElementById('edit_income_detailed_description').value = detailedDescription || '';
  document.getElementById('edit_income_received_at').value = receivedAt;
  document.getElementById('edit_income_amount').value = (amount / 100).toFixed(2); // Convert cents to reais
  document.getElementById('edit_income_category').value = categoryId || '';
}

function closeEditIncomeModal() {
  document.getElementById('editIncomeModal').classList.remove('modal-open');
  setTimeout(function() {
    document.getElementById('editIncomeForm').reset();
  }, 200)
}

// Form submission functions
async function submitExpense() {
  const form = document.getElementById('expenseForm');
  const formData = new FormData(form);
  
  const data = {
    description: formData.get('description'),
    detailed_description: formData.get('detailed_description'),
    spent_at: formData.get('spent_at'),
    amount: formData.get('amount'),
    category_id: formData.get('category') || null
  };
  
  try {
    const response = await fetch(window.createExpenseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeExpenseModal();
      // Reload page to show new expense
      window.location.reload();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function submitCategory() {
  const form = document.getElementById('categoryForm');
  const formData = new FormData(form);
  const editingId = form.getAttribute('data-editing-id');
  
  const data = {
    name: formData.get('name'),
    description: formData.get('description'),
    color: formData.get('color')
  };
  
  try {
    let response;
    let url;
    let successMessage;
    
    if (editingId) {
      // Update existing category
      url = `/finance/category/${editingId}/edit/`;
      successMessage = 'Categoria atualizada com sucesso!';
    } else {
      // Create new category
      url = window.createCategoryUrl;
      successMessage = 'Categoria criada com sucesso!';
    }
    
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      if (editingId) {
        // Update the option in the select dropdown
        const categorySelect = document.getElementById('edit_category');
        const optionToUpdate = categorySelect.querySelector(`option[value="${editingId}"]`);
        if (optionToUpdate) {
          optionToUpdate.textContent = result.category.name;
          optionToUpdate.setAttribute('data-color', result.category.color);
        }
      } else {
        // Add new category to select dropdown
        const categorySelect = document.getElementById('category');
        const option = document.createElement('option');
        option.value = result.category.id;
        option.textContent = result.category.name;
        option.setAttribute('data-color', result.category.color);
        categorySelect.appendChild(option);
        
        // Select the new category
        categorySelect.value = result.category.id;
      }
      
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(successMessage);
      } else {
        alert(successMessage);
      }
      closeCategoryModal();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function submitEditExpense() {
  const form = document.getElementById('editExpenseForm');
  const formData = new FormData(form);
  const expenseId = formData.get('expense_id');
  
  const data = {
    description: formData.get('description'),
    detailed_description: formData.get('detailed_description'),
    spent_at: formData.get('spent_at'),
    amount: formData.get('amount'),
    category_id: formData.get('category') || null
  };
  
  try {
    const response = await fetch(`/finance/expense/${expenseId}/edit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeEditExpenseModal();
      // Reload page to show updated expense
      window.location.reload();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function deleteExpense() {

  const expenseId = document.getElementById('edit_expense_id').value;
  
  if (!confirm('Tem certeza que deseja excluir este gasto? Esta ação não pode ser desfeita.')) {
    return;
  }
  
  try {
    const response = await fetch(`/finance/expense/${expenseId}/delete/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeEditExpenseModal();
      // Reload page to reflect deletion
      window.location.reload();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function submitIncome() {
  const form = document.getElementById('incomeForm');
  const formData = new FormData(form);
  
  const data = {
    description: formData.get('description'),
    detailed_description: formData.get('detailed_description'),
    received_at: formData.get('received_at'),
    amount: formData.get('amount'),
    category_id: formData.get('category') || null
  };
  
  try {
    const response = await fetch(window.createIncomeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeIncomeModal();
      // Reload page to show new income
      window.location.reload();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function submitIncomeCategory() {
  const form = document.getElementById('incomeCategoryForm');
  const formData = new FormData(form);
  const editingId = form.getAttribute('data-editing-id');
  
  const data = {
    name: formData.get('name'),
    description: formData.get('description'),
    color: formData.get('color')
  };
  
  try {
    let response;
    let url;
    let successMessage;
    
    if (editingId) {
      // Update existing income category
      url = `/finance/income_category/${editingId}/edit/`;
      successMessage = 'Categoria de renda atualizada com sucesso!';
    } else {
      // Create new income category
      url = window.createIncomeCategoryUrl;
      successMessage = 'Categoria de renda criada com sucesso!';
    }
    
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    }
  );
    
    const result = await response.json();
    
    if (result.success) {
      if (editingId) {
        // Update the option in the select dropdown
        const categorySelect = document.getElementById('edit_income_category');
        const optionToUpdate = categorySelect.querySelector(`option[value="${editingId}"]`);
        if (optionToUpdate) {
          optionToUpdate.textContent = result.category.name;
          optionToUpdate.setAttribute('data-color', result.category.color);
        }
      } else {
        // Add new category to select dropdown
        const categorySelect = document.getElementById('income_category');
        const option = document.createElement('option');
        option.value = result.category.id;
        option.textContent = result.category.name;
        option.setAttribute('data-color', result.category.color);
        categorySelect.appendChild(option);
        
        // Select the new category
        categorySelect.value = result.category.id;
      }
      
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(successMessage);
      } else {
        alert(successMessage);
      }
      closeIncomeCategoryModal();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function submitEditIncome() {
  const form = document.getElementById('editIncomeForm');
  const formData = new FormData(form);
  const incomeId = formData.get('income_id');
  
  const data = {
    description: formData.get('description'),
    detailed_description: formData.get('detailed_description'),
    received_at: formData.get('received_at'),
    amount: formData.get('amount'),
    category_id: formData.get('category') || null
  };
  
  try {
    const response = await fetch(`/finance/income/${incomeId}/edit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeEditIncomeModal();
      // Reload page to show updated income
      window.location.reload();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

async function deleteIncome() {
  const incomeId = document.getElementById('edit_income_id').value;
  
  if (!confirm('Tem certeza que deseja excluir esta receita? Esta ação não pode ser desfeita.')) {
    return;
  }
  
  try {
    const response = await fetch(`/finance/income/${incomeId}/delete/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success toast
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeEditIncomeModal();
      // Reload page to reflect deletion
      window.location.reload();
    } else {
      // Show error toast
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

// Category editing function
function editSelectedCategory() {
  const categorySelect = document.getElementById('edit_category');
  const selectedCategoryId = categorySelect.value;
  
  if (!selectedCategoryId) {
    if (typeof toastWarning !== 'undefined') {
      toastWarning('Selecione uma categoria para editar');
    } else {
      alert('Selecione uma categoria para editar');
    }
    return;
  }
  
  // Get the selected category data
  const selectedOption = categorySelect.querySelector(`option[value="${selectedCategoryId}"]`);
  if (!selectedOption) {
    if (typeof toastError !== 'undefined') {
      toastError('Categoria não encontrada');
    } else {
      alert('Categoria não encontrada');
    }
    return;
  }
  
  const categoryName = selectedOption.textContent;
  const categoryColor = selectedOption.getAttribute('data-color') || '#3B82F6';
  
  // Open category edit modal on top of expense modal with higher z-index
  const categoryModal = document.getElementById('categoryModal');
  categoryModal.classList.add('modal-open');
  categoryModal.style.zIndex = '1001'; // Higher than expense modal
  
  // Pre-populate form with current category data
  document.getElementById('category_name').value = categoryName;
  document.getElementById('category_description').value = `Categoria para ${categoryName}`; // Auto-complete description
  document.getElementById('category_color').value = categoryColor;
  
  // Change the modal title to indicate editing
  const modalTitle = document.querySelector('#categoryModal h3');
  modalTitle.innerHTML = '<i data-lucide="pencil" class="w-5 h-5 inline-block mr-2"></i>Editar Categoria';
  
  // Change button text
  const submitButton = document.querySelector('#categoryModal .btn-primary');
  submitButton.innerHTML = '<i data-lucide="save" class="w-4 h-4 mr-2"></i>Atualizar Categoria';

  lucide.createIcons()
  
  // Store the category ID for updating
  document.getElementById('categoryForm').setAttribute('data-editing-id', selectedCategoryId);
  
  // Hide the "add new category" button in edit mode
  const addCategoryButton = document.querySelector('#categoryModal .btn-outline');
  if (addCategoryButton && addCategoryButton.onclick && addCategoryButton.onclick.toString().includes('openCategoryModal')) {
    addCategoryButton.style.display = 'none';
  }
  
  // Show the delete button in edit mode
  const deleteCategoryBtn = document.getElementById('deleteCategoryBtn');
  if (deleteCategoryBtn) {
    deleteCategoryBtn.style.display = 'inline-flex';
  }
}

// Delete category function with warning
async function deleteCategory() {
  const form = document.getElementById('categoryForm');
  const editingId = form.getAttribute('data-editing-id');
  
  if (!editingId) {
    if (typeof toastError !== 'undefined') {
      toastError('Nenhuma categoria selecionada para exclusão');
    } else {
      alert('Nenhuma categoria selecionada para exclusão');
    }
    return;
  }
  
  // Show warning about related expenses
  const confirmMessage = `⚠️ ATENÇÃO: Ao excluir esta categoria, TODOS os gastos relacionados a ela também serão excluídos permanentemente!\n\nEsta ação não pode ser desfeita.\n\nTem certeza que deseja continuar?`;
  
  if (!confirm(confirmMessage)) {
    return;
  }
  
  try {
    const response = await fetch(`/finance/category/${editingId}/delete/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeCategoryModal();
      // Reload page to reflect deletion
      window.location.reload();
    } else {
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}

// Utility functions for CSRF token handling
function getCSRFToken() {
  // First try to get from window (set in template)
  if (window.csrfToken) {
    return window.csrfToken;
  }
  
  // Fallback to hidden input
  const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (csrfInput) {
    return csrfInput.value;
  }
  
  // Fallback to cookie
  return getCookie('csrftoken');
}

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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Close modals when clicking outside
  document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
      if (event.target.id === 'expenseModal') {
        closeExpenseModal();
      } else if (event.target.id === 'categoryModal') {
        closeCategoryModal();
      } else if (event.target.id === 'editExpenseModal') {
        closeEditExpenseModal();
      } else if (event.target.id === 'incomeModal') {
        closeIncomeModal();
      } else if (event.target.id === 'incomeCategoryModal') {
        closeIncomeCategoryModal();
      } else if (event.target.id === 'editIncomeModal') {
        closeEditIncomeModal();
      }
    }
  });
  
  // Close modals on Escape key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      closeExpenseModal();
      closeCategoryModal();
      closeEditExpenseModal();
      closeIncomeModal();
      closeIncomeCategoryModal();
      closeEditIncomeModal();
    }
  });
});

// Income Category editing function
function editSelectedIncomeCategory() {
  const categorySelect = document.getElementById('edit_income_category');
  const selectedCategoryId = categorySelect.value;
  
  if (!selectedCategoryId) {
    if (typeof toastWarning !== 'undefined') {
      toastWarning('Selecione uma categoria para editar');
    } else {
      alert('Selecione uma categoria para editar');
    }
    return;
  }
  
  // Get the selected category data
  const selectedOption = categorySelect.querySelector(`option[value="${selectedCategoryId}"]`);
  if (!selectedOption) {
    if (typeof toastError !== 'undefined') {
      toastError('Categoria não encontrada');
    } else {
      alert('Categoria não encontrada');
    }
    return;
  }
  
  const categoryName = selectedOption.textContent;
  const categoryColor = selectedOption.getAttribute('data-color') || '#10B981';
  
  // Open income category modal on top of income modal with higher z-index
  const incomeCategoryModal = document.getElementById('incomeCategoryModal');
  incomeCategoryModal.classList.add('modal-open');
  incomeCategoryModal.style.zIndex = '1001'; // Higher than income modal
  
  // Pre-populate form with current category data
  document.getElementById('income_category_name').value = categoryName;
  document.getElementById('income_category_description').value = `Categoria para ${categoryName}`; // Auto-complete description
  document.getElementById('income_category_color').value = categoryColor;

  // Change the modal title to indicate editing
  const modalTitle = document.querySelector('#incomeCategoryModal h3');
  modalTitle.innerHTML = '<i data-lucide="pencil" class="w-5 h-5 inline-block mr-2"></i>Editar Categoria de Renda';
  
  // Change button text
  const submitButton = document.querySelector('#incomeCategoryModal .btn-secondary');
  submitButton.innerHTML = '<i data-lucide="save" class="w-4 h-4 mr-2"></i>Atualizar Categoria';
  
  lucide.createIcons()
  
  // Store the category ID for updating
  document.getElementById('incomeCategoryForm').setAttribute('data-editing-id', selectedCategoryId);
  
  // Hide the "add new category" button in edit mode
  const addCategoryButton = document.querySelector('#incomeCategoryModal .btn-outline');
  if (addCategoryButton && addCategoryButton.onclick && addCategoryButton.onclick.toString().includes('openIncomeCategoryModal')) {
    addCategoryButton.style.display = 'none';
  }
  
  // Show the delete button in edit mode
  const deleteIncomeCategoryBtn = document.getElementById('deleteIncomeCategoryBtn');
  if (deleteIncomeCategoryBtn) {
    deleteIncomeCategoryBtn.style.display = 'inline-flex';
  }
}

// Delete income category function with warning
async function deleteIncomeCategory() {
  const form = document.getElementById('incomeCategoryForm');
  const editingId = form.getAttribute('data-editing-id');
  
  if (!editingId) {
    if (typeof toastError !== 'undefined') {
      toastError('Nenhuma categoria selecionada para exclusão');
    } else {
      alert('Nenhuma categoria selecionada para exclusão');
    }
    return;
  }
  
  // Show warning about related incomes
  const confirmMessage = `⚠️ ATENÇÃO: Ao excluir esta categoria de renda, TODAS as receitas relacionadas a ela também serão excluídas permanentemente!\n\nEsta ação não pode ser desfeita.\n\nTem certeza que deseja continuar?`;
  
  if (!confirm(confirmMessage)) {
    return;
  }
  
  try {
    const response = await fetch(`/finance/income_category/${editingId}/delete/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      if (typeof toastSuccess !== 'undefined') {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      closeIncomeCategoryModal();
      // Reload page to reflect deletion
      window.location.reload();
    } else {
      if (typeof toastError !== 'undefined') {
        toastError(result.message);
      } else {
        alert('Erro: ' + result.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    if (typeof toastError !== 'undefined') {
      toastError('Erro ao conectar com o servidor');
    } else {
      alert('Erro ao conectar com o servidor');
    }
  }
}
