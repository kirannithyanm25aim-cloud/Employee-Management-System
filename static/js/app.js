/**
 * EMPLOYEE HUB - Smart Employee Management System
 * Core Client Application Script
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileNav();
    initFlashMessages();
    initEmployeeFilters();
    initViewToggle();
    initDeleteModal();
    initFormLivePreview();
    initSettingsStorage();
});

/* --------------------------------------------------------------------------
   1. Theme Management (Dark / Light Mode)
   -------------------------------------------------------------------------- */
function initTheme() {
    const savedTheme = localStorage.getItem('employeehub_theme') || 'dark';
    applyTheme(savedTheme);

    const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
    themeToggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
            showToast(`Switched to ${nextTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
        });
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('employeehub_theme', theme);

    // Update icons
    const icons = document.querySelectorAll('.theme-toggle-icon');
    icons.forEach(icon => {
        if (theme === 'light') {
            icon.className = 'fa-solid fa-moon theme-toggle-icon';
        } else {
            icon.className = 'fa-solid fa-sun theme-toggle-icon';
        }
    });

    // Update settings radio if on settings page
    const darkRadio = document.getElementById('themeDarkRadio');
    const lightRadio = document.getElementById('themeLightRadio');
    if (darkRadio && lightRadio) {
        if (theme === 'dark') darkRadio.checked = true;
        else lightRadio.checked = true;
    }
}

/* --------------------------------------------------------------------------
   2. Mobile Drawer Navigation
   -------------------------------------------------------------------------- */
function initMobileNav() {
    const toggleBtn = document.getElementById('mobileToggleBtn');
    const sidebar = document.querySelector('.app-sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (!toggleBtn || !sidebar || !backdrop) return;

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('show-mobile');
        backdrop.classList.toggle('show');
    });

    backdrop.addEventListener('click', () => {
        sidebar.classList.remove('show-mobile');
        backdrop.classList.remove('show');
    });

    // Close on navigation link click on mobile
    const navLinks = sidebar.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 991) {
                sidebar.classList.remove('show-mobile');
                backdrop.classList.remove('show');
            }
        });
    });
}

/* --------------------------------------------------------------------------
   3. Modern Toast Notification Engine
   -------------------------------------------------------------------------- */
function showToast(message, type = 'success', duration = 3800) {
    let container = document.querySelector('.toast-container-custom');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container-custom';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;

    let iconClass = 'fa-solid fa-circle-check';
    if (type === 'error') iconClass = 'fa-solid fa-circle-exclamation';
    if (type === 'info') iconClass = 'fa-solid fa-circle-info';

    toast.innerHTML = `
        <i class="${iconClass} toast-icon"></i>
        <div class="toast-message">${message}</div>
        <button type="button" class="toast-close" aria-label="Close">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;

    container.appendChild(toast);

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.style.animation = 'slideInRight 0.25s ease reverse forwards';
        setTimeout(() => toast.remove(), 250);
    });

    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideInRight 0.25s ease reverse forwards';
            setTimeout(() => toast.remove(), 250);
        }
    }, duration);
}

// Convert Django messages from DOM into modern floating toasts
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.django-flash-message');
    flashMessages.forEach(msgEl => {
        const text = msgEl.getAttribute('data-message');
        const tag = msgEl.getAttribute('data-tag') || 'success';
        const type = tag === 'error' ? 'error' : (tag === 'info' ? 'info' : 'success');
        showToast(text, type);
        msgEl.remove();
    });
}

/* --------------------------------------------------------------------------
   4. Real-time Live Search & Dynamic Filters (Employees Directory)
   -------------------------------------------------------------------------- */
