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
      } else if (event.target.id === 'importModal') {
        closeImportModal();
      } else if (event.target.id === 'exportModal') {
        closeExportModal();
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
      closeImportModal();
      closeExportModal();
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


// ============================================
// IMPORT DATA FUNCTIONALITY
// ============================================

let selectedFile = null;

function openImportModal() {
  document.getElementById("importModal").classList.add("modal-open");
  resetImportModal();
}

function closeImportModal() {
  document.getElementById("importModal").classList.remove("modal-open");
  resetImportModal();
}

function resetImportModal() {
  selectedFile = null;
  document.getElementById("import-file").value = "";
  document.getElementById("clear-existing").checked = false;
  document.getElementById("file-info").classList.add("hidden");
  document.getElementById("import-preview").classList.add("hidden");
  document.getElementById("import-progress").classList.add("hidden");
  document.getElementById("import-btn").disabled = true;
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  
  if (!file) {
    resetImportModal();
    return;
  }

  const fileName = file.name.toLowerCase();
  
  // Validate file type - unified check
  const validExtensions = ['.json', '.csv', '.xlsx', '.xls'];
  const isValidFile = validExtensions.some(ext => fileName.endsWith(ext));
  
  if (!isValidFile) {
    if (typeof toastError !== "undefined") {
      toastError("Apenas arquivos JSON, CSV e Excel são permitidos");
    } else {
      alert("Apenas arquivos JSON, CSV e Excel são permitidos");
    }
    event.target.value = "";
    return;
  }

  // Validate file size (10MB limit)
  if (file.size > 10 * 1024 * 1024) {
    if (typeof toastError !== "undefined") {
      toastError("Arquivo muito grande. Limite máximo: 10MB");
    } else {
      alert("Arquivo muito grande. Limite máximo: 10MB");
    }
    event.target.value = "";
    return;
  }

  selectedFile = file;
  
  // Show file info with detected file type
  const fileInfo = document.getElementById("file-info");
  const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
  
  let fileType;
  if (fileName.endsWith(".json")) {
    fileType = "JSON";
  } else if (fileName.endsWith(".csv")) {
    fileType = "CSV";
  } else if (fileName.endsWith(".xlsx") || fileName.endsWith(".xls")) {
    fileType = "Excel";
  }
  
  fileInfo.innerHTML = `
    <div class="flex items-center space-x-2">
      <i data-lucide="file-text" class="w-4 h-4 text-green-600"></i>
      <span><strong>${file.name}</strong> (${fileSizeMB} MB) - ${fileType}</span>
    </div>
  `;
  fileInfo.classList.remove("hidden");

  // Parse and preview file based on type
  if (fileName.endsWith(".json")) {
    parseAndPreviewJSON(file);
  } else if (fileName.endsWith(".csv")) {
    parseAndPreviewCSV(file);
  } else if (fileName.endsWith(".xlsx") || fileName.endsWith(".xls")) {
    parseAndPreviewExcel(file);
  }
}

function parseAndPreviewJSON(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const data = JSON.parse(e.target.result);
      showImportPreview(data, "JSON");
      document.getElementById("import-btn").disabled = false;
    } catch (error) {
      if (typeof toastError !== "undefined") {
        toastError("Arquivo JSON inválido: " + error.message);
      } else {
        alert("Arquivo JSON inválido: " + error.message);
      }
      resetImportModal();
    }
  };
  reader.readAsText(file);
}

function parseAndPreviewCSV(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const content = e.target.result;
      const lines = content.split('\n');
      const data = parseCSVContent(lines);
      showImportPreview(data, "CSV");
      document.getElementById("import-btn").disabled = false;
    } catch (error) {
      if (typeof toastError !== "undefined") {
        toastError("Erro ao processar arquivo CSV: " + error.message);
      } else {
        alert("Erro ao processar arquivo CSV: " + error.message);
      }
      resetImportModal();
    }
  };
  reader.readAsText(file);
}

function parseAndPreviewExcel(file) {
  // Enhanced Excel preview with actual file analysis
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      // We can't fully parse Excel in browser, but we can provide better preview
      const arrayBuffer = e.target.result;
      const data = analyzeExcelFile(arrayBuffer);
      showImportPreview(data, "Excel");
      document.getElementById("import-btn").disabled = false;
    } catch (error) {
      // Fallback to basic Excel preview
      const data = {
        expense_categories: "Será processado no servidor",
        income_categories: "Será processado no servidor", 
        expenses: "Será processado no servidor",
        incomes: "Será processado no servidor",
        fileSize: (file.size / 1024).toFixed(2) + " KB",
        lastModified: new Date(file.lastModified).toLocaleDateString('pt-BR')
      };
      showImportPreview(data, "Excel");
      document.getElementById("import-btn").disabled = false;
    }
  };
  reader.readAsArrayBuffer(file);
}

