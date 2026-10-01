/**
 * CreatorOS Core JavaScript
 * Handles Splash Screen, Offline Detection, and Navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
  initSplashScreen();
  initSidebarToggle();
  initSidebarLock();
  initRealTimeClock();
  initOfflineDetector();
  initGlobalSearch();
  initGlobalBootstrapFallbacks();
});

/* 1. Splash Screen Controller */
function initSplashScreen() {
  const splashScreen = document.getElementById('splash-screen');
  if (splashScreen) {
    setTimeout(() => {
      splashScreen.classList.add('hidden');
      setTimeout(() => splashScreen.remove(), 600);
    }, 700);
  }
}

/* 2. Mobile Sidebar Toggle */
function initSidebarToggle() {
  const sidebarBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarBtn && sidebar) {
    sidebarBtn.addEventListener('click', () => {
      sidebar.classList.toggle('active');
    });
  }
}

/* 3. Desktop Sidebar Lock
 * Lets the user stop the hover slide and keep the navigation open.
 * The state is remembered for the current browser so the layout stays consistent.
 */
function initSidebarLock() {
  const sidebar = document.querySelector('.sidebar');
  const lockBtn = document.getElementById('sidebar-lock-btn');
  const appContainer = document.querySelector('.app-container');
  if (!sidebar || !lockBtn || !appContainer) return;

  const storageKey = 'creatoros-sidebar-locked';

  function setLocked(locked) {
    sidebar.classList.toggle('sidebar-locked', locked);
    appContainer.classList.toggle('sidebar-is-locked', locked);
    lockBtn.setAttribute('aria-pressed', String(locked));
    lockBtn.title = locked ? 'Unlock sidebar' : 'Keep sidebar open';
    lockBtn.setAttribute('aria-label', locked ? 'Unlock sidebar' : 'Keep sidebar open');
    lockBtn.innerHTML = locked
      ? '<i class="bi bi-pin-angle-fill"></i>'
      : '<i class="bi bi-pin-angle"></i>';
    try { localStorage.setItem(storageKey, locked ? '1' : '0'); } catch (_) {}
  }

  let saved = false;
  try { saved = localStorage.getItem(storageKey) === '1'; } catch (_) {}
  setLocked(saved);

  lockBtn.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    setLocked(!sidebar.classList.contains('sidebar-locked'));
  });
}

/* 3. Live Clock & Date */
function initRealTimeClock() {
  const clockElement = document.getElementById('live-clock');
  if (!clockElement) return;

  function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    clockElement.innerText = timeStr;
  }

  updateClock();
  setInterval(updateClock, 1000);
}

/* 5. Network Offline / Online Detection */
function initOfflineDetector() {
  window.addEventListener('online', () => {
    showToast('Back online! Connected to CreatorOS AI services.', 'success');
  });

  window.addEventListener('offline', () => {
    showToast('Offline Mode active. Local drafts & fallback tools available.', 'warning');
  });
}

/* 6. Global Search Keyboard Shortcut */
function initGlobalSearch() {
  const searchInput = document.getElementById('global-search-input');
  if (!searchInput) return;

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
  });
}