function initEmployeeFilters() {
    const searchInput = document.getElementById('employeeSearchInput');
    const deptSelect = document.getElementById('deptFilterSelect');
    const statusSelect = document.getElementById('statusFilterSelect');
    const genderSelect = document.getElementById('genderFilterSelect');
    const sortSelect = document.getElementById('sortSelect');
    const resetBtn = document.getElementById('resetFiltersBtn');

    if (!searchInput && !deptSelect) return;

    function applyClientFiltering() {
        const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
        const dept = (deptSelect ? deptSelect.value : 'all').toLowerCase();
        const status = (statusSelect ? statusSelect.value : 'all').toLowerCase();
        const gender = (genderSelect ? genderSelect.value : 'all').toLowerCase();

        const tableRows = document.querySelectorAll('.employee-table-row');
        const gridCards = document.querySelectorAll('.employee-grid-card');
        let visibleCount = 0;

        // Filter Table Rows
        tableRows.forEach(row => {
            const rowText = row.getAttribute('data-search-text') || '';
            const rowDept = (row.getAttribute('data-department') || '').toLowerCase();
            const rowStatus = (row.getAttribute('data-status') || '').toLowerCase();
            const rowGender = (row.getAttribute('data-gender') || '').toLowerCase();

            const matchesQuery = !query || rowText.includes(query);
            const matchesDept = dept === 'all' || rowDept === dept;
            const matchesStatus = status === 'all' || rowStatus === status;
            const matchesGender = gender === 'all' || rowGender === gender;

            if (matchesQuery && matchesDept && matchesStatus && matchesGender) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Filter Grid Cards
        gridCards.forEach(card => {
            const cardText = card.getAttribute('data-search-text') || '';
            const cardDept = (card.getAttribute('data-department') || '').toLowerCase();
            const cardStatus = (card.getAttribute('data-status') || '').toLowerCase();
            const cardGender = (card.getAttribute('data-gender') || '').toLowerCase();

            const matchesQuery = !query || cardText.includes(query);
            const matchesDept = dept === 'all' || cardDept === dept;
            const matchesStatus = status === 'all' || cardStatus === status;
            const matchesGender = gender === 'all' || cardGender === gender;

            if (matchesQuery && matchesDept && matchesStatus && matchesGender) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });

        // Update count badge & empty state
        const countBadge = document.getElementById('visibleEmployeeCount');
        if (countBadge) {
            countBadge.textContent = visibleCount;
        }

        const emptyState = document.getElementById('employeeEmptyState');
        const tableContainer = document.getElementById('employeeTableContainer');
        const gridContainer = document.getElementById('employeeGridContainer');

        if (visibleCount === 0) {
            if (emptyState) emptyState.style.display = 'block';
            if (tableContainer) tableContainer.style.display = 'none';
            if (gridContainer) gridContainer.style.display = 'none';
        } else {
            if (emptyState) emptyState.style.display = 'none';
            const currentView = localStorage.getItem('employeehub_view') || 'table';
            if (tableContainer) tableContainer.style.display = currentView === 'table' ? 'block' : 'none';
            if (gridContainer) gridContainer.style.display = currentView === 'grid' ? 'grid' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyClientFiltering);
    }
    if (deptSelect) {
        deptSelect.addEventListener('change', applyClientFiltering);
    }
    if (statusSelect) {
        statusSelect.addEventListener('change', applyClientFiltering);
    }
    if (genderSelect) {
        genderSelect.addEventListener('change', applyClientFiltering);
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            // Sort triggers server-side or sorting logic
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort_by', sortSelect.value);
            if (searchInput && searchInput.value) currentUrl.searchParams.set('q', searchInput.value);
            if (deptSelect && deptSelect.value !== 'all') currentUrl.searchParams.set('department', deptSelect.value);
            if (statusSelect && statusSelect.value !== 'all') currentUrl.searchParams.set('status', statusSelect.value);
            if (genderSelect && genderSelect.value !== 'all') currentUrl.searchParams.set('gender', genderSelect.value);
            window.location.href = currentUrl.toString();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            if (deptSelect) deptSelect.value = 'all';
            if (statusSelect) statusSelect.value = 'all';
            if (genderSelect) genderSelect.value = 'all';
            applyClientFiltering();
        });
    }

    // Topbar global search sync
    const topSearch = document.getElementById('topbarGlobalSearch');
    if (topSearch && searchInput) {
        topSearch.addEventListener('input', (e) => {
            searchInput.value = e.target.value;
            applyClientFiltering();
        });
    }
}

