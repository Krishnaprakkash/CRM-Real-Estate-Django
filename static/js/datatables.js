// ===== DATATABLE INITIALIZATION AND FILTERS =====

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all DataTables
    initManagerLeadsTable();
    initManagerOppsTable();
    initManagerSalesTable();
    initSalesmanLeadsTable();
    initSalesmanOppsTable();
    initSalesmanSalesTable();
});

// ===== MANAGER TABLES =====

function initManagerLeadsTable() {
    if (!document.getElementById('manager-leads-table')) return;

    const table = $('#manager-leads-table').DataTable({
        order: [[0, 'desc']],
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        columnDefs: [{ orderable: false, targets: 6 }]
    });

    const typeCol = 3;
    const statusCol = 6;
    const salesmanCol = 5;

    setTimeout(() => populateFilters(table, typeCol, statusCol, salesmanCol, 'Leads'), 100);

    $('#typeFilterLeads, #statusFilterLeads, #salesmanFilterLeads').on('change', function() {
        filterManagerTable(table, typeCol, statusCol, salesmanCol, 'Leads');
    });

    $('#clearFiltersLeads').click(function() {
        clearFilters('Leads');
    });
}

function initManagerOppsTable() {
    if (!document.getElementById('manager-opps-table')) return;

    const table = $('#manager-opps-table').DataTable({
        order: [[0, 'desc']],
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        columnDefs: [{ orderable: false, targets: 6 }]
    });

    const typeCol = 3;
    const statusCol = 6;
    const salesmanCol = 5;

    setTimeout(() => populateFilters(table, typeCol, statusCol, salesmanCol, 'Opps'), 100);

    $('#typeFilterOpps, #statusFilterOpps, #salesmanFilterOpps').on('change', function() {
        filterManagerTable(table, typeCol, statusCol, salesmanCol, 'Opps');
    });

    $('#clearFiltersOpps').click(function() {
        clearFilters('Opps');
    });
}

function initManagerSalesTable() {
    if (!document.getElementById('manager-sales-table')) return;

    const table = $('#manager-sales-table').DataTable({
        order: [[0, 'desc']],
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        columnDefs: [{ orderable: false, targets: 6 }]
    });

    const typeCol = 3;
    const statusCol = 6;
    const salesmanCol = 5;

    setTimeout(() => populateFilters(table, typeCol, statusCol, salesmanCol, 'Sale'), 100);

    $('#typeFilterSale, #statusFilterSale, #salesmanFilterSale').on('change', function() {
        filterManagerTable(table, typeCol, statusCol, salesmanCol, 'Sale');
    });

    $('#clearFiltersSale').click(function() {
        clearFilters('Sale');
    });
}

// ===== SALESMAN TABLES =====

function initSalesmanLeadsTable() {
    if (!document.getElementById('salesman-leads-table')) return;

    const table = $('#salesman-leads-table').DataTable({
        order: [[0, 'desc']],
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        columnDefs: [{ orderable: false, targets: 4 }]
    });

    const typeCol = 3;
    const statusCol = 5;

    setTimeout(() => populateSalesmanFilters(table, typeCol, statusCol, 'Leads'), 100);

    $('#typeFilterLeads, #statusFilterLeads').on('change', function() {
        filterSalesmanTable(table, typeCol, statusCol, 'Leads');
    });

    $('#clearFiltersLeads').click(function() {
        clearSalesmanFilters('Leads');
    });
}

function initSalesmanOppsTable() {
    if (!document.getElementById('salesman-opps-table')) return;

    const table = $('#salesman-opps-table').DataTable({
        order: [[0, 'desc']],
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        columnDefs: [{ orderable: false, targets: 4 }]
    });

    const typeCol = 3;
    const statusCol = 5;

    setTimeout(() => populateSalesmanFilters(table, typeCol, statusCol, 'Opps'), 100);

    $('#typeFilterOpps, #statusFilterOpps').on('change', function() {
        filterSalesmanTable(table, typeCol, statusCol, 'Opps');
    });

    $('#clearFiltersOpps').click(function() {
        clearSalesmanFilters('Opps');
    });
}

