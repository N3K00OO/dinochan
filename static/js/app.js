function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

const getCsrfToken = () => {
  const cookieToken = getCookie('csrftoken');
  if (cookieToken) {
    return cookieToken;
  }
  const metaToken = document.querySelector('meta[name="csrf-token"]');
  if (metaToken) {
    return metaToken.getAttribute('content');
  }
  return '';
};

const escapeHtml = (value) => {
  if (value === undefined || value === null) {
    return '';
  }
  return String(value).replace(/[&<>'"]/g, (char) => {
    switch (char) {
      case '&':
        return '&amp;';
      case '<':
        return '&lt;';
      case '>':
        return '&gt;';
      case '"':
        return '&quot;';
      case "'":
        return '&#39;';
      default:
        return char;
    }
  });
};

const formatCurrency = (value) => {
  if (value === undefined || value === null || value === '') {
    return '';
  }
  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }
  return number.toLocaleString('id-ID');
};

const escapeSelector = (value) => {
  const stringValue = String(value ?? '');
  if (typeof window !== 'undefined' && window.CSS && typeof window.CSS.escape === 'function') {
    return window.CSS.escape(stringValue);
  }
  return stringValue.replace(/([\0-\x1f\x7f-\x9f!"#$%&'()*+,./:;<=>?@[\\\]^`{|}~])/g, '\\$1');
};

const toastRootClassName =
  'pointer-events-none fixed inset-x-0 bottom-4 z-50 flex flex-col items-center gap-3 px-4 sm:px-6';

const baseToastClassName =
  'pointer-events-auto w-full max-w-md rounded-3xl border px-5 py-4 text-sm font-medium shadow-2xl shadow-slate-950/40 backdrop-blur transition-all duration-300';

const toastLevelClassNames = {
  success: 'border-emerald-400/40 bg-emerald-500/20 text-emerald-50',
  info: 'border-white/20 bg-slate-950/90 text-white',
  warning: 'border-amber-400/40 bg-amber-500/20 text-amber-50',
  error: 'border-rose-500/40 bg-rose-500/20 text-rose-50',
};

const DEFAULT_TOAST_DURATION = 3000;

const onDocumentReady = (callback) => {
  if (typeof document === 'undefined') {
    return;
  }
  if (typeof callback !== 'function') {
    return;
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback, { once: true });
  } else {
    callback();
  }
};

const ensureToastRoot = () => {
  if (typeof document === 'undefined') {
    return null;
  }
  let root = document.querySelector('[data-toast-root]');
  if (!root) {
    root = document.createElement('div');
    root.dataset.toastRoot = 'true';
    root.className = toastRootClassName;
    root.setAttribute('aria-live', 'polite');
    root.setAttribute('aria-atomic', 'false');
    document.body.appendChild(root);
  } else if (!root.classList.contains('pointer-events-none')) {
    root.className = toastRootClassName;
  }
  return root;
};

const normaliseToastLevel = (value) => {
  if (!value) {
    return 'info';
  }
  const level = String(value).toLowerCase();
  if (level.includes('error') || level.includes('danger') || level.includes('alert')) {
    return 'error';
  }
  if (level.includes('warn')) {
    return 'warning';
  }
  if (level.includes('success')) {
    return 'success';
  }
  if (level.includes('info') || level.includes('notice')) {
    return 'info';
  }
  return 'info';
};

const applyToastClasses = (toast, level) => {
  const normalisedLevel = normaliseToastLevel(level);
  const levelClasses = toastLevelClassNames[normalisedLevel] || toastLevelClassNames.info;
  toast.className = `${baseToastClassName} ${levelClasses}`;
  toast.dataset.toastLevel = normalisedLevel;
  toast.dataset.toastMessage = 'true';
  if (!toast.getAttribute('role')) {
    toast.setAttribute('role', 'status');
  }
  return normalisedLevel;
};

const hideToast = (toast) => {
  if (!toast || toast.dataset.toastHiding === 'true') {
    return;
  }
  toast.dataset.toastHiding = 'true';
  if (toast.dataset.toastTimer) {
    window.clearTimeout(Number(toast.dataset.toastTimer));
    delete toast.dataset.toastTimer;
  }
  toast.classList.add('opacity-0', 'translate-y-2', 'pointer-events-none');
  toast.addEventListener(
    'transitionend',
    () => {
      if (toast.isConnected) {
        toast.remove();
      }
    },
    { once: true }
  );
  window.setTimeout(() => {
    if (toast.isConnected) {
      toast.remove();
    }
  }, 400);
};

const resolveToastDuration = (toast, fallbackDuration) => {
  if (!toast) {
    return DEFAULT_TOAST_DURATION;
  }
  const attributeDuration = toast.getAttribute('data-toast-duration') || toast.dataset.toastDuration;
  const parsedAttribute = Number(attributeDuration);
  if (!Number.isNaN(parsedAttribute) && parsedAttribute > 0) {
    return parsedAttribute;
  }
  const parsedFallback = Number(fallbackDuration);
  if (!Number.isNaN(parsedFallback) && parsedFallback > 0) {
    return parsedFallback;
  }
  return DEFAULT_TOAST_DURATION;
};

const scheduleToastRemoval = (toast, duration) => {
  const timeout = Number(duration);
  if (!toast || Number.isNaN(timeout) || timeout <= 0) {
    return;
  }
  const timerId = window.setTimeout(() => {
    hideToast(toast);
  }, timeout);
  toast.dataset.toastTimer = String(timerId);
};

const registerToastElement = (toast, { level, duration = DEFAULT_TOAST_DURATION, animateIn = false } = {}) => {
  if (!toast) {
    return null;
  }
  const normalisedLevel = applyToastClasses(toast, level || toast.dataset.messageLevel || toast.dataset.toastLevel);
  toast.dataset.toastLevel = normalisedLevel;
  toast.addEventListener('click', () => {
    hideToast(toast);
  });
  const resolvedDuration = resolveToastDuration(toast, duration);
  toast.dataset.toastDuration = String(resolvedDuration);
  if (animateIn) {
    toast.classList.add('opacity-0', 'translate-y-2');
    requestAnimationFrame(() => {
      toast.classList.remove('opacity-0', 'translate-y-2');
    });
  }
  scheduleToastRemoval(toast, resolvedDuration);
  return toast;
};

const showToast = (message, { level = 'info', duration = DEFAULT_TOAST_DURATION } = {}) => {
  if (!message) {
    return null;
  }
  const root = ensureToastRoot();
  if (!root) {
    return null;
  }
  const toast = document.createElement('div');
  toast.textContent = message;
  root.appendChild(toast);
  return registerToastElement(toast, { level, duration, animateIn: true });
};

const bootstrapToasts = () => {
  const root = ensureToastRoot();
  if (!root) {
    return;
  }
  const existingToasts = Array.from(root.querySelectorAll('[data-toast-message]'));
  existingToasts.forEach((toast) => {
    registerToastElement(toast, {
      level: toast.dataset.messageLevel || toast.dataset.toastLevel || 'info',
      duration: DEFAULT_TOAST_DURATION,
      animateIn: false,
    });
  });
};

onDocumentReady(bootstrapToasts);

const resolveBookingElements = () => {
  if (typeof document === 'undefined') {
    return { list: null, empty: null };
  }
  return {
    list: document.querySelector('[data-booking-list]'),
    empty: document.querySelector('[data-booking-empty]'),
  };
};

const showBookingEmptyState = (elements) => {
  const { empty } = elements;
  if (!empty) {
    return;
  }
  empty.classList.remove('hidden');
};

const updateBookingEmptyState = (elements) => {
  const { list } = elements;
  if (!list) {
    return;
  }
  const remaining = list.querySelectorAll('[data-booking-card]').length;
  if (remaining === 0) {
    showBookingEmptyState(elements);
  }
};

const removeBookingCard = (bookingId, form) => {
  const elements = resolveBookingElements();
  const { list } = elements;
  if (!list) {
    return;
  }
  let card = null;
  if (bookingId) {
    const selectorId = escapeSelector(bookingId);
    card = list.querySelector(`[data-booking-card][data-booking-id="${selectorId}"]`);
  }
  if (!card && form) {
    card = form.closest('[data-booking-card]');
  }
  if (!card) {
    updateBookingEmptyState(elements);
    return;
  }
  card.classList.add('opacity-0', 'scale-95');
  card.addEventListener(
    'transitionend',
    () => {
      card.remove();
      updateBookingEmptyState(elements);
    },
    { once: true }
  );
  window.setTimeout(() => {
    if (card.isConnected) {
      card.remove();
      updateBookingEmptyState(elements);
    }
  }, 350);
};

const closeContainingModal = (element) => {
  if (!element) {
    return;
  }
  const modal = element.closest('[data-modal]');
  if (!modal) {
    return;
  }
  const dismissTrigger = modal.querySelector('[data-modal-close]');
  if (dismissTrigger) {
    dismissTrigger.click();
  } else {
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
  }
};

const prepareCancelBookingForm = (form) => {
  if (!(form instanceof HTMLFormElement) || form.dataset.cancelPrepared === 'true') {
    return;
  }
  form.dataset.cancelPrepared = 'true';
  form.addEventListener('submit', async (submitEvent) => {
    submitEvent.preventDefault();
    if (form.dataset.submitting === 'true') {
      return;
    }
    form.dataset.submitting = 'true';
    const submitButton = form.querySelector('[type="submit"]');
    if (submitButton) {
      submitButton.setAttribute('disabled', 'true');
    }
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(form),
        credentials: 'same-origin',
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      if (!data || data.success !== true) {
        throw new Error('Invalid response');
      }
      const message = data.message || 'Booking cancelled successfully.';
      removeBookingCard(data.booking_id, form);
      showToast(message, { level: 'success' });
      closeContainingModal(form);
    } catch (error) {
      showToast('Could not cancel this booking. Please try again.', { level: 'error' });
    } finally {
      form.dataset.submitting = 'false';
      if (submitButton) {
        submitButton.removeAttribute('disabled');
      }
    }
  });
};

const prepareCancelBookingForms = (root = document) => {
  if (!root) {
    return;
  }
  const forms = root.querySelectorAll('[data-cancel-booking-form]');
  forms.forEach((form) => prepareCancelBookingForm(form));
};

onDocumentReady(() => {
  prepareCancelBookingForms();
});

const prepareWishlistButton = (button) => {
  if (!(button instanceof HTMLButtonElement)) {
    return;
  }
  if (button.dataset.wishlistPrepared === 'true') {
    return;
  }
  const currentType = button.getAttribute('type');
  if (!currentType || currentType.toLowerCase() === 'submit') {
    button.setAttribute('type', 'button');
  }
  button.dataset.wishlistPrepared = 'true';
};

const prepareWishlistButtons = (root = document) => {
  if (!root || typeof root.querySelectorAll !== 'function') {
    return;
  }
  root.querySelectorAll('.wishlist-button').forEach((button) => {
    if (button instanceof HTMLButtonElement) {
      prepareWishlistButton(button);
    }
  });
};

onDocumentReady(() => {
  prepareWishlistButtons(document);
});

const updateWishlistButton = (button, wishlisted) => {
  if (!button) return;
  const svg = button.querySelector('svg');
  const path = svg ? svg.querySelector('path') : null;
  if (svg) {
    svg.setAttribute('fill', wishlisted ? '#ef4444' : 'none');
    svg.setAttribute('stroke', wishlisted ? '#ef4444' : 'currentColor');
  }
  if (path) {
    path.setAttribute('fill', wishlisted ? '#ef4444' : 'none');
    path.setAttribute('stroke', wishlisted ? '#ef4444' : 'currentColor');
  }
  button.classList.toggle('wishlist-button--active', Boolean(wishlisted));
  button.setAttribute('aria-pressed', wishlisted ? 'true' : 'false');
  const label = wishlisted ? 'Remove from wishlist' : 'Add to wishlist';
  button.setAttribute('aria-label', label);
  button.setAttribute('title', label);
  button.dataset.wishlisted = wishlisted ? 'true' : 'false';
};

const extractVenueData = (button) => {
  if (!button) return null;
  const {
    venue: id,
    venueName: name,
    venueCity: city,
    venueCategory: category,
    venuePrice: price,
    venueUrl: url,
    venueImage: image,
    venueDescription: description,
    toggleUrl,
  } = button.dataset;
  if (!id) {
    return null;
  }
  return {
    id,
    name: name || '',
    city: city || '',
    category: category || '',
    price: price || '',
    url: url || '',
    image: image || '',
    description: description || '',
    toggleUrl: toggleUrl || '',
  };
};

const applyVenueDataset = (button, venueData) => {
  if (!button || !venueData) {
    return;
  }
  if (venueData.id !== undefined && venueData.id !== null) {
    button.dataset.venue = String(venueData.id);
  }
  const mapping = {
    venueName: 'name',
    venueCity: 'city',
    venueCategory: 'category',
    venuePrice: 'price',
    venueUrl: 'url',
    venueImage: 'image',
    venueDescription: 'description',
    toggleUrl: 'toggleUrl',
  };
  Object.entries(mapping).forEach(([datasetKey, sourceKey]) => {
    if (Object.prototype.hasOwnProperty.call(venueData, sourceKey)) {
      const value = venueData[sourceKey];
      if (value !== undefined && value !== null) {
        button.dataset[datasetKey] = String(value);
      }
    }
  });
};

const createWishlistCard = (venueData) => {
  const card = document.createElement('article');
  card.className =
    'card-tilt group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl shadow-slate-950/40 backdrop-blur-xl';
  card.setAttribute('data-animate', '');
  card.dataset.wishlistItem = String(venueData.id || '');

  const image = document.createElement('img');
  image.src = venueData.image || '';
  image.alt = venueData.name || '';
  image.className = 'h-48 w-full rounded-2xl object-cover';
  card.appendChild(image);

  const header = document.createElement('div');
  header.className = 'mt-4 flex items-start justify-between';
  card.appendChild(header);

  const meta = document.createElement('div');
  header.appendChild(meta);

  const category = document.createElement('p');
  category.className = 'text-xs uppercase tracking-[0.4em] text-white/50';
  category.textContent = venueData.category || '';
  meta.appendChild(category);

  const title = document.createElement('h3');
  title.className = 'text-xl font-semibold text-white';
  title.textContent = venueData.name || '';
  meta.appendChild(title);

  const city = document.createElement('p');
  city.className = 'text-sm text-white/60';
  city.textContent = venueData.city || '';
  meta.appendChild(city);

  const form = document.createElement('form');
  form.method = 'post';
  const toggleUrl = venueData.toggleUrl || venueData.toggle_url || (venueData.id ? `/api/wishlist/${venueData.id}/toggle/` : '');
  if (toggleUrl) {
    const fallbackAction = toggleUrl.includes('/api/') ? toggleUrl.replace('/api/', '/') : toggleUrl;
    form.action = fallbackAction;
  }
  form.setAttribute('data-wishlist-form', '');
  header.appendChild(form);

  const csrfValue = getCsrfToken();
  if (csrfValue) {
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfValue;
    form.appendChild(csrfInput);
  }

  const nextInput = document.createElement('input');
  nextInput.type = 'hidden';
  nextInput.name = 'next';
  nextInput.value = `${window.location.pathname}${window.location.search || ''}`;
  form.appendChild(nextInput);

  const button = document.createElement('button');
  button.className =
    'wishlist-button wishlist-button--active rounded-full border border-white/20 bg-white/10 p-2 text-white transition hover:bg-white/20';
  button.type = 'button';
  button.setAttribute('aria-label', 'Unlove');
  button.setAttribute('aria-pressed', 'true');
  button.dataset.venue = String(venueData.id || '');
  button.dataset.wishlisted = 'true';
  button.dataset.venueName = venueData.name || '';
  button.dataset.venueCity = venueData.city || '';
  button.dataset.venueCategory = venueData.category || '';
  button.dataset.venuePrice = venueData.price || '';
  button.dataset.venueUrl = venueData.url || '';
  button.dataset.venueImage = venueData.image || '';
  button.dataset.venueDescription = venueData.description || '';
  if (toggleUrl) {
    button.dataset.toggleUrl = toggleUrl;
  }
  form.appendChild(button);
  prepareWishlistButton(button);

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('stroke-width', '1.5');
  svg.setAttribute('class', 'h-6 w-6');
  button.appendChild(svg);

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('stroke-linecap', 'round');
  path.setAttribute('stroke-linejoin', 'round');
  path.setAttribute(
    'd',
    'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z'
  );
  svg.appendChild(path);
  updateWishlistButton(button, true);

  const description = document.createElement('p');
  description.className = 'mt-2 text-sm text-white/70';
  description.textContent = venueData.description || '';
  card.appendChild(description);

  const footer = document.createElement('div');
  footer.className = 'mt-4 flex items-center justify-between';
  card.appendChild(footer);

  const priceTag = document.createElement('span');
  priceTag.className =
    'rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs uppercase tracking-widest text-white/70';
  const priceText = formatCurrency(venueData.price);
  const fallbackPrice = venueData.price ? String(venueData.price) : '';
  const combinedPrice = priceText || fallbackPrice;
  priceTag.textContent = combinedPrice ? `Rp ${combinedPrice}` : 'Rp';
  footer.appendChild(priceTag);

  const link = document.createElement('a');
  link.href = venueData.url || '#';
  link.className =
    'interactive-glow rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20';
  link.textContent = 'View product';
  link.setAttribute('data-ripple', '');
  footer.appendChild(link);

  return card;
};

const updateWishlistEmptyState = (grid, emptyState) => {
  if (!emptyState) {
    return;
  }
  const hasItems = Boolean(grid && grid.querySelector('[data-wishlist-item]'));
  if (hasItems) {
    emptyState.classList.add('hidden');
  } else {
    emptyState.classList.remove('hidden');
  }
};

const syncWishlistGrid = ({ venueId, wishlisted, venueData, wishlistItemHtml }) => {
  if (!venueId) {
    return;
  }
  const grid = document.querySelector('[data-wishlist-grid]');
  if (!grid) {
    return;
  }
  const emptyState = document.querySelector('[data-wishlist-empty]');
  const selector = `[data-wishlist-item="${escapeSelector(venueId)}"]`;
  const existingCard = grid.querySelector(selector);
  if (!wishlisted) {
    if (existingCard) {
      existingCard.remove();
    }
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  if (typeof wishlistItemHtml === 'string' && wishlistItemHtml.trim() !== '') {
    const trimmed = wishlistItemHtml.trim();
    if (existingCard) {
      existingCard.outerHTML = trimmed;
      const replacedCard = grid.querySelector(selector);
      if (replacedCard) {
        prepareWishlistButtons(replacedCard);
      }
    } else {
      const template = document.createElement('template');
      template.innerHTML = trimmed;
      const newCard = template.content.firstElementChild;
      if (newCard) {
        grid.prepend(newCard);
        prepareWishlistButtons(newCard);
      }
    }
    if (window.RagaSpace && typeof window.RagaSpace.refreshInteractive === 'function') {
      window.RagaSpace.refreshInteractive(grid);
    }
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  if (existingCard) {
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  if (!venueData) {
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  const card = createWishlistCard(venueData);
  grid.prepend(card);
  prepareWishlistButtons(card);
  if (window.RagaSpace && typeof window.RagaSpace.refreshInteractive === 'function') {
    window.RagaSpace.refreshInteractive(card);
  }
  updateWishlistEmptyState(grid, emptyState);
};

const syncWishlistButtons = ({ venueId, wishlisted, venueData }) => {
  if (!venueId) {
    return;
  }
  const selector = `.wishlist-button[data-venue="${escapeSelector(venueId)}"]`;
  document.querySelectorAll(selector).forEach((button) => {
    if (!(button instanceof HTMLElement)) {
      return;
    }
    if (button instanceof HTMLButtonElement) {
      prepareWishlistButton(button);
    }
    if (venueData) {
      applyVenueDataset(button, venueData);
    }
    updateWishlistButton(button, wishlisted);
  });
};

document.addEventListener('wishlist:changed', (event) => {
  if (!event.detail) {
    return;
  }
  syncWishlistGrid(event.detail);
  syncWishlistButtons(event.detail);
  prepareWishlistButtons(document);
});

function toggleWishlist(button) {
  const venueId = button.dataset.venue;
  if (!venueId || button.dataset.loading === 'true') {
    return;
  }

  const initialScrollX = typeof window !== 'undefined' ? window.scrollX : 0;
  const initialScrollY = typeof window !== 'undefined' ? window.scrollY : 0;
  const restoreScrollPosition = () => {
    if (typeof window === 'undefined') {
      return;
    }
    const applyScroll = () => {
      window.scrollTo(initialScrollX, initialScrollY);
    };
    if (typeof window.requestAnimationFrame === 'function') {
      window.requestAnimationFrame(applyScroll);
    } else {
      window.setTimeout(applyScroll, 0);
    }
  };

  const previousState = button.getAttribute('aria-pressed') === 'true';
  const desiredState = !previousState;
  const csrfToken = getCsrfToken();
  const toggleUrl = button.dataset.toggleUrl || `/api/wishlist/${venueId}/toggle/`;
  const form = button.closest('[data-wishlist-form]');
  const nextInput = form ? form.querySelector('input[name="next"]') : null;
  const nextValue = nextInput
    ? nextInput.value
    : `${window.location.pathname}${window.location.search || ''}`;

  button.dataset.loading = 'true';
  updateWishlistButton(button, desiredState);
  

  const payload = {};
  if (nextValue) {
    payload.next = nextValue;
  }

  fetch(toggleUrl, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  })
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
        throw new Error('Authentication required');
      }
      if (!response.ok) {
        throw new Error(`Wishlist toggle failed with status ${response.status}`);
      }
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        throw new Error('Unexpected response format');
      }
      return response.json();
    })
    .then((data) => {
      const wishlisted = Boolean(data && data.wishlisted);
      const fallbackVenueData = extractVenueData(button) || { id: venueId };
      const serverVenue = data && typeof data.venue === 'object' && data.venue !== null ? data.venue : null;
      const venueData = {
        ...fallbackVenueData,
        ...(serverVenue || {}),
      };
      if (!venueData.id) {
        venueData.id = venueId;
      }
      if (serverVenue && typeof serverVenue.toggle_url === 'string') {
        venueData.toggleUrl = serverVenue.toggle_url;
      }
      if (!venueData.toggleUrl && venueData.id) {
        venueData.toggleUrl = `/api/wishlist/${venueData.id}/toggle/`;
      }
      const wishlistItemHtml =
        data && typeof data.wishlist_item_html === 'string' ? data.wishlist_item_html : null;
      const wishlistCount =
        data && typeof data.wishlist_count === 'number' ? data.wishlist_count : null;
      applyVenueDataset(button, venueData);
      updateWishlistButton(button, wishlisted);
      document.dispatchEvent(
        new CustomEvent('wishlist:changed', {
          detail: {
            venueId: String(venueData.id),
            wishlisted,
            venueData,
            wishlistItemHtml,
            wishlistCount,
          },
        })
      );
      const venueName = venueData.name && venueData.name.trim() ? venueData.name : 'venue';
      const toastMessage = wishlisted
        ? `Added ${venueName} to your wishlist.`
        : `Removed ${venueName} from your wishlist.`;
      showToast(toastMessage, { level: wishlisted ? 'success' : 'info', duration: 1000 });
    })
    .catch((error) => {
      updateWishlistButton(button, previousState);
      console.error('Wishlist toggle failed', error);
      if (error && error.message === 'Authentication required') {
        return;
      }
      showToast('Unable to update your wishlist right now. Please try again.', { level: 'error', duration: 4500 });
    })
    .finally(() => {
      restoreScrollPosition();
      delete button.dataset.loading;
    });
}