/* Helper Toast Notification System */
function showToast(message, type = 'info') {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) return;

  const bgClass = type === 'success' ? 'bg-success text-white' : 
                  type === 'warning' ? 'bg-warning text-dark' : 
                  type === 'danger' ? 'bg-danger text-white' : 'bg-dark text-white';

  const toastHtml = `
    <div class="toast align-items-center ${bgClass} border-0 show shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body font-weight-bold">
          <i class="bi bi-info-circle-fill me-2"></i>${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  const wrapper = document.createElement('div');
  wrapper.innerHTML = toastHtml;
  const toastElement = wrapper.firstElementChild;
  toastContainer.appendChild(toastElement);

  setTimeout(() => {
    toastElement.classList.remove('show');
    setTimeout(() => toastElement.remove(), 300);
  }, 4000);
}

/* CreatorOS custom confirmation helper. Returns a Promise<boolean>. */
function creatorOSConfirm(message, options = {}) {
  return new Promise((resolve) => {
    const overlay = document.getElementById('creatoros-confirm');
    const title = document.getElementById('creatoros-confirm-title');
    const text = document.getElementById('creatoros-confirm-message');
    const cancel = document.getElementById('creatoros-confirm-cancel');
    const ok = document.getElementById('creatoros-confirm-ok');
    if (!overlay || !title || !text || !cancel || !ok) {
      // No browser confirm fallback: silently cancel rather than expose localhost/IP text.
      resolve(false);
      return;
    }

    title.textContent = options.title || 'Confirm action';
    text.textContent = message || 'Are you sure you want to continue?';
    ok.textContent = options.okText || 'Delete';
    ok.className = 'btn ' + (options.okClass || 'btn-danger');
    overlay.classList.add('show');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');

    let finished = false;
    const finish = (value) => {
      if (finished) return;
      finished = true;
      overlay.classList.remove('show');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('modal-open');
      document.removeEventListener('keydown', onKeyDown);
      overlay.removeEventListener('click', onBackdrop);
      cancel.removeEventListener('click', onCancel);
      ok.removeEventListener('click', onOk);
      resolve(value);
    };
    const onCancel = () => finish(false);
    const onOk = () => finish(true);
    const onBackdrop = (e) => { if (e.target === overlay) finish(false); };
    const onKeyDown = (e) => {
      if (e.key === 'Escape') finish(false);
      if (e.key === 'Enter') finish(true);
    };
    cancel.addEventListener('click', onCancel);
    ok.addEventListener('click', onOk);
    overlay.addEventListener('click', onBackdrop);
    document.addEventListener('keydown', onKeyDown);
    setTimeout(() => cancel.focus(), 0);
  });
}

/* 7. Bulletproof JavaScript Tab and Modal Fallbacks (No CDN dependencies) */
function initGlobalBootstrapFallbacks() {
  // Catch any document clicks to handle Modals & Tabs globally
  document.addEventListener('click', (e) => {
    const target = e.target;
    
    // A. Handle Modal toggles: data-bs-toggle="modal"
    const modalToggle = target.closest('[data-bs-toggle="modal"]');
    if (modalToggle) {
      e.preventDefault();
      const targetSelector = modalToggle.getAttribute('data-bs-target');
      const modalEl = document.querySelector(targetSelector);
      if (modalEl) {
        showCustomModal(modalEl);
      }
      return;
    }

    // B. Handle Modal dismiss/close: data-bs-dismiss="modal"
    const modalDismiss = target.closest('[data-bs-dismiss="modal"]');
    if (modalDismiss) {
      e.preventDefault();
      const modalEl = modalDismiss.closest('.modal');
      if (modalEl) {
        hideCustomModal(modalEl);
      }
      return;
    }

    // C. Handle Tab/Pill toggles: data-bs-toggle="pill" or data-bs-toggle="tab"
    const tabToggle = target.closest('[data-bs-toggle="pill"]') || target.closest('[data-bs-toggle="tab"]');
    if (tabToggle) {
      e.preventDefault();
      const targetSelector = tabToggle.getAttribute('data-bs-target');
      const targetPane = document.querySelector(targetSelector);
      
      if (targetPane) {
        // Deactivate siblings in the navigation list
        const pillNav = tabToggle.closest('.nav');
        if (pillNav) {
          pillNav.querySelectorAll('.nav-link, .btn').forEach(link => {
            link.classList.remove('active');
            link.setAttribute('aria-selected', 'false');
          });
        }
        
        // Deactivate all tab panes inside the tab content wrapper
        const tabContent = targetPane.closest('.tab-content');
        if (tabContent) {
          tabContent.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
          });
        }

        // Activate current tab button & target pane
        tabToggle.classList.add('active');
        tabToggle.setAttribute('aria-selected', 'true');
        targetPane.classList.add('show', 'active');
      }
      return;
    }

    // D. Handle Collapse/Accordion toggles: data-bs-toggle="collapse"
    const collapseToggle = target.closest('[data-bs-toggle="collapse"]');
    if (collapseToggle) {
      e.preventDefault();
      const targetSelector = collapseToggle.getAttribute('data-bs-target') || collapseToggle.getAttribute('href');
      const collapseEl = document.querySelector(targetSelector);
      
      if (collapseEl) {
        const isCollapsed = !collapseEl.classList.contains('show');
        
        // If part of an accordion, close other open sibling collapses
        const parentSelector = collapseEl.getAttribute('data-bs-parent');
        if (parentSelector && isCollapsed) {
          const parentEl = document.querySelector(parentSelector);
          if (parentEl) {
            parentEl.querySelectorAll('.accordion-collapse.show').forEach(openCollapse => {
              openCollapse.classList.remove('show');
              // Find matching toggle button and mark as collapsed
              const toggleId = openCollapse.id;
              const matchingBtn = parentEl.querySelector(`[data-bs-target="#${toggleId}"], [href="#${toggleId}"]`);
              if (matchingBtn) {
                matchingBtn.classList.add('collapsed');
                matchingBtn.setAttribute('aria-expanded', 'false');
              }
            });
          }
        }

        // Toggle state of target collapse
        if (isCollapsed) {
          collapseEl.classList.add('show');
          collapseToggle.classList.remove('collapsed');
          collapseToggle.setAttribute('aria-expanded', 'true');
        } else {
          collapseEl.classList.remove('show');
          collapseToggle.classList.add('collapsed');
          collapseToggle.setAttribute('aria-expanded', 'false');
        }
      }
    }
  });

  // Modal show utility
  function showCustomModal(modalEl) {
    modalEl.style.display = 'block';
    // Add brief timeout to trigger CSS transition
    setTimeout(() => {
      modalEl.classList.add('show');
    }, 10);
    
    // Add backdrop
    if (!document.querySelector('.modal-backdrop')) {
      const backdrop = document.createElement('div');
      backdrop.className = 'modal-backdrop fade show';
      document.body.appendChild(backdrop);
      
      // Close modal when clicking backdrop
      backdrop.addEventListener('click', () => {
        hideCustomModal(modalEl);
      });
    }
    
    document.body.classList.add('modal-open');
    document.body.style.overflow = 'hidden';
  }

  // Modal hide utility
  function hideCustomModal(modalEl) {
    modalEl.classList.remove('show');
    
    // Remove backdrop
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
      backdrop.classList.remove('show');
      setTimeout(() => backdrop.remove(), 150);
    }
    
    setTimeout(() => {
      modalEl.style.display = 'none';
    }, 150);
    
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
  }
}
