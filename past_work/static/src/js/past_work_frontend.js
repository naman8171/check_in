/* ══════════════════════════════════════════════════════════
   Past Work — Frontend JS
   - Portfolio grid category filtering (no isotope dep needed)
   - Smooth show/hide with CSS transitions
══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initPortfolioFilter();
    });

    function initPortfolioFilter() {
        var filterBtns = document.querySelectorAll('.pw-filter-btn');
        var gridItems  = document.querySelectorAll('.pw-portfolio-item');

        if (!filterBtns.length || !gridItems.length) return;

        filterBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var filter = btn.getAttribute('data-filter');

                // ── Update active button ──
                filterBtns.forEach(function (b) { b.classList.remove('active'); });
                btn.classList.add('active');

                // ── Filter items ──
                gridItems.forEach(function (item) {
                    if (filter === '*') {
                        showItem(item);
                    } else {
                        // filter looks like ".filter-branding"
                        var cls = filter.replace('.', '');
                        if (item.classList.contains(cls)) {
                            showItem(item);
                        } else {
                            hideItem(item);
                        }
                    }
                });

                // ── Re-layout grid to avoid gaps ──
                relayout();
            });
        });
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