function analyzeExcelFile(arrayBuffer) {
  // Basic analysis without full parsing
  const data = {
    expense_categories: "Detectando estrutura...",
    income_categories: "Detectando estrutura...",
    expenses: "Detectando estrutura...",
    incomes: "Detectando estrutura...",
    fileInfo: {
      size: (arrayBuffer.byteLength / 1024).toFixed(2) + " KB",
      type: "Excel Workbook",
      estimatedSheets: "Múltiplas abas detectadas"
    }
  };
  
  return data;
}

function parseCSVContent(lines) {
  const data = {
    expense_categories: [],
    income_categories: [],
    expenses: [],
    incomes: []
  };

  let currentSection = null;
  let headers = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Parse CSV line (simple parsing - doesn't handle quoted commas)
    const row = line.split(',').map(cell => cell.trim().replace(/^"(.*)"$/, '$1'));

    // Check for section headers
    if (row.length >= 1) {
      if (row[0] === "EXPENSE CATEGORIES") {
        currentSection = "expense_categories";
        continue;
      } else if (row[0] === "INCOME CATEGORIES") {
        currentSection = "income_categories";
        continue;
      } else if (row[0] === "EXPENSES") {
        currentSection = "expenses";
        continue;
      } else if (row[0] === "INCOMES") {
        currentSection = "incomes";
        continue;
      }

      // Check for headers row
      if (currentSection && (row[0] === "Name" || row[0] === "Category")) {
        headers = row;
        continue;
      }
    }

    // Process data rows
    if (currentSection && headers.length > 0 && row.length >= headers.length) {
      const rowData = {};
      headers.forEach((header, index) => {
        rowData[header] = row[index] || "";
      });

      if (currentSection === "expense_categories" || currentSection === "income_categories") {
        data[currentSection].push({
          name: rowData["Name"] || "",
          description: rowData["Description"] || "",
          color: rowData["Color"] || "#FFFFFF"
        });
      } else if (currentSection === "expenses") {
        data[currentSection].push({
          category: rowData["Category"] || "",
          date: rowData["Date"] || "",
          description: rowData["Description"] || "",
          detailed_description: rowData["Detailed Description"] || "",
          amount: parseInt(rowData["Amount (cents)"]) || 0
        });
      } else if (currentSection === "incomes") {
        data[currentSection].push({
          category: rowData["Category"] || "",
          date: rowData["Date"] || "",
          description: rowData["Description"] || "",
          detailed_description: rowData["Detailed Description"] || "",
          amount: parseInt(rowData["Amount (cents)"]) || 0
        });
      }
    }
  }

  return data;
}