document.addEventListener('click', (event) => {
  const button = event.target.closest('.wishlist-button');
  if (button) {
    event.preventDefault();
    toggleWishlist(button);
  }
});

document.addEventListener('submit', (event) => {
  const form = event.target;
  if (form.matches('[data-wishlist-form]')) {
    event.preventDefault();
    const button = form.querySelector('.wishlist-button');
    if (button) {
      toggleWishlist(button);
    }
  }
});

document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('js-enabled');
  const navToggleButtons = document.querySelectorAll('[data-nav-toggle]');
  navToggleButtons.forEach((button) => {
    const controls = button.getAttribute('aria-controls');
    if (!controls) {
      return;
    }
    const menu = document.getElementById(controls);
    if (!menu) {
      return;
    }
    button.addEventListener('click', () => {
      const expanded = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      if (menu.classList.contains('hidden')) {
        menu.classList.remove('hidden');
      } else {
        menu.classList.add('hidden');
      }
    });
  });

  const modalStack = [];

  const openModal = (modal) => {
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    if (!modalStack.includes(modal)) {
      modalStack.push(modal);
    }
    document.body.classList.add('overflow-hidden');
    const focusTargetId = modal.dataset.modalInitialFocus;
    let focusTarget = focusTargetId ? modal.querySelector(`#${focusTargetId}`) : null;
    if (!focusTarget) {
      focusTarget = modal.querySelector('[data-autofocus], input, select, textarea, button, a[href]');
    }
    if (focusTarget && typeof focusTarget.focus === 'function') {
      focusTarget.focus();
    }
  };

  const closeModal = (modal) => {
    if (!modal) return;
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    const index = modalStack.indexOf(modal);
    if (index >= 0) {
      modalStack.splice(index, 1);
    }
    if (modalStack.length === 0) {
      document.body.classList.remove('overflow-hidden');
    }
  };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-modal-target]');
    if (trigger) {
      const modalId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(modalId);
      if (modal) {
        event.preventDefault();
        openModal(modal);
        return;
      }
    }

    const dismiss = event.target.closest('[data-modal-close]');
    if (dismiss) {
      event.preventDefault();
      const modal = dismiss.closest('[data-modal]');
      closeModal(modal);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modalStack.length > 0) {
      event.preventDefault();
      const modal = modalStack[modalStack.length - 1];
      closeModal(modal);
    }
  });

  document.querySelectorAll('[data-modal]').forEach((modal) => {
    if (!modal.hasAttribute('aria-hidden')) {
      modal.setAttribute('aria-hidden', modal.classList.contains('hidden') ? 'true' : 'false');
    }
    const defaultOpen = modal.getAttribute('data-modal-default-open');
    if (defaultOpen && defaultOpen !== 'false') {
      openModal(modal);
    }
  });

  const animatedElements = document.querySelectorAll('[data-animate]');
  const animatedObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          animatedObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  const observeAnimated = (element) => {
    if (!element || element.dataset.animateObserved === 'true') {
      return;
    }
    animatedObserver.observe(element);
    element.dataset.animateObserved = 'true';
  };

  animatedElements.forEach((element) => observeAnimated(element));

  const attachRipple = (element) => {
    if (!element || element.dataset.rippleBound === 'true') {
      return;
    }
    element.dataset.rippleBound = 'true';
    if (!element.classList.contains('relative')) {
      element.classList.add('relative');
    }
    element.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey) {
        return;
      }
      if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
      }
      const rect = element.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      ripple.style.left = `${event.clientX - rect.left}px`;
      ripple.style.top = `${event.clientY - rect.top}px`;
      element.appendChild(ripple);
      window.setTimeout(() => {
        ripple.remove();
      }, 750);
    });
  };

  document.querySelectorAll('.interactive-glow, [data-ripple]').forEach((element) => attachRipple(element));

  const transitionOverlay = document.getElementById('page-transition');
  const pageShell = document.querySelector('[data-page-shell]');

  const revealPageShell = () => {
    if (!pageShell) return;
    pageShell.classList.remove('is-leaving');
    pageShell.classList.remove('opacity-0');
    window.requestAnimationFrame(() => {
      pageShell.style.removeProperty('opacity');
      pageShell.style.removeProperty('filter');
      pageShell.style.removeProperty('transform');
      pageShell.classList.add('is-ready');
    });
  };

  const hideTransition = () => {
    if (!transitionOverlay) return;
    transitionOverlay.classList.remove('opacity-100', 'pointer-events-auto');
    transitionOverlay.classList.add('opacity-0', 'pointer-events-none');
    window.setTimeout(() => {
      transitionOverlay.classList.add('invisible');
    }, 400);
    revealPageShell();
  };

  const showTransition = () => {
    if (!transitionOverlay) return;
    transitionOverlay.classList.remove('pointer-events-none', 'opacity-0', 'invisible');
    transitionOverlay.classList.add('opacity-100', 'pointer-events-auto');
    if (pageShell) {
      pageShell.classList.remove('is-ready');
      pageShell.classList.add('is-leaving');
    }
  };

  revealPageShell();
  hideTransition();
  window.addEventListener('pageshow', () => hideTransition());
  window.addEventListener('beforeunload', () => showTransition());

  document.addEventListener('click', (event) => {
    if (event.defaultPrevented) {
      return;
    }
    const anchor = event.target.closest('a[href]');
    if (!anchor) {
      return;
    }
    if (anchor.dataset.modalTarget || anchor.hasAttribute('data-modal-target')) {
      return;
    }
    const href = anchor.getAttribute('href');
    if (!href || href.startsWith('#')) {
      return;
    }
    if (anchor.target && anchor.target !== '_self') {
      return;
    }
    if (anchor.host && anchor.host !== window.location.host) {
      return;
    }
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }
    showTransition();
    event.preventDefault();
    window.setTimeout(() => {
      window.location.href = anchor.href;
    }, 320);
  });

  document.addEventListener('submit', (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }
    if (event.defaultPrevented) {
      return;
    }
    if (form.dataset.noTransition === 'true') {
      return;
    }
    if (form.target && form.target !== '_self') {
      return;
    }
    showTransition();
  });

  const refreshInteractive = (root = document) => {
    const scope = root instanceof Element ? root : document;
    scope.querySelectorAll('[data-animate]').forEach((element) => observeAnimated(element));
    scope.querySelectorAll('.interactive-glow, [data-ripple]').forEach((element) => attachRipple(element));
  };

  window.RagaSpace = window.RagaSpace || {};
  window.RagaSpace.refreshInteractive = refreshInteractive;
});

