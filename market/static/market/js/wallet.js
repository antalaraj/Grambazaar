document.addEventListener('DOMContentLoaded', function() {
    const walletContainer = document.querySelector('[data-wallet-poll-url]');
    if (!walletContainer) return;

    const pollUrl = walletContainer.dataset.walletPollUrl;
    const pageBalanceEl = document.getElementById('wallet-balance-amount');
    const dashboardBalanceEl = document.getElementById('dashboard-wallet-balance');
    const ledgerBody = document.getElementById('ledger-body');

    function renderWallet(data) {
        if (data && typeof data.balance !== 'undefined') {
            const formatted = '₹ ' + data.balance;
            if (pageBalanceEl) pageBalanceEl.textContent = formatted;
            if (dashboardBalanceEl) dashboardBalanceEl.textContent = formatted;
        }

        if (!ledgerBody) return;

        const entries = data && Array.isArray(data.entries) ? data.entries : [];
        if (!entries.length) {
            ledgerBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted small">No ledger entries yet.</td></tr>';
            return;
        }

        let html = '';
        entries.forEach(function(e) {
            html += '<tr>' +
                '<td>' + (e.date || '') + '</td>' +
                '<td>' + (e.description || '') + '</td>' +
                '<td class="text-end">' + (e.credit ? ('₹ ' + e.credit) : '') + '</td>' +
                '<td class="text-end">' + (e.debit ? ('₹ ' + e.debit) : '') + '</td>' +
                '<td class="text-end">₹ ' + (e.balance_after || '0') + '</td>' +
            '</tr>';
        });
        ledgerBody.innerHTML = html;
    }

    function pollWallet() {
        fetch(pollUrl, { credentials: 'same-origin' })
            .then(function(res) { return res.json(); })
            .then(renderWallet)
            .catch(function() {});
    }

    pollWallet();
    setInterval(pollWallet, 15000);
});