/* --------------------------------------------------------------------------
   5. View Toggle (Table vs Grid Cards)
   -------------------------------------------------------------------------- */
function initViewToggle() {
    const btnTable = document.getElementById('viewTableBtn');
    const btnGrid = document.getElementById('viewGridBtn');
    const tableContainer = document.getElementById('employeeTableContainer');
    const gridContainer = document.getElementById('employeeGridContainer');

    if (!btnTable || !btnGrid || !tableContainer || !gridContainer) return;

    function setView(view) {
        localStorage.setItem('employeehub_view', view);
        if (view === 'grid') {
            btnGrid.classList.add('active');
            btnTable.classList.remove('active');
            tableContainer.style.display = 'none';
            gridContainer.style.display = 'grid';
        } else {
            btnTable.classList.add('active');
            btnGrid.classList.remove('active');
            tableContainer.style.display = 'block';
            gridContainer.style.display = 'none';
        }
    }

    const savedView = localStorage.getItem('employeehub_view') || 'table';
    setView(savedView);

    btnTable.addEventListener('click', () => setView('table'));
    btnGrid.addEventListener('click', () => setView('grid'));
}

/* --------------------------------------------------------------------------
   6. Delete Confirmation Modal
   -------------------------------------------------------------------------- */
function initDeleteModal() {
    const modalElement = document.getElementById('deleteConfirmModal');
    if (!modalElement) return;

    const modal = new bootstrap.Modal(modalElement);
    const deleteForm = document.getElementById('deleteEmployeeForm');
    const nameSpan = document.getElementById('deleteEmployeeName');
    const idSpan = document.getElementById('deleteEmployeeId');

    document.querySelectorAll('.btn-trigger-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const empId = btn.getAttribute('data-id');
            const empName = btn.getAttribute('data-name');
            const deleteUrl = btn.getAttribute('data-url');

            if (nameSpan) nameSpan.textContent = empName;
            if (idSpan) idSpan.textContent = empId;
            if (deleteForm) deleteForm.setAttribute('action', deleteUrl);

            modal.show();
        });
    });
}

/* --------------------------------------------------------------------------
   7. Live Form Preview (Add / Edit Employee)
   -------------------------------------------------------------------------- */
function initFormLivePreview() {
    const nameInput = document.getElementById('inputFullName');
    const emailInput = document.getElementById('inputEmail');
    const deptInput = document.getElementById('inputDepartment');
    const roleInput = document.getElementById('inputDesignation');
    const salaryInput = document.getElementById('inputSalary');
    const statusInput = document.getElementById('inputStatus');

    const previewAvatar = document.getElementById('previewAvatar');
    const previewName = document.getElementById('previewName');
    const previewEmail = document.getElementById('previewEmail');
    const previewRole = document.getElementById('previewRole');
    const previewDept = document.getElementById('previewDept');
    const previewSalary = document.getElementById('previewSalary');
    const previewStatus = document.getElementById('previewStatus');

    if (!nameInput || !previewName) return;

    function getInitials(name) {
        const parts = (name || '').trim().split(/\s+/).filter(Boolean);
        if (!parts.length) return 'EH';
        if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }

    const gradients = [
        'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
        'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
        'linear-gradient(135deg, #10b981 0%, #14b8a6 100%)',
        'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
        'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
    ];

    function updatePreview() {
        const nameVal = nameInput.value.trim() || 'New Employee';
        const emailVal = emailInput ? emailInput.value.trim() || 'employee@employeehub.io' : '';
        const roleVal = roleInput ? roleInput.value.trim() || 'Designation Title' : '';
        const deptVal = deptInput ? deptInput.value || 'Department' : '';
        const salaryVal = salaryInput ? salaryInput.value || '0' : '0';
        const statusVal = statusInput ? statusInput.value || 'Active' : 'Active';

        if (previewName) previewName.textContent = nameVal;
        if (previewEmail) previewEmail.textContent = emailVal;
        if (previewRole) previewRole.textContent = roleVal;
        if (previewDept) previewDept.textContent = deptVal;

        if (previewSalary) {
            const num = parseFloat(salaryVal) || 0;
            previewSalary.textContent = `$${num.toLocaleString()}`;
        }

        if (previewAvatar) {
            previewAvatar.textContent = getInitials(nameVal);
            const hash = nameVal.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
            previewAvatar.style.background = gradients[hash % gradients.length];
        }

        if (previewStatus) {
            previewStatus.className = `status-badge ${statusVal.toLowerCase().replace(' ', '-')}`;
            previewStatus.innerHTML = `<span class="status-dot"></span> ${statusVal}`;
        }
    }

    [nameInput, emailInput, deptInput, roleInput, salaryInput, statusInput].forEach(inp => {
        if (inp) {
            inp.addEventListener('input', updatePreview);
            inp.addEventListener('change', updatePreview);
        }
    });

    updatePreview();
}

