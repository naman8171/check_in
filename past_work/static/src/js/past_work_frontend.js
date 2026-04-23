/* ══════════════════════════════════════════════════════════
   Past Work — Frontend JS
   - Portfolio grid category filtering (no isotope dep needed)
   - Smooth show/hide with CSS transitions
   - Keeps filter in URL so server + client filters stay in sync
══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initPortfolioFilter();
    });

    function initPortfolioFilter() {
        var filterBtns = document.querySelectorAll('.pw-filter-btn');
        var filterLinks = document.querySelectorAll('.pw-filter-link');
        var gridItems  = document.querySelectorAll('.pw-portfolio-item');

        if (!filterBtns.length || !gridItems.length || !filterLinks.length) return;

        filterLinks.forEach(function (link) {
            link.addEventListener('click', function (event) {
                event.preventDefault();

                var parentBtn = link.closest('.pw-filter-btn');
                var filter = link.getAttribute('data-filter') || '*';
                var slug = link.getAttribute('data-filter-slug') || '*';

                // ── Update active button ──
                filterBtns.forEach(function (b) { b.classList.remove('active'); });
                if (parentBtn) {
                    parentBtn.classList.add('active');
                }

                // ── Filter items ──
                gridItems.forEach(function (item) {
                    if (filter === '*') {
                        showItem(item);
                    } else {
                        var cls = filter.replace('.', '');
                        if (item.classList.contains(cls)) {
                            showItem(item);
                        } else {
                            hideItem(item);
                        }
                    }
                });

                updateFilterInUrl(slug);
                relayout();
            });
        });
    }

    function updateFilterInUrl(slug) {
        if (!window.history || !window.history.replaceState) {
            return;
        }

        var url = new URL(window.location.href);
        if (!slug || slug === '*') {
            url.searchParams.delete('filter');
        } else {
            url.searchParams.set('filter', slug);
        }
        window.history.replaceState({}, '', url.toString());
    }

    function showItem(item) {
        item.style.display = '';
        requestAnimationFrame(function () {
            item.classList.remove('pw-hidden');
        });
    }

    function hideItem(item) {
        item.classList.add('pw-hidden');
        // After transition, hide from flow
        item.addEventListener('transitionend', function handler() {
            if (item.classList.contains('pw-hidden')) {
                item.style.display = 'none';
            }
            item.removeEventListener('transitionend', handler);
        });
    }

    /**
     * A simple relayout nudge: toggle a class on the grid parent
     * to force the browser to recalculate flex/grid gaps.
     */
    function relayout() {
        var grid = document.getElementById('pwGrid');
        if (!grid) return;
        grid.classList.add('pw-relayout');
        setTimeout(function () { grid.classList.remove('pw-relayout'); }, 50);
    }

})();