const filterForm = document.querySelector('#catalog-filter-form');
if (filterForm) {
  filterForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const params = new URLSearchParams(new FormData(filterForm));
    fetch(`/api/catalog/filter/?${params.toString()}`, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const grid = document.querySelector('#catalog-grid');
        if (!grid) return;
        grid.innerHTML = '';
        if (data.venues.length === 0) {
          grid.innerHTML = '<p class="text-white/70">No venues match your filters yet.</p>';
          return;
        }
        data.venues.forEach((venue) => {
          const card = document.createElement('article');
          card.className = 'card-tilt group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-slate-950/40 backdrop-blur-xl transition hover:bg-white/10';
          card.setAttribute('data-animate', '');
          const wishlistedClass = venue.wishlisted ? 'wishlist-button--active' : '';
          const heartFill = venue.wishlisted ? '#ef4444' : 'none';
          const heartStroke = venue.wishlisted ? '#ef4444' : 'currentColor';
          const wishlistedState = venue.wishlisted ? 'true' : 'false';
          const priceDisplay = formatCurrency(venue.price);
          card.innerHTML = `
            <div class="relative">
              <img src="${escapeHtml(venue.image_url)}" alt="${escapeHtml(venue.name)}" class="h-48 w-full rounded-2xl object-cover" />
              <button data-venue="${escapeHtml(venue.id)}" data-wishlisted="${wishlistedState}" data-venue-name="${escapeHtml(venue.name)}" data-venue-city="${escapeHtml(venue.city)}" data-venue-category="${escapeHtml(venue.category)}" data-venue-price="${escapeHtml(venue.price)}" data-venue-url="${escapeHtml(venue.url)}" data-venue-image="${escapeHtml(venue.image_url)}" data-venue-description="${escapeHtml(venue.description || '')}" data-toggle-url="${escapeHtml(venue.toggle_url)}" class="wishlist-button ${wishlistedClass} absolute right-3 top-3 rounded-full border border-white/30 bg-white/10 p-2 text-white transition hover:bg-white/20" aria-label="Toggle wishlist" aria-pressed="${wishlistedState}">
                <svg xmlns="http://www.w3.org/2000/svg" fill="${heartFill}" viewBox="0 0 24 24" stroke-width="1.5" stroke="${heartStroke}" class="h-6 w-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>
              </button>
            </div>
            <div class="mt-4 flex flex-col gap-2">
              <p class="text-xs uppercase tracking-[0.4em] text-white/50">${escapeHtml(venue.category)}</p>
              <h3 class="text-xl font-semibold text-white">${escapeHtml(venue.name)}</h3>
              <p class="text-sm text-white/60">${escapeHtml(venue.city)}</p>
            </div>
            <div class="mt-4 flex items-center justify-between">
              <span class="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs uppercase tracking-widest text-white/70">Rp ${escapeHtml(priceDisplay)}</span>
              <a href="${escapeHtml(venue.url)}" class="interactive-glow rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20" data-ripple>View product</a>
            </div>
          `;
          grid.appendChild(card);
        });
        if (window.RagaSpace && typeof window.RagaSpace.refreshInteractive === 'function') {
          window.RagaSpace.refreshInteractive(grid);
        }
      })
      .catch((error) => console.error('Filter failed', error));
  });
}
