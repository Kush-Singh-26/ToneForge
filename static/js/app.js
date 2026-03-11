const API_BASE = "";

document.addEventListener('DOMContentLoaded', () => {
    switchTab('formalize');
});

// --- Theme Management ---
function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (window.lucide) lucide.createIcons();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.add('hidden');
    });
    
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.remove('hidden');
    }

    // Toggle corresponding output container
    document.querySelectorAll('.task-output').forEach(el => el.classList.add('hidden'));
    const targetOutput = document.getElementById(`output-${tabId}`);
    if (targetOutput) {
        targetOutput.classList.remove('hidden');
        // Re-calculate heights for hidden-then-visible textareas
        setTimeout(() => {
            targetOutput.querySelectorAll('textarea[oninput="autoResize(this)"]').forEach(ta => autoResize(ta));
        }, 50);
    }

    document.querySelectorAll('.nav-link').forEach(el => {
        el.classList.remove('active');
    });
    const targetLink = document.getElementById(`tab-${tabId}`);
    if (targetLink) {
        targetLink.classList.add('active');
    }
}

// --- Loading State ---
function setLoading(type, isLoading) {
    const btn = document.getElementById(`btn-${type}`);
    const originalText = btn.dataset.originalText || btn.innerText;
    
    if (isLoading) {
        btn.disabled = true;
        btn.dataset.originalText = originalText;
        btn.innerHTML = `
            <div class="flex items-center justify-center gap-3">
                <div class="custom-spinner !w-5 !h-5 !border-2"></div>
                <span class="text-xs font-semibold tracking-widest uppercase opacity-80">Forging...</span>
            </div>
        `;
        btn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        btn.disabled = false;
        btn.innerText = originalText;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// --- Render Helpers ---

function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `<span class="text-[10px] font-bold text-accent-500 uppercase tracking-widest">Copied</span>`;
        setTimeout(() => {
            btn.innerHTML = originalHtml;
        }, 2000);
    });
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function renderEmailCard(emailObj, title) {
    const uniqueId = Math.random().toString(36).substr(2, 9);
    return `
        <div class="output-card animate-slide-up group border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm dark:shadow-none">
            <div class="px-6 py-4 bg-slate-50 dark:bg-zinc-900/50 flex justify-between items-center border-b border-slate-100 dark:border-zinc-800/50">
                <div class="flex items-center gap-2">
                    <i data-lucide="mail" class="w-3.5 h-3.5 text-accent-500"></i>
                    <span class="text-slate-900 dark:text-zinc-200 font-semibold text-[10px] uppercase tracking-widest">${title}</span>
                </div>
                <button onclick="copyToClipboard(document.getElementById('body-${uniqueId}').value, this)" class="text-slate-400 dark:text-zinc-500 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-100 dark:bg-zinc-800/50 hover:bg-slate-200 dark:hover:bg-zinc-800">
                    <i data-lucide="copy" class="w-3 h-3"></i>
                    <span class="text-[10px] font-bold uppercase tracking-tight">Copy Body</span>
                </button>
            </div>
            <div class="p-8">
                <div class="space-y-3 mb-8 pb-6 border-b border-slate-100 dark:border-zinc-800/30 text-[11px] font-medium text-slate-400 dark:text-zinc-500">
                    <div class="flex items-center gap-3">
                        <span class="w-16 flex-shrink-0 text-slate-300 dark:text-zinc-600 uppercase tracking-tighter">Subject</span> 
                        <span id="subject-${uniqueId}" class="text-slate-700 dark:text-zinc-200 font-semibold flex-1">${emailObj.subject}</span>
                        <button onclick="copyToClipboard(document.getElementById('subject-${uniqueId}').innerText, this)" class="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-accent-500">
                            <i data-lucide="copy" class="w-3 h-3"></i>
                        </button>
                    </div>
                    <div class="flex gap-3"><span class="w-16 flex-shrink-0 text-slate-300 dark:text-zinc-600 uppercase tracking-tighter">Sender</span> <span class="text-slate-500 dark:text-zinc-400">${emailObj.sender}</span></div>
                    <div class="flex gap-3"><span class="w-16 flex-shrink-0 text-slate-300 dark:text-zinc-600 uppercase tracking-tighter">Recipient</span> <span class="text-slate-500 dark:text-zinc-400">${emailObj.to}</span></div>
                    ${emailObj.cc ? `<div class="flex gap-3"><span class="w-16 flex-shrink-0 text-slate-300 dark:text-zinc-600 uppercase tracking-tighter">CC</span> <span class="text-slate-500 dark:text-zinc-400">${emailObj.cc}</span></div>` : ''}
                </div>
                <textarea id="body-${uniqueId}" oninput="autoResize(this)" class="output-body text-slate-600 dark:text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap font-normal" spellcheck="false">${emailObj.body}</textarea>
            </div>
        </div>
    `;
}

