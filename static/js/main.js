// Utility functions for the accounting system

// Format numbers as currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: 'EGP'
    }).format(amount);
}

// Format numbers with thousand separators
function formatNumber(number) {
    return new Intl.NumberFormat('ar-EG').format(number);
}

// Format dates to Arabic format
function formatDate(date) {
    return new Date(date).toLocaleDateString('ar-EG');
}

// Calculate total from a list of numbers
function calculateTotal(numbers) {
    return numbers.reduce((a, b) => a + (parseFloat(b) || 0), 0);
}

// Handle form submission with AJAX
function handleFormSubmit(formId, successCallback) {
    $(formId).on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const url = form.attr('action');
        const method = form.attr('method');
        const data = new FormData(this);

        $.ajax({
            url: url,
            method: method,
            data: data,
            processData: false,
            contentType: false,
            success: function(response) {
                if (successCallback) {
                    successCallback(response);
                }
            },
            error: function(xhr) {
                const errors = xhr.responseJSON;
                showErrors(errors);
            }
        });
    });
}

// Show error messages
function showErrors(errors) {
    Object.keys(errors).forEach(key => {
        const input = $(`[name="${key}"]`);
        input.addClass('is-invalid');
        input.siblings('.invalid-feedback').text(errors[key]);
    });
}

// Clear form errors
function clearErrors(formId) {
    const form = $(formId);
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').text('');
}

// Initialize dynamic form fields
function initDynamicFields() {
    $('.add-row').click(function() {
        const template = $(this).data('template');
        const container = $(this).data('container');
        const newRow = $(template).clone();
        $(container).append(newRow);
        updateRowNumbers();
    });

    $(document).on('click', '.remove-row', function() {
        $(this).closest('.dynamic-row').remove();
        updateRowNumbers();
    });
}

// Update row numbers in dynamic forms
function updateRowNumbers() {
    $('.dynamic-row').each(function(index) {
        $(this).find('.row-number').text(index + 1);
    });
}

// Calculate invoice totals
function calculateInvoiceTotal() {
    let subtotal = 0;
    $('.item-row').each(function() {
        const quantity = parseFloat($(this).find('.quantity').val()) || 0;
        const price = parseFloat($(this).find('.price').val()) || 0;
        const rowTotal = quantity * price;
        $(this).find('.row-total').text(formatCurrency(rowTotal));
        subtotal += rowTotal;
    });

    const taxRate = parseFloat($('#tax-rate').val()) || 0;
    const tax = subtotal * (taxRate / 100);
    const total = subtotal + tax;

    $('#subtotal').text(formatCurrency(subtotal));
    $('#tax-amount').text(formatCurrency(tax));
    $('#total').text(formatCurrency(total));
}

// Initialize tooltips and popovers
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Document ready handler
$(document).ready(function() {
    // Initialize tooltips and popovers
    initTooltips();

    // Initialize dynamic form fields
    initDynamicFields();

    // Setup invoice calculations
    $(document).on('input', '.quantity, .price, #tax-rate', calculateInvoiceTotal);

    // Clear form errors when input changes
    $(document).on('input', 'form input, form select, form textarea', function() {
        $(this).removeClass('is-invalid');
        $(this).siblings('.invalid-feedback').text('');
    });

    // Print functionality
    $('.print-button').click(function() {
        window.print();
    });
});