function initSalesmanSalesTable() {
    if (!document.getElementById('salesman-sales-table')) return;

    const table = $('#salesman-sales-table').DataTable({
        order: [[0, 'desc']],
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        columnDefs: [{ orderable: false, targets: 4 }]
    });

    const typeCol = 3;
    const statusCol = 5;

    setTimeout(() => populateSalesmanFilters(table, typeCol, statusCol, 'Sale'), 100);

    $('#typeFilterSale, #statusFilterSale').on('change', function() {
        filterSalesmanTable(table, typeCol, statusCol, 'Sale');
    });

    $('#clearFiltersSale').click(function() {
        clearSalesmanFilters('Sale');
    });
}

// ===== HELPER FUNCTIONS =====

function populateFilters(table, typeCol, statusCol, salesmanCol, suffix) {
    populateFilter(`#typeFilter${suffix}`, table, typeCol);
    populateFilter(`#statusFilter${suffix}`, table, statusCol);
    populateFilter(`#salesmanFilter${suffix}`, table, salesmanCol);
}

function populateSalesmanFilters(table, typeCol, statusCol, suffix) {
    populateFilter(`#typeFilter${suffix}`, table, typeCol);
    populateFilter(`#statusFilter${suffix}`, table, statusCol);
}

function populateFilter(selector, table, colIndex) {
    const select = $(selector);
    if (!select.length) return;

    const values = [];

    table.column(colIndex).nodes().to$().each(function () {
        const cleanText = $(this).text().trim();
        if (cleanText && !values.includes(cleanText)) {
            values.push(cleanText);
        }
    });

    values.sort().forEach(val => {
        select.append(`<option value="${val}">${val}</option>`);
    });
}

function filterManagerTable(table, typeCol, statusCol, salesmanCol, suffix) {
    $.fn.dataTable.ext.search.pop();

    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        const row = table.row(dataIndex).node();
        const typeCell = $(row).find(`td:nth-child(${typeCol + 1})`).text().trim();
        const statusCell = $(row).find(`td:nth-child(${statusCol + 1})`).text().trim();
        const salesmanCell = $(row).find(`td:nth-child(${salesmanCol + 1})`).text().trim();

        return (!$(`#typeFilter${suffix}`).val() || typeCell === $(`#typeFilter${suffix}`).val()) &&
            (!$(`#statusFilter${suffix}`).val() || statusCell === $(`#statusFilter${suffix}`).val()) &&
            (!$(`#salesmanFilter${suffix}`).val() || salesmanCell === $(`#salesmanFilter${suffix}`).val());
    });

    table.draw();
}

function filterSalesmanTable(table, typeCol, statusCol, suffix) {
    $.fn.dataTable.ext.search.pop();

    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        const row = table.row(dataIndex).node();
        const typeCell = $(row).find(`td:nth-child(${typeCol + 1})`).text().trim();
        const statusCell = $(row).find(`td:nth-child(${statusCol + 1})`).text().trim();

        return (!$(`#typeFilter${suffix}`).val() || typeCell === $(`#typeFilter${suffix}`).val()) &&
            (!$(`#statusFilter${suffix}`).val() || statusCell === $(`#statusFilter${suffix}`).val());
    });

    table.draw();
}

function clearFilters(suffix) {
    $(`#typeFilter${suffix}, #statusFilter${suffix}, #salesmanFilter${suffix}`).val('').trigger('change');
}

function clearSalesmanFilters(suffix) {
    $(`#typeFilter${suffix}, #statusFilter${suffix}`).val('').trigger('change');
}


// Listings Table Initialization
document.addEventListener('DOMContentLoaded', function() {
    const listingsTable = document.getElementById('listings-table');
    
    if (listingsTable && typeof $.fn.DataTable !== 'undefined') {
        // Check if DataTable is already initialized
        if ($.fn.DataTable.isDataTable(listingsTable)) {
            // Destroy existing instance first
            $(listingsTable).DataTable().destroy();
        }
        
        // Initialize DataTable
        $(listingsTable).DataTable({
            order: [[0, 'desc']], // Sort by ID descending
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            columnDefs: [
                { orderable: false, targets: -1 } // Disable sorting on Actions column
            ],
            responsive: true,
            language: {
                search: "Search listings:",
                lengthMenu: "Show _MENU_ listings per page",
                info: "Showing _START_ to _END_ of _TOTAL_ listings",
                infoEmpty: "No listings available",
                infoFiltered: "(filtered from _MAX_ total listings)",
                emptyTable: "No listings found"
            }
        });
    }
});