/* --------------------------------------------------------------------------
   8. Settings LocalStorage Persistence
   -------------------------------------------------------------------------- */
function initSettingsStorage() {
    const adminNameInput = document.getElementById('settingsAdminName');
    const adminEmailInput = document.getElementById('settingsAdminEmail');
    const emailNotifToggle = document.getElementById('settingsEmailNotif');
    const updatesNotifToggle = document.getElementById('settingsUpdatesNotif');
    const saveBtn = document.getElementById('saveSettingsBtn');

    // Load saved settings
    const savedName = localStorage.getItem('employeehub_admin_name') || 'Admin User';
    const savedEmail = localStorage.getItem('employeehub_admin_email') || 'admin@employeehub.io';
    const savedEmailNotif = localStorage.getItem('employeehub_email_notif') !== 'false';
    const savedUpdatesNotif = localStorage.getItem('employeehub_updates_notif') !== 'false';

    // Update Topbar and Sidebar Admin displays
    const headerAdminNames = document.querySelectorAll('.display-admin-name');
    const headerAdminEmails = document.querySelectorAll('.display-admin-email');
    headerAdminNames.forEach(el => el.textContent = savedName);
    headerAdminEmails.forEach(el => el.textContent = savedEmail);

    if (adminNameInput) adminNameInput.value = savedName;
    if (adminEmailInput) adminEmailInput.value = savedEmail;
    if (emailNotifToggle) emailNotifToggle.checked = savedEmailNotif;
    if (updatesNotifToggle) updatesNotifToggle.checked = savedUpdatesNotif;

    // Listen to theme radio buttons in settings
    const darkRadio = document.getElementById('themeDarkRadio');
    const lightRadio = document.getElementById('themeLightRadio');
    if (darkRadio && lightRadio) {
        darkRadio.addEventListener('change', () => applyTheme('dark'));
        lightRadio.addEventListener('change', () => applyTheme('light'));
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            if (adminNameInput) localStorage.setItem('employeehub_admin_name', adminNameInput.value.trim());
            if (adminEmailInput) localStorage.setItem('employeehub_admin_email', adminEmailInput.value.trim());
            if (emailNotifToggle) localStorage.setItem('employeehub_email_notif', emailNotifToggle.checked);
            if (updatesNotifToggle) localStorage.setItem('employeehub_updates_notif', updatesNotifToggle.checked);

            headerAdminNames.forEach(el => el.textContent = adminNameInput.value.trim() || 'Admin User');
            headerAdminEmails.forEach(el => el.textContent = adminEmailInput.value.trim() || 'admin@employeehub.io');

            showToast('Preferences updated and saved locally!', 'success');
        });
    }
}
