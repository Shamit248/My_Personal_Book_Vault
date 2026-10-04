/**
 * MY PERSONAL BOOK VAULT — ENHANCED CLIENT-SIDE SCRIPTS
 * Comprehensive, accessible, interactive features:
 * - Theme Switcher (High-Contrast Light / Dark Mode with persistence)
 * - Stackable Toast Notification System
 * - Table Column Sorting & Live Text Search Highlighting
 * - Keyboard Shortcuts (Ctrl+K, Esc, N, D)
 * - Interactive 3D Book Cover Hover Effects
 * - Live Reading Progress & Percentage Calculator
 * - Textarea Character Counters
 * - Accessible Custom Confirmation Modal
 * - Copy Citation & Book Metadata to Clipboard
 */

(function () {
  'use strict';

  /* ==========================================================================
     1. THEME MANAGER (Forest Light & Deep Obsidian Dark)
     ========================================================================== */
  const THEME_KEY = 'vault_theme_pref';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* ignore storage restrictions */
    }

    // Update all theme toggle button icons
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = theme === 'dark' ? 'ti ti-sun' : 'ti ti-moon';
      }
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    });
  }

  function initTheme() {
    let savedTheme = null;
    try {
      savedTheme = localStorage.getItem(THEME_KEY);
    } catch (e) {}

    if (!savedTheme) {
      savedTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    applyTheme(savedTheme);

    // Watch for system preference changes if user hasn't set an explicit preference
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        let currentLocal = null;
        try { currentLocal = localStorage.getItem(THEME_KEY); } catch (err) {}
        if (!currentLocal) {
          applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    }

    // Bind theme buttons
    document.addEventListener('click', (e) => {
      const toggle = e.target.closest('.theme-toggle-btn');
      if (toggle) {
        const cur = document.documentElement.getAttribute('data-theme') || 'light';
        const next = cur === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        showToast(next === 'dark' ? 'Dark mode enabled' : 'Light mode enabled', 'info', 2200);
      }
    });
  }

  /* ==========================================================================
     2. DYNAMIC STACKABLE TOAST NOTIFICATIONS
     ========================================================================== */
  let toastContainer = null;

  function ensureToastContainer() {
    if (!toastContainer || !document.body.contains(toastContainer)) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-stack-container';
      toastContainer.setAttribute('role', 'region');
      toastContainer.setAttribute('aria-label', 'System notifications');
      toastContainer.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastContainer);
    }
    return toastContainer;
  }

  window.showToast = function (message, type = 'info', duration = 3500) {
    const container = ensureToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;
    toast.setAttribute('role', 'alert');

    let iconClass = 'ti ti-info-circle';
    if (type === 'success') iconClass = 'ti ti-circle-check';
    if (type === 'danger' || type === 'error') iconClass = 'ti ti-alert-triangle';
    if (type === 'warning') iconClass = 'ti ti-alert-circle';

    toast.innerHTML = `
      <div class="toast-icon-wrap"><i class="${iconClass}" aria-hidden="true"></i></div>
      <div class="toast-message">${message}</div>
      <button type="button" class="toast-close-btn" aria-label="Close notification">
        <i class="ti ti-x" aria-hidden="true"></i>
      </button>
      <div class="toast-timer-line" style="animation-duration: ${duration}ms"></div>
    `;

    container.appendChild(toast);

    // Entrance animation
    requestAnimationFrame(() => {
      toast.classList.add('toast-visible');
    });

    let dismissTimeout;
    function removeToast() {
      clearTimeout(dismissTimeout);
      toast.classList.remove('toast-visible');
      toast.classList.add('toast-hiding');
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 250);
    }

    dismissTimeout = setTimeout(removeToast, duration);

    toast.querySelector('.toast-close-btn').addEventListener('click', removeToast);

    // Pause timer on hover
    toast.addEventListener('mouseenter', () => {
      clearTimeout(dismissTimeout);
      const bar = toast.querySelector('.toast-timer-line');
      if (bar) bar.style.animationPlayState = 'paused';
    });

    toast.addEventListener('mouseleave', () => {
      dismissTimeout = setTimeout(removeToast, 1500);
      const bar = toast.querySelector('.toast-timer-line');
      if (bar) bar.style.animationPlayState = 'running';
    });
  };

  /* ==========================================================================
     3. TABLE COLUMN SORTING & LIVE TEXT HIGHLIGHTING
     ========================================================================== */
  function initTableSorting() {
    const table = document.querySelector('.vault-table');
    if (!table) return;

    const headers = table.querySelectorAll('th[data-sortable]');
    const tbody = table.querySelector('tbody');
    if (!tbody || headers.length === 0) return;

    headers.forEach(header => {
      header.classList.add('th-sortable');
      header.setAttribute('tabindex', '0');
      header.setAttribute('role', 'button');
      header.setAttribute('aria-sort', 'none');

      // Add indicator span
      if (!header.querySelector('.sort-indicator')) {
        const ind = document.createElement('span');
        ind.className = 'sort-indicator';
        ind.innerHTML = '<i class="ti ti-arrows-sort"></i>';
        header.appendChild(ind);
      }

      function handleSort() {
        const colKey = header.getAttribute('data-col');
        const currentDir = header.getAttribute('aria-sort');
        const nextDir = currentDir === 'ascending' ? 'descending' : 'ascending';

        // Reset all headers
        headers.forEach(h => {
          h.setAttribute('aria-sort', 'none');
          const i = h.querySelector('.sort-indicator i');
          if (i) i.className = 'ti ti-arrows-sort';
        });

        header.setAttribute('aria-sort', nextDir);
        const icon = header.querySelector('.sort-indicator i');
        if (icon) {
          icon.className = nextDir === 'ascending' ? 'ti ti-arrow-up' : 'ti ti-arrow-down';
        }

        const rows = Array.from(tbody.querySelectorAll('tr.book-row'));

        rows.sort((rowA, rowB) => {
          let valA = '';
          let valB = '';

          if (colKey === 'title') {
            valA = (rowA.querySelector('.book-title-link')?.textContent || '').trim().toLowerCase();
            valB = (rowB.querySelector('.book-title-link')?.textContent || '').trim().toLowerCase();
            return nextDir === 'ascending' ? valA.localeCompare(valB) : valB.localeCompare(valA);
          } else if (colKey === 'author') {
            valA = (rowA.querySelector('.author-name')?.textContent || '').trim().toLowerCase();
            valB = (rowB.querySelector('.author-name')?.textContent || '').trim().toLowerCase();
            return nextDir === 'ascending' ? valA.localeCompare(valB) : valB.localeCompare(valA);
          } else if (colKey === 'status') {
            valA = (rowA.getAttribute('data-status') || '').toLowerCase();
            valB = (rowB.getAttribute('data-status') || '').toLowerCase();
            return nextDir === 'ascending' ? valA.localeCompare(valB) : valB.localeCompare(valA);
          } else if (colKey === 'rating') {
            valA = Number(rowA.querySelector('.book-title-link')?.getAttribute('data-rating')) || 0;
            valB = Number(rowB.querySelector('.book-title-link')?.getAttribute('data-rating')) || 0;
            return nextDir === 'ascending' ? valA - valB : valB - valA;
          } else if (colKey === 'progress') {
            const pctA = parseInt(rowA.querySelector('.progress-pct')?.textContent) || 0;
            const pctB = parseInt(rowB.querySelector('.progress-pct')?.textContent) || 0;
            return nextDir === 'ascending' ? pctA - pctB : pctB - pctA;
          }
          return 0;
        });

        rows.forEach(r => tbody.appendChild(r));
      }

      header.addEventListener('click', handleSort);
      header.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleSort();
        }
      });
    });
  }

  /* Live Text Highlighting in Table */
  function highlightTextInElement(element, query) {
    if (!element) return;
    const originalText = element.getAttribute('data-original-text') || element.textContent;
    if (!element.hasAttribute('data-original-text')) {
      element.setAttribute('data-original-text', originalText);
    }

    if (!query) {
      element.textContent = originalText;
      return;
    }

    const lower = originalText.toLowerCase();
    const index = lower.indexOf(query);
    if (index === -1) {
      element.textContent = originalText;
      return;
    }

    const before = originalText.slice(0, index);
    const match = originalText.slice(index, index + query.length);
    const after = originalText.slice(index + query.length);

    element.innerHTML = `${escapeHTML(before)}<mark class="search-highlight">${escapeHTML(match)}</mark>${escapeHTML(after)}`;
  }

  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }

  function initLiveSearchHighlight() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    searchInput.addEventListener('input', function () {
      const q = this.value.trim().toLowerCase();
      document.querySelectorAll('#book-table tr.book-row').forEach(row => {
        const titleLink = row.querySelector('.book-title-link');
        const authorSpan = row.querySelector('.author-name');
        highlightTextInElement(titleLink, q);
        highlightTextInElement(authorSpan, q);
      });
    });
  }

  /* ==========================================================================
     4. KEYBOARD SHORTCUTS
     ========================================================================== */
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Don't trigger shortcuts if user is typing in an input, textarea, or select
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      const isInput = activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select' || document.activeElement.isContentEditable;

      // Ctrl+K or Cmd+K or "/" to focus search
      if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && !isInput)) {
        const search = document.getElementById('search-input') || document.querySelector('.user-search-field');
        if (search) {
          e.preventDefault();
          search.focus();
          search.select();
          showToast('Search focused (Type to filter)', 'info', 1800);
        }
      }

      // Escape to close modals or blur active search
      if (e.key === 'Escape') {
        const modal = document.getElementById('book-modal');
        if (modal && modal.style.display === 'flex') {
          modal.style.display = 'none';
          document.body.style.overflow = '';
        }
        const confirmModal = document.getElementById('custom-confirm-modal');
        if (confirmModal && confirmModal.classList.contains('active')) {
          confirmModal.classList.remove('active');
        }
        if (isInput) {
          document.activeElement.blur();
        }
      }

      // Press 'n' for New Book when not typing
      if (e.key === 'n' && !isInput && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const addBtn = document.querySelector('a[href*="book_add"]');
        if (addBtn) {
          e.preventDefault();
          showToast('Navigating to Add Book…', 'info', 1200);
          window.location.href = addBtn.href;
        }
      }
    });
  }

  /* ==========================================================================
     5. 3D CARD & COVER HOVER PHYSICS
     ========================================================================== */
  function init3DCoverEffects() {
    const cards = document.querySelectorAll('.cover-thumb-wrap, .book-card-cover-wrap, .showcase-cover-wrap');
    cards.forEach(card => {
      card.classList.add('book-cover-3d');
    });
  }

  /* ==========================================================================
     6. LIVE READING PROGRESS & PERCENTAGE CALCULATOR
     ========================================================================== */
  function initProgressCalculator() {
    const curInput = document.getElementById('current_page');
    const totalInput = document.getElementById('page_count');

    function updatePreview() {
      let cur = parseInt(curInput ? curInput.value : 0) || 0;
      let total = parseInt(totalInput ? totalInput.value : (curInput ? curInput.getAttribute('max') : 0)) || 0;

      let preview = document.getElementById('progress-calc-preview');
      if (!preview && curInput) {
        preview = document.createElement('div');
        preview.id = 'progress-calc-preview';
        preview.className = 'progress-calc-preview';
        curInput.closest('.field').appendChild(preview);
      }

      if (preview) {
        if (total > 0 && cur > 0) {
          const pct = Math.min(100, Math.round((cur / total) * 100));
          preview.innerHTML = `
            <div class="calc-indicator-row">
              <span class="calc-label"><i class="ti ti-gauge"></i> Reading Progress:</span>
              <span class="calc-pct-badge">${pct}% completed (${cur} / ${total} pp.)</span>
            </div>
            <div class="progress-track" style="margin-top: 4px; height: 5px;">
              <div class="progress-fill" style="width: ${pct}%;"></div>
            </div>
          `;
          preview.style.display = 'block';
        } else {
          preview.style.display = 'none';
        }
      }
    }

    if (curInput) curInput.addEventListener('input', updatePreview);
    if (totalInput) totalInput.addEventListener('input', updatePreview);
    if (curInput && curInput.value) updatePreview();
  }

  /* ==========================================================================
     7. TEXTAREA LIVE CHARACTER & WORD COUNTERS
     ========================================================================== */
  function initCharacterCounters() {
    document.querySelectorAll('textarea').forEach(textarea => {
      const parent = textarea.closest('.field');
      if (!parent) return;

      let counter = parent.querySelector('.char-counter');
      if (!counter) {
        counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.innerHTML = '<span class="count-words">0 words</span> • <span class="count-chars">0 characters</span>';
        parent.appendChild(counter);
      }

      function updateCount() {
        const text = textarea.value.trim();
        const chars = textarea.value.length;
        const words = text ? text.split(/\s+/).length : 0;
        counter.querySelector('.count-words').textContent = `${words} word${words !== 1 ? 's' : ''}`;
        counter.querySelector('.count-chars').textContent = `${chars} char${chars !== 1 ? 's' : ''}`;
      }

      textarea.addEventListener('input', updateCount);
      updateCount();
    });
  }

  /* ==========================================================================
     8. ACCESSIBLE CUSTOM CONFIRMATION MODAL
     ========================================================================== */
  function initCustomConfirmDialogs() {
    // Create confirm modal in DOM if not exists
    let confirmModal = document.getElementById('custom-confirm-modal');
    if (!confirmModal) {
      confirmModal = document.createElement('div');
      confirmModal.id = 'custom-confirm-modal';
      confirmModal.className = 'custom-confirm-overlay';
      confirmModal.innerHTML = `
        <div class="confirm-card-box" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
          <div class="confirm-icon-danger">
            <i class="ti ti-trash"></i>
          </div>
          <h3 id="confirm-title" class="confirm-title">Are you sure?</h3>
          <p id="confirm-msg" class="confirm-message">This item will be removed from your vault.</p>
          <div class="confirm-actions">
            <button type="button" class="btn-secondary-action" id="confirm-cancel-btn">Cancel</button>
            <button type="button" class="btn-danger-solid" id="confirm-proceed-btn">Yes, Delete</button>
          </div>
        </div>
      `;
      document.body.appendChild(confirmModal);
    }

    let activeFormToSubmit = null;

    document.addEventListener('submit', (e) => {
      const form = e.target;
      // If form has custom-confirm or action includes delete, intercept it
      if (form.getAttribute('action') && form.getAttribute('action').includes('delete')) {
        // Prevent default confirm
        if (form.hasAttribute('onsubmit')) {
          form.removeAttribute('onsubmit');
        }
        e.preventDefault();
        activeFormToSubmit = form;

        // Custom friendly title & message
        const titleEl = confirmModal.querySelector('#confirm-title');
        const msgEl = confirmModal.querySelector('#confirm-msg');
        titleEl.textContent = 'Remove from Vault?';
        msgEl.textContent = 'This action will remove the item from your library.';

        confirmModal.classList.add('active');
        confirmModal.querySelector('#confirm-cancel-btn').focus();
      }
    });

    confirmModal.querySelector('#confirm-cancel-btn').addEventListener('click', () => {
      confirmModal.classList.remove('active');
      activeFormToSubmit = null;
    });

    confirmModal.querySelector('#confirm-proceed-btn').addEventListener('click', () => {
      if (activeFormToSubmit) {
        confirmModal.classList.remove('active');
        activeFormToSubmit.submit();
      }
    });

    confirmModal.addEventListener('click', (e) => {
      if (e.target === confirmModal) {
        confirmModal.classList.remove('active');
        activeFormToSubmit = null;
      }
    });
  }

  /* ==========================================================================
     9. CLIPBOARD METADATA COPIER
     ========================================================================== */
  function initClipboardCopier() {
    document.addEventListener('click', (e) => {
      const copyBtn = e.target.closest('#m-copy-btn');
      if (copyBtn) {
        const title = document.getElementById('m-title')?.textContent || '';
        const author = document.getElementById('m-author')?.textContent || '';
        const genre = document.getElementById('m-genre')?.textContent || '';
        const progress = document.getElementById('m-progress')?.textContent || '';
        const rating = document.getElementById('m-rating-text')?.textContent || '';

        const citation = `📖 ${title} (${author})\nGenre: ${genre} | Progress: ${progress} | Rating: ${rating}\nArchived in My Personal Book Vault`;

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(citation).then(() => {
            showToast('Book details copied to clipboard!', 'success', 2500);
          }).catch(() => {
            fallbackCopy(citation);
          });
        } else {
          fallbackCopy(citation);
        }
      }
    });

    function fallbackCopy(text) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast('Book details copied to clipboard!', 'success', 2500);
    }
  }

  /* ==========================================================================
     DOCUMENT INITIALIZATION
     ========================================================================== */
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTableSorting();
    initLiveSearchHighlight();
    initKeyboardShortcuts();
    init3DCoverEffects();
    initProgressCalculator();
    initCharacterCounters();
    initCustomConfirmDialogs();
    initClipboardCopier();
  });

})();