function showImportPreview(data, fileType) {
  const preview = document.getElementById("import-preview");
  const content = document.getElementById("preview-content");
  
  let expenseCategories, incomeCategories, expenses, incomes;
  
  if (fileType === "Excel") {
    // Enhanced Excel preview
    content.innerHTML = `
      <div>
        <div class="text-lg font-semibold mb-4 text-center">Prévia do arquivo Excel</div>
        
        <!-- File Info Section -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div class="flex items-center justify-between cursor-pointer" onclick="toggleSection('excel-info')">
            <div class="flex items-center">
              <i data-lucide="file-spreadsheet" class="w-5 h-5 text-blue-600 mr-2"></i>
              <span class="font-medium text-blue-800">Informações do Arquivo</span>
            </div>
            <i data-lucide="chevron-down" class="w-4 h-4 text-blue-600 transition-transform" id="excel-info-icon"></i>
          </div>
          <div class="hidden" id="excel-info-content" class="mt-3 space-y-2">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-blue-600 font-medium">Tamanho:</span>
                <span class="text-blue-800">${data.fileInfo?.size || 'Calculando...'}</span>
              </div>
              <div>
                <span class="text-blue-600 font-medium">Tipo:</span>
                <span class="text-blue-800">${data.fileInfo?.type || 'Excel Workbook'}</span>
              </div>
            </div>
            <div class="text-sm">
              <span class="text-blue-600 font-medium">Status:</span>
              <span class="text-blue-800">Arquivo será processado no servidor com análise completa</span>
            </div>
          </div>
        </div>

        <!-- Expected Structure Section -->
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div class="flex items-center justify-between cursor-pointer" onclick="toggleSection('excel-structure')">
            <div class="flex items-center">
              <i data-lucide="layout" class="w-5 h-5 text-green-600 mr-2"></i>
              <span class="font-medium text-green-800">Estrutura Esperada</span>
            </div>
            <i data-lucide="chevron-down" class="w-4 h-4 text-green-600 transition-transform" id="excel-structure-icon"></i>
          </div>
          <div class="hidden" id="excel-structure-content" class="mt-3">
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div class="bg-white rounded p-3 border border-green-200">
                <div class="flex items-center mb-2">
                  <div class="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                  <span class="font-medium">Expense Categories</span>
                </div>
                <div class="text-xs text-gray-600">Aba com categorias de gastos</div>
              </div>
              
              <div class="bg-white rounded p-3 border border-green-200">
                <div class="flex items-center mb-2">
                  <div class="w-3 h-3 bg-emerald-500 rounded mr-2"></div>
                  <span class="font-medium">Income Categories</span>
                </div>
                <div class="text-xs text-gray-600">Aba com categorias de receitas</div>
              </div>
              
              <div class="bg-white rounded p-3 border border-green-200">
                <div class="flex items-center mb-2">
                  <div class="w-3 h-3 bg-red-500 rounded mr-2"></div>
                  <span class="font-medium">Expenses</span>
                </div>
                <div class="text-xs text-gray-600">Aba com lista de gastos</div>
              </div>
              
              <div class="bg-white rounded p-3 border border-green-200">
                <div class="flex items-center mb-2">
                  <div class="w-3 h-3 bg-green-500 rounded mr-2"></div>
                  <span class="font-medium">Incomes</span>
                </div>
                <div class="text-xs text-gray-600">Aba com lista de receitas</div>
              </div>
            </div>
            
            <div class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
              <div class="flex items-center">
                <i data-lucide="info" class="w-4 h-4 text-yellow-600 mr-2"></i>
                <span class="text-yellow-800 font-medium">Dica:</span>
              </div>
              <div class="text-yellow-700 mt-1">
                Use arquivos exportados por este sistema para garantir compatibilidade completa.
              </div>
            </div>
          </div>
        </div>

          </div>
        </div>
      </div>
    `;
  } else {
    // Enhanced JSON/CSV preview with collapsible sections
    expenseCategories = Array.isArray(data.expense_categories) ? data.expense_categories.length : 0;
    incomeCategories = Array.isArray(data.income_categories) ? data.income_categories.length : 0;
    expenses = Array.isArray(data.expenses) ? data.expenses.length : 0;
    incomes = Array.isArray(data.incomes) ? data.incomes.length : 0;
    
    const totalRecords = expenseCategories + incomeCategories + expenses + incomes;
    
    content.innerHTML = `
      <div>
        <div class="text-lg font-semibold mb-4 text-center">Prévia dos dados (${fileType})</div>
        
        <!-- Summary Cards Section -->
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <div class="flex items-center justify-between cursor-pointer" onclick="toggleSection('summary-cards')">
            <div class="flex items-center">
              <i data-lucide="bar-chart-3" class="w-5 h-5 text-gray-600 mr-2"></i>
              <span class="font-medium text-gray-800">Resumo dos Dados</span>
            </div>
            <i data-lucide="chevron-down" class="w-4 h-4 text-gray-600 transition-transform" id="summary-cards-icon"></i>
          </div>
          <div class="hidden" id="summary-cards-content" class="mt-3">
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div class="text-blue-600 font-medium">Categorias de Gastos</div>
                <div class="text-2xl font-bold text-blue-800">${expenseCategories}</div>
                ${expenseCategories > 0 ? `<div class="text-xs text-blue-600 mt-1">Primeiras: ${getPreviewItems(data.expense_categories, 'name')}</div>` : ''}
              </div>
              
              <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <div class="text-green-600 font-medium">Categorias de Receitas</div>
                <div class="text-2xl font-bold text-green-800">${incomeCategories}</div>
                ${incomeCategories > 0 ? `<div class="text-xs text-green-600 mt-1">Primeiras: ${getPreviewItems(data.income_categories, 'name')}</div>` : ''}
              </div>
              
              <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                <div class="text-red-600 font-medium">Gastos</div>
                <div class="text-2xl font-bold text-red-800">${expenses}</div>
                ${expenses > 0 ? `<div class="text-xs text-red-600 mt-1">Primeiros: ${getPreviewItems(data.expenses, 'description')}</div>` : ''}
              </div>
              
              <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                <div class="text-emerald-600 font-medium">Receitas</div>
                <div class="text-2xl font-bold text-emerald-800">${incomes}</div>
                ${incomes > 0 ? `<div class="text-xs text-emerald-600 mt-1">Primeiras: ${getPreviewItems(data.incomes, 'description')}</div>` : ''}
              </div>
            </div>
            
            <!-- Total Summary -->
            <div class="bg-white border border-gray-300 rounded-lg p-4 text-center">
              <div class="text-gray-600">Total de registros para importar</div>
              <div class="text-3xl font-bold text-gray-800">${totalRecords}</div>
            </div>
          </div>
        </div>
        
        <!-- Detailed Preview Tables Section -->
        ${(expenseCategories > 0 || expenses > 0 || incomeCategories > 0 || incomes > 0) ? `
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between cursor-pointer" onclick="toggleSection('detailed-preview')">
            <div class="flex items-center">
              <i data-lucide="table" class="w-5 h-5 text-gray-600 mr-2"></i>
              <span class="font-medium text-gray-800">Prévia Detalhada</span>
            </div>
            <i data-lucide="chevron-down" class="w-4 h-4 text-gray-600 transition-transform" id="detailed-preview-icon"></i>
          </div>
          <div class="hidden" id="detailed-preview-content" class="mt-3">
            ${expenseCategories > 0 ? createCollapsiblePreviewTable('Categorias de Gastos', data.expense_categories.slice(0, 3), ['name', 'description', 'color'], 'expense-categories') : ''}
            ${expenses > 0 ? createCollapsiblePreviewTable('Gastos (amostra)', data.expenses.slice(0, 3), ['description', 'category', 'amount'], 'expenses') : ''}
            ${incomeCategories > 0 ? createCollapsiblePreviewTable('Categorias de Receitas', data.income_categories.slice(0, 3), ['name', 'description', 'color'], 'income-categories') : ''}
            ${incomes > 0 ? createCollapsiblePreviewTable('Receitas (amostra)', data.incomes.slice(0, 3), ['description', 'category', 'amount'], 'incomes') : ''}
          </div>
        </div>
        ` : ''}
      </div>
    `;
  }
  
  preview.classList.remove("hidden");
  
  // Initialize Lucide icons for the new elements
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

function createCollapsiblePreviewTable(title, items, fields, sectionId) {
  if (!items || items.length === 0) return '';
  
  const headers = fields.map(field => {
    switch(field) {
      case 'name': return 'Nome';
      case 'description': return 'Descrição';
      case 'color': return 'Cor';
      case 'category': return 'Categoria';
      case 'amount': return 'Valor';
      default: return field;
    }
  }).join('</th><th class="px-2 py-1 text-left text-xs font-medium text-gray-600 border">');
  
  const rows = items.map(item => {
    const cells = fields.map(field => {
      let value = item[field] || '-';
      if (field === 'amount' && typeof value === 'number') {
        value = `R$ ${(value / 100).toFixed(2)}`;
      } else if (field === 'color' && value !== '-') {
        value = `<span class="inline-block w-4 h-4 rounded border" style="background-color: ${value}"></span> ${value}`;
      }
      return value;
    }).join('</td><td class="px-2 py-1 text-xs text-gray-800 border">');
    
    return `<tr><td class="px-2 py-1 text-xs text-gray-800 border">${cells}</td></tr>`;
  }).join('');
  
  return `
    <div class="mt-4 border border-gray-200 rounded-lg overflow-hidden">
      <div class="bg-gray-50 px-3 py-2 cursor-pointer" onclick="toggleSection('${sectionId}')">
        <div class="flex items-center justify-between">
          <h4 class="font-medium text-sm text-gray-700">${title}</h4>
          <i data-lucide="chevron-down" class="w-4 h-4 text-gray-600 transition-transform" id="${sectionId}-icon"></i>
        </div>
      </div>
      <div class="hidden" id="${sectionId}-content" class="p-3">
        <div class="overflow-x-auto">
          <table class="min-w-full text-xs border-collapse border border-gray-300">
            <thead>
              <tr class="bg-gray-100">
                <th class="px-2 py-1 text-left text-xs font-medium text-gray-600 border">${headers}</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>
        ${items.length > 3 ? `<p class="text-xs text-gray-500 mt-2">Mostrando 3 de ${items.length} registros</p>` : ''}
      </div>
    </div>
  `;
}

function toggleSection(sectionId) {
  const content = document.getElementById(`${sectionId}-content`);
  const icon = document.getElementById(`${sectionId}-icon`);
  
  if (!content || !icon) return;
  
  const isHidden = content.style.display === 'none';
  
  if (isHidden) {
    content.style.display = 'block';
    icon.style.transform = 'rotate(180deg)';
  } else {
    content.style.display = 'none';
    icon.style.transform = 'rotate(0deg)';
  }
}

function getPreviewItems(items, field) {
  if (!Array.isArray(items) || items.length === 0) return 'Nenhum';
  
  const names = items.slice(0, 3).map(item => item[field] || 'Sem nome').filter(name => name && name !== 'Sem nome');
  
  if (names.length === 0) return 'Dados sem nome';
  
  let result = names.join(', ');
  if (items.length > 3) {
    result += `... (+${items.length - 3})`;
  }
  
  return result.length > 40 ? result.substring(0, 37) + '...' : result;
}

function showGenericPreview(fileType) {
  // This function is now only used as fallback
  const preview = document.getElementById("import-preview");
  const content = document.getElementById("preview-content");
  
  content.innerHTML = `
    <div class="text-center">
      <div class="text-lg font-semibold mb-2">Arquivo ${fileType} selecionado</div>
      <p class="text-gray-600">
        O arquivo será processado durante a importação. 
        Certifique-se de que está no formato correto exportado por este sistema.
      </p>
      <div class="mt-3 text-sm text-gray-500">
        <strong>Formato esperado:</strong><br>
        ${fileType === "CSV" ? "CSV com seções separadas para categorias, gastos e receitas" : "Excel com abas separadas para cada tipo de dados"}
      </div>
    </div>
  `;
  
  preview.classList.remove("hidden");
}

async function submitImport() {
  if (!selectedFile) {
    if (typeof toastError !== "undefined") {
      toastError("Nenhum arquivo selecionado");
    } else {
      alert("Nenhum arquivo selecionado");
    }
    return;
  }

  // Use unified import URL - no need to check file type
  const importUrl = window.importDataUrl;

  // Show progress
  document.getElementById("import-progress").classList.remove("hidden");
  document.getElementById("import-btn").disabled = true;

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("clear_existing", document.getElementById("clear-existing").checked);
    formData.append("csrfmiddlewaretoken", window.csrfToken);

    const response = await fetch(importUrl, {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": window.csrfToken,
      },
    });

    const result = await response.json();

    // Hide progress
    document.getElementById("import-progress").classList.add("hidden");

    if (result.success) {
      if (typeof toastSuccess !== "undefined") {
        toastSuccess(result.message);
      } else {
        alert(result.message);
      }
      
      // Close modal and reload page
      closeImportModal();
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      if (typeof toastError !== "undefined") {
        toastError(result.message);
      } else {
        alert("Erro: " + result.message);
      }
      document.getElementById("import-btn").disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("import-progress").classList.add("hidden");
    document.getElementById("import-btn").disabled = false;
    
    if (typeof toastError !== "undefined") {
      toastError("Erro ao conectar com o servidor");
    } else {
      alert("Erro ao conectar com o servidor");
    }
  }
}