function renderNegotiation(data) {
    const isSuccess = data.agreement_reached;
    let html = `
        <div class="output-card p-8 animate-slide-up bg-white dark:bg-zinc-900/50 mb-10 border-slate-200 dark:border-accent-500/10 shadow-sm dark:shadow-none">
            <div class="flex items-center justify-between mb-8">
                <h3 class="text-xl font-semibold text-slate-900 dark:text-white tracking-tight">${data.topic}</h3>
                <span class="px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-widest border ${isSuccess ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' : 'bg-slate-100 dark:bg-zinc-800 border-slate-200 dark:border-zinc-700 text-slate-500 dark:text-zinc-400'}">
                    ${isSuccess ? 'Converged' : 'In Discussion'}
                </span>
            </div>
            
            <div class="p-6 bg-slate-50 dark:bg-zinc-950 rounded-2xl border border-slate-100 dark:border-zinc-800/50 relative overflow-hidden group">
                <div class="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                    <i data-lucide="brain-circuit" class="w-12 h-12 text-accent-500"></i>
                </div>
                <div class="text-[10px] font-bold text-accent-500 uppercase tracking-widest mb-3">Intelligence Summary</div>
                <p class="text-slate-600 dark:text-zinc-400 text-sm leading-relaxed relative z-10">${data.summary}</p>
            </div>
        </div>

        <div class="space-y-6 mb-12">
            <div class="flex items-center gap-4 px-2">
                <div class="h-px flex-1 bg-slate-200 dark:bg-zinc-900"></div>
                <span class="text-[10px] font-bold text-slate-300 dark:text-zinc-600 uppercase tracking-[0.3em]">Communication Sequence</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-zinc-900"></div>
            </div>
    `;

    data.email_thread.forEach((msg, idx) => {
        const isProposer = msg.role === 'proposer';
        const label = isProposer ? 'Internal Strategy' : 'Counterpart Response';
        const uniqueId = Math.random().toString(36).substr(2, 9);

        html += `
            <div class="animate-slide-up group" style="animation-delay: ${idx * 0.1}s">
                <div class="flex items-center justify-between mb-2 px-2">
                    <div class="flex items-center gap-3">
                        <div class="w-1.5 h-1.5 rounded-full ${isProposer ? 'bg-accent-500' : 'bg-slate-300 dark:bg-zinc-700'}"></div>
                        <span class="text-[9px] font-bold ${isProposer ? 'text-slate-900 dark:text-zinc-200' : 'text-slate-400 dark:text-zinc-500'} uppercase tracking-widest">${label}</span>
                    </div>
                    <button onclick="copyToClipboard(document.getElementById('body-${uniqueId}').value, this)" class="opacity-0 group-hover:opacity-100 transition-opacity text-[9px] font-bold text-accent-500 uppercase flex items-center gap-1">
                        <i data-lucide="copy" class="w-3 h-3"></i>
                        Copy
                    </button>
                </div>
                <div class="p-6 rounded-2xl border ${isProposer ? 'bg-white dark:bg-zinc-900 border-slate-200 dark:border-zinc-800 shadow-sm dark:shadow-none' : 'bg-slate-50 dark:bg-zinc-950 border-slate-100 dark:border-zinc-900/50'}">
                    <div class="flex items-center gap-2 text-[10px] font-semibold text-slate-400 dark:text-zinc-600 mb-4 pb-2 border-b border-slate-100 dark:border-zinc-800/50">
                        <span id="subject-${uniqueId}" class="flex-1">RE: ${msg.subject}</span>
                        <button onclick="copyToClipboard(document.getElementById('subject-${uniqueId}').innerText.replace('RE: ', ''), this)" class="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-accent-500">
                             <i data-lucide="copy" class="w-2.5 h-2.5"></i>
                        </button>
                    </div>
                    <textarea id="body-${uniqueId}" oninput="autoResize(this)" class="output-body text-slate-600 dark:text-zinc-400 text-sm leading-relaxed whitespace-pre-wrap font-normal" spellcheck="false">${msg.body}</textarea>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    return html;
}

function renderLegal(data) {
    const riskMap = {
        low: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400',
        medium: 'bg-amber-500/10 border-amber-500/20 text-amber-600 dark:text-amber-400',
        high: 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400'
    };

    let html = `
        <div class="output-card animate-slide-up bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 shadow-sm dark:shadow-none">
            <div class="px-8 py-5 bg-slate-50 dark:bg-zinc-900/50 border-b border-slate-100 dark:border-zinc-800/50 flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <i data-lucide="shield-check" class="w-4 h-4 text-accent-500"></i>
                    <h3 class="font-bold text-slate-900 dark:text-zinc-200 text-[11px] uppercase tracking-wider">Legal Intelligence Report</h3>
                </div>
                <span class="px-4 py-1.5 rounded-xl text-[10px] font-bold uppercase border ${riskMap[data.overall_risk]}">
                    ${data.overall_risk} Risk Profile
                </span>
            </div>
            
            <div class="p-8">
                <div class="mb-12">
                    <div class="text-[10px] font-bold text-slate-400 dark:text-zinc-600 uppercase tracking-widest mb-4">Executive Interpretation</div>
                    <p class="text-slate-600 dark:text-zinc-300 leading-relaxed text-sm p-6 bg-slate-50 dark:bg-zinc-950 rounded-2xl border border-slate-100 dark:border-zinc-800/50 italic font-light">
                        "${data.plain_summary}"
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-10 mb-12">
                    <div class="space-y-5">
                        <div class="flex items-center gap-2 border-b border-slate-100 dark:border-zinc-800 pb-2">
                            <i data-lucide="list-checks" class="w-3.5 h-3.5 text-slate-400 dark:text-zinc-500"></i>
                            <div class="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest">Key Obligations</div>
                        </div>
                        <ul class="space-y-4">
                            ${data.obligations.length ? data.obligations.map(o => `
                                <li class="flex gap-3 text-sm text-slate-600 dark:text-zinc-400">
                                    <div class="w-1 h-1 rounded-full bg-accent-500 mt-2 flex-shrink-0"></div>
                                    <span>${o}</span>
                                </li>
                            `).join('') : '<li class="text-slate-300 dark:text-zinc-600 italic text-sm">No obligations detected.</li>'}
                        </ul>
                    </div>
                    <div class="space-y-5">
                        <div class="flex items-center gap-2 border-b border-slate-100 dark:border-zinc-800 pb-2">
                            <i data-lucide="clock" class="w-3.5 h-3.5 text-slate-400 dark:text-zinc-500"></i>
                            <div class="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest">Temporal Bounds</div>
                        </div>
                        <ul class="space-y-4">
                            ${data.deadlines.length ? data.deadlines.map(d => `
                                <li class="flex gap-3 text-sm text-slate-600 dark:text-zinc-400">
                                    <div class="w-1 h-1 rounded-full bg-slate-300 dark:bg-zinc-700 mt-2 flex-shrink-0"></div>
                                    <span>${d}</span>
                                </li>
                            `).join('') : '<li class="text-slate-300 dark:text-zinc-600 italic text-sm">No deadlines detected.</li>'}
                        </ul>
                    </div>
                </div>

                <div class="mb-12">
                    <div class="text-[10px] font-bold text-slate-400 dark:text-zinc-600 uppercase tracking-widest mb-4">Identified Risk Markers</div>
                    <div class="flex flex-wrap gap-2">
                        ${data.risk_flags.length ? data.risk_flags.map(f => `
                            <span class="px-3 py-1.5 bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-slate-500 dark:text-zinc-400 text-[9px] font-bold uppercase rounded-lg">
                                ${f}
                            </span>
                        `).join('') : '<span class="text-slate-300 dark:text-zinc-600 text-xs italic">Clear path identified.</span>'}
                    </div>
                </div>

                <div class="space-y-4">
                    <div class="text-[10px] font-bold text-slate-400 dark:text-zinc-600 uppercase tracking-widest mb-6">Structured Clause Deconstruction</div>
                    ${data.clauses.map(c => `
                        <div class="p-5 bg-slate-50 dark:bg-zinc-950/50 rounded-2xl border border-slate-100 dark:border-zinc-900 hover:border-slate-200 dark:hover:border-zinc-800 transition-all group shadow-sm dark:shadow-none">
                            <div class="flex justify-between items-start mb-3">
                                <span class="text-accent-500 text-[10px] font-bold uppercase tracking-widest">${c.clause_type}</span>
                                <span class="text-[8px] px-2 py-1 rounded-lg border ${riskMap[c.risk_level]} font-bold uppercase tracking-tighter">
                                    ${c.risk_level}
                                </span>
                            </div>
                            <p class="text-slate-400 dark:text-zinc-500 text-[11px] leading-relaxed group-hover:text-slate-600 dark:group-hover:text-zinc-300 transition-colors font-mono tracking-tight">${c.text}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    return html;
}

// --- API Execution ---

async function submitForm(type) {
    let endpoint = "";
    let payload = {};
    
    const outputArea = document.getElementById('output-' + type);
    outputArea.innerHTML = `
        <div class="h-full flex flex-col items-center justify-center space-y-8 py-32 animate-fade-in">
            <div class="custom-spinner !w-12 !h-12"></div>
            <div class="text-[10px] font-bold text-accent-500 tracking-[0.4em] uppercase opacity-80">Synthesizing Logic...</div>
        </div>
    `;

    try {
        if (type === 'formalize') {
            endpoint = "/formalize_email";
            payload = {
                raw_email: document.getElementById('form-raw').value,
                category: document.getElementById('form-cat').value,
                language: document.getElementById('form-lang').value || "English"
            };
            if (!payload.raw_email) throw new Error("A prompt is required to forge.");
        } 
        else if (type === 'reply') {
            endpoint = "/generate_reply";
            payload = {
                original_email: document.getElementById('reply-raw').value,
                category: document.getElementById('reply-cat').value
            };
            if (!payload.original_email) throw new Error("Input context is missing.");
        }
        else if (type === 'negotiate') {
            endpoint = "/negotiate_email";
            payload = {
                topic: document.getElementById('neg-topic').value,
                our_position: document.getElementById('neg-our').value,
                their_position: document.getElementById('neg-their').value,
                category: document.getElementById('neg-cat').value,
                max_rounds: parseInt(document.getElementById('neg-rounds').value) || 3
            };
            if (!payload.topic || !payload.our_position) throw new Error("Define the strategic context first.");
        }
        else if (type === 'legal') {
            endpoint = "/parse_legal_email";
            payload = {
                raw_email: document.getElementById('legal-raw').value
            };
            if (!payload.raw_email) throw new Error("Legal artifacts required.");
        }

        setLoading(type, true);

        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Network error ${response.status}`);
        }

        const data = await response.json();
        
        // Render Output
        if (type === 'formalize') {
            let html = renderEmailCard(data.email, `Formalized (${data.category})`);
            if (data.translated_email) {
                html += renderEmailCard(data.translated_email, `Translated (${data.translated_email.language})`);
            }
            outputArea.innerHTML = html;
        } 
        else if (type === 'reply') {
            outputArea.innerHTML = renderEmailCard(data.smart_reply, `Contextual Synthesis`);
        } 
        else if (type === 'negotiate') {
            outputArea.innerHTML = renderNegotiation(data);
        } 
        else if (type === 'legal') {
            outputArea.innerHTML = renderLegal(data);
        }
        
        // Re-initialize icons and auto-resize textareas
        if (window.lucide) {
            lucide.createIcons();
        }
        document.querySelectorAll('textarea[oninput="autoResize(this)"]').forEach(ta => autoResize(ta));

    } catch (error) {
        outputArea.innerHTML = `
            <div class="p-8 rounded-[2rem] bg-rose-500/5 border border-rose-500/10 text-rose-400/80 animate-slide-up text-center">
                <i data-lucide="alert-circle" class="w-10 h-10 mx-auto mb-6 text-rose-500"></i>
                <h4 class="text-xs font-bold uppercase tracking-[0.2em] mb-4 text-rose-500">Synthesis Interrupted</h4>
                <p class="text-sm font-light leading-relaxed mb-8">${error.message}</p>
                <div class="text-[10px] uppercase tracking-widest py-3 px-6 bg-rose-500/5 rounded-xl border border-rose-500/10 inline-block">
                    Verify connection & re-forge
                </div>
            </div>
        `;
        if (window.lucide) lucide.createIcons();
    } finally {
        setLoading(type, false);
    }
}
