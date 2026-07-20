document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('texto');
    const emailInput = document.getElementById('email');
    const charcount = document.getElementById('charcount');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const statusNote = document.getElementById('statusNote');
    const resultContent = document.getElementById('resultContent');

    // Contador de caracteres
    textarea.addEventListener('input', () => {
        charcount.textContent = textarea.value.length;
    });

    // Cargar métricas en los divs estáticos
    async function loadMetrics() {
        try {
            const response = await fetch('http://localhost:8000/metricas');
            if (!response.ok) throw new Error('Network error');
            const data = await response.json();
            
            if (data.error) return;

            document.getElementById('m_cat_acc').textContent = `${(data.cat_acc * 100).toFixed(2)}%`;
            document.getElementById('m_cat_prec').textContent = `${(data.cat_prec * 100).toFixed(2)}%`;
            document.getElementById('m_cat_rec').textContent = `${(data.cat_rec * 100).toFixed(2)}%`;
            document.getElementById('m_cat_f1').textContent = `${(data.cat_f1 * 100).toFixed(2)}%`;

            document.getElementById('m_sent_acc').textContent = `${(data.sent_acc * 100).toFixed(2)}%`;
            document.getElementById('m_sent_prec').textContent = `${(data.sent_prec * 100).toFixed(2)}%`;
            document.getElementById('m_sent_rec').textContent = `${(data.sent_rec * 100).toFixed(2)}%`;
            document.getElementById('m_sent_f1').textContent = `${(data.sent_f1 * 100).toFixed(2)}%`;

        } catch (error) {
            console.warn('No se pudieron cargar las métricas.');
        }
    }
    loadMetrics();

    // Análisis de texto
    analyzeBtn.addEventListener('click', async () => {
        const text = textarea.value.trim();
        const email = emailInput.value.trim() || 'anonimo@corp.net';
        
        if(text.length < 3){
            textarea.style.borderBottomColor = '#b8453d';
            setTimeout(()=> textarea.style.borderBottomColor = '', 900);
            return;
        }

        const originalBtnText = analyzeBtn.textContent;
        analyzeBtn.textContent = 'Procesando...';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/analizar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto: text })
            });

            if (!response.ok) throw new Error('Error de servidor');

            const data = await response.json();

            // Determinar clases visuales
            let confClass = 'neu';
            if (data.sentimiento === 'Negativo') confClass = 'neg';
            if (data.sentimiento === 'Positivo') confClass = 'pos';

            // Tiempo y Resumen
            const time = new Date().toLocaleTimeString('es-EC', {hour:'2-digit', minute:'2-digit'});
            const summary = text.length > 46 ? text.slice(0,46) + '…' : text;

            // Procesar entidades
            let entitiesHtml = '<span class="mono-cell" style="font-style:italic">Ninguna</span>';
            if (data.entidades && data.entidades.length > 0) {
                entitiesHtml = data.entidades.map(ent => 
                    `<span class="tag-chip" style="margin-bottom:2px">${ent.texto}</span>`
                ).join(' ');
            }

            // Quitar mensaje de fila vacía
            const emptyRow = document.getElementById('emptyRow');
            if(emptyRow) emptyRow.remove();

            // Crear fila y agregar a tabla
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="mono-cell">${time}</td>
                <td class="mono-cell">${email}</td>
                <td title="${text}">${summary}</td>
                <td class="mono-cell">${data.categoria}</td>
                <td><span class="tag-chip ${confClass}">${data.sentimiento}</span></td>
                <td class="mono-cell">${entitiesHtml}</td>
            `;
            
            document.getElementById('ledgerBody').prepend(row);
            
            // Llenar panel de desglose (notebook)
            let entidadesList = '';
            if (data.entidades && data.entidades.length > 0) {
                entidadesList = '<ul style="margin-top:4px; padding-left:16px;">';
                data.entidades.forEach(ent => {
                    entidadesList += `<li><b>${ent.texto}</b> <span style="color:var(--text-l-muted); font-size:0.85em;">[${ent.etiqueta}]</span></li>`;
                });
                entidadesList += '</ul>';
            } else {
                entidadesList = '<span style="color:var(--text-l-muted); font-style:italic;"> No se detectaron entidades específicas.</span>';
            }

            resultContent.innerHTML = `
                <p style="margin-bottom: 12px; font-family: var(--serif); font-size: 1.1rem; line-height: 1.4;">
                    «${text}»
                </p>
                <div style="font-size: 0.92rem; color: var(--text-l); display: flex; flex-direction: column; gap: 12px;">
                    <div>
                        <span style="font-family: var(--mono); color: var(--amber); text-transform: uppercase; font-size: 0.75rem;">Categoría</span><br>
                        ${data.categoria}
                    </div>
                    <div>
                        <span style="font-family: var(--mono); color: var(--amber); text-transform: uppercase; font-size: 0.75rem;">Sentimiento</span><br>
                        ${data.sentimiento} <span style="color:var(--text-l-muted); font-size: 0.85em;">(Confianza principal: ${data.confianza_sentimiento}%)</span>
                        <div style="margin-top: 6px; padding-left: 10px; border-left: 2px solid var(--rule-d);">
                            <span style="font-size: 0.85em; color: var(--text-l-muted);">
                                <b>Positivo:</b> ${data.desglose_sentimiento["Positivo"]}% &nbsp;·&nbsp; 
                                <b>Neutral:</b> ${data.desglose_sentimiento["Neutral"]}% &nbsp;·&nbsp; 
                                <b>Negativo:</b> ${data.desglose_sentimiento["Negativo"]}%
                            </span>
                        </div>
                    </div>
                    <div>
                        <span style="font-family: var(--mono); color: var(--amber); text-transform: uppercase; font-size: 0.75rem;">Entidades Detectadas</span><br>
                        ${entidadesList}
                    </div>
                </div>
            `;
            
            // Limpiar
            textarea.value = '';
            charcount.textContent = '0';
            
        } catch (error) {
            console.error('Error:', error);
            statusNote.textContent = 'Error: No se pudo conectar a la API FastAPI.';
            statusNote.style.color = '#b8453d';
        } finally {
            analyzeBtn.textContent = originalBtnText;
            analyzeBtn.disabled = false;
        }
    });
});