// Export Modal Functions
function openExportModal() {
    document.getElementById('exportModal').classList.add('modal-open');
    // Reset to JSON as default
    document.querySelector('input[name="export-format"][value="json"]').checked = true;
}

function closeExportModal() {
    document.getElementById('exportModal').classList.remove('modal-open');
}

function executeExport() {
    const selectedFormat = document.querySelector('input[name="export-format"]:checked').value;
    
    let exportUrl;
    switch(selectedFormat) {
        case 'csv':
            exportUrl = window.exportDataCsvUrl;
            break;
        case 'excel':
            exportUrl = window.exportDataExcelUrl;
            break;
        case 'json':
        default:
            exportUrl = window.exportDataJsonUrl;
            break;
    }
    
    // Show loading state
    const exportBtn = document.querySelector('#exportModal .btn-primary');
    const originalText = exportBtn.innerHTML;
    exportBtn.innerHTML = '<span class="loading loading-spinner loading-sm mr-2"></span>Exportando...';
    exportBtn.disabled = true;
    
    // Create a temporary link to trigger download
    const link = document.createElement('a');
    link.href = exportUrl;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Reset button state after a short delay
    setTimeout(() => {
        exportBtn.innerHTML = originalText;
        exportBtn.disabled = false;
        closeExportModal();
        
        // Show success message
        if (typeof toastSuccess !== 'undefined') {
            toastSuccess('Arquivo exportado com sucesso!');
        } else {
            alert('Arquivo exportado com sucesso!');
        }
    }, 1000);
}

// Remove the old exportData function if it exists and replace with this
function exportData(format) {
    // This function is deprecated, use the modal instead
    openExportModal();
}

// Add event listeners for modal closing (including import/export modals)
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
      } else if (event.target.id === 'importModal') {
        closeImportModal();
      } else if (event.target.id === 'exportModal') {
        closeExportModal();
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
      closeImportModal();
      closeExportModal();
    }
  });